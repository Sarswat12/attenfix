from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserRole, UserStatus
from app.models.department import Department, DepartmentStatus
from app.models.face_encoding import FaceEncoding, FaceEncodingStatus
from app.models.attendance import AttendanceRecord
from app.utils.decorators import admin_required
from app.services.report_service import ReportService
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
report_service = ReportService()

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with filters"""
    try:
        role_filter = request.args.get('role')
        status_filter = request.args.get('status')
        department_filter = request.args.get('department')
        search = request.args.get('search')

        query = User.query

        if role_filter:
            query = query.filter_by(role=role_filter)
        if status_filter:
            query = query.filter_by(status=status_filter)
        if department_filter:
            query = query.filter_by(department=department_filter)
        if search:
            query = query.filter(
                db.or_(User.name.contains(search), User.email.contains(search))
            )

        users = query.all()

        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """Update user status (activate/deactivate/suspend)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['Active', 'Inactive', 'Suspended']:
            return jsonify({'error': 'Invalid status'}), 400

        user.status = new_status
        db.session.commit()

        return jsonify({
            'message': f'User status updated to {new_status}',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()
        return jsonify({
            'departments': [dept.to_dict() for dept in departments]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/departments', methods=['POST'])
@admin_required
def create_department():
    """Create new department"""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Department name required'}), 400

        # Check if department exists
        existing = Department.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Department already exists'}), 409

        department_id = f"DEPT_{uuid.uuid4().hex[:8].upper()}"
        department = Department(
            id=department_id,
            name=data['name'],
            description=data.get('description'),
            location=data.get('location')
        )

        db.session.add(department)
        db.session.commit()

        return jsonify({
            'message': 'Department created successfully',
            'department': department.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/face-encodings/pending', methods=['GET'])
@admin_required
def get_pending_face_encodings():
    """Get pending face encodings for verification"""
    try:
        encodings = FaceEncoding.query.filter_by(status=FaceEncodingStatus.PENDING).all()

        result = []
        for enc in encodings:
            user = User.query.get(enc.user_id)
            result.append({
                'encoding': enc.to_dict(),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            })

        return jsonify({'pending_encodings': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/face-encodings/<encoding_id>/verify', methods=['PUT'])
@admin_required
def verify_face_encoding(encoding_id):
    """Verify or reject face encoding"""
    try:
        encoding = FaceEncoding.query.get(encoding_id)
        if not encoding:
            return jsonify({'error': 'Face encoding not found'}), 404

        data = request.get_json()
        action = data.get('action')  # 'verify' or 'reject'
        notes = data.get('notes')

        if action == 'verify':
            encoding.status = FaceEncodingStatus.VERIFIED
        elif action == 'reject':
            encoding.status = FaceEncodingStatus.REJECTED
        else:
            return jsonify({'error': 'Invalid action'}), 400

        if notes:
            encoding.verification_notes = notes

        db.session.commit()

        return jsonify({
            'message': f'Face encoding {action}ed successfully',
            'encoding': encoding.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/attendance/bulk', methods=['POST'])
@admin_required
def bulk_attendance_operations():
    """Bulk attendance operations"""
    try:
        data = request.get_json()
        operation = data.get('operation')  # 'mark', 'update', 'delete'
        user_ids = data.get('user_ids', [])
        date_str = data.get('date')
        status = data.get('status')

        if not user_ids or not date_str:
            return jsonify({'error': 'User IDs and date required'}), 400

        from datetime import datetime
        target_date = datetime.fromisoformat(date_str).date()

        results = []

        if operation == 'mark':
            for user_id in user_ids:
                # Check if already marked
                existing = AttendanceRecord.query.filter(
                    db.and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == target_date)
                ).first()

                if existing:
                    results.append({
                        'user_id': user_id,
                        'status': 'already_marked'
                    })
                    continue

                # Mark attendance
                record = AttendanceRecord(
                    user_id=user_id,
                    date_only=target_date,
                    status=status or 'Present',
                    source='manual'
                )
                db.session.add(record)
                results.append({
                    'user_id': user_id,
                    'status': 'marked'
                })

        elif operation == 'update':
            for user_id in user_ids:
                record = AttendanceRecord.query.filter(
                    db.and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == target_date)
                ).first()

                if record:
                    record.status = status
                    results.append({
                        'user_id': user_id,
                        'status': 'updated'
                    })
                else:
                    results.append({
                        'user_id': user_id,
                        'status': 'not_found'
                    })

        elif operation == 'delete':
            for user_id in user_ids:
                record = AttendanceRecord.query.filter(
                    db.and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == target_date)
                ).first()

                if record:
                    db.session.delete(record)
                    results.append({
                        'user_id': user_id,
                        'status': 'deleted'
                    })
                else:
                    results.append({
                        'user_id': user_id,
                        'status': 'not_found'
                    })

        db.session.commit()

        return jsonify({'results': results}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports/generate', methods=['POST'])
@admin_required
def generate_report():
    """Generate custom report"""
    try:
        data = request.get_json()
        report_type = data.get('type')  # 'attendance', 'users', 'departments'
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        filters = data.get('filters', {})

        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date required'}), 400

        report_data = report_service.generate_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            filters=filters
        )

        return jsonify({
            'message': 'Report generated successfully',
            'report_id': report_data['report_id'],
            'download_url': report_data['download_url']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/system/stats', methods=['GET'])
@admin_required
def get_system_stats():
    """Get system-wide statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(status='Active').count()
        total_departments = Department.query.count()
        total_face_encodings = FaceEncoding.query.count()
        verified_face_encodings = FaceEncoding.query.filter_by(status='verified').count()
        total_attendance_records = AttendanceRecord.query.count()

        # Today's attendance
        from datetime import date
        today = date.today()
        today_attendance = AttendanceRecord.query.filter_by(date_only=today).count()

        return jsonify({
            'system_stats': {
                'total_users': total_users,
                'active_users': active_users,
                'total_departments': total_departments,
                'total_face_encodings': total_face_encodings,
                'verified_face_encodings': verified_face_encodings,
                'total_attendance_records': total_attendance_records,
                'today_attendance': today_attendance
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
