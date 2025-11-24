from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from app import db
from app.models.attendance import AttendanceRecord, AttendanceStatus, AttendanceSource
from app.models.user import User, UserRole
from app.services.attendance_service import AttendanceService
from app.utils.decorators import admin_required
from sqlalchemy import and_, func

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')
attendance_service = AttendanceService()

@attendance_bp.route('/mark', methods=['POST'])
@jwt_required()
def mark_attendance():
    """Mark attendance for current user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        # Check if already marked today
        today = date.today()
        existing = AttendanceRecord.query.filter(
            and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == today)
        ).first()

        if existing:
            return jsonify({
                'message': 'Attendance already marked for today',
                'record': existing.to_dict()
            }), 409

        # Determine status based on time
        current_time = datetime.now().time()
        # Assume 9 AM is the cutoff for late
        late_cutoff = datetime.strptime('09:00:00', '%H:%M:%S').time()

        status = AttendanceStatus.PRESENT
        if current_time > late_cutoff:
            status = AttendanceStatus.LATE

        # Mark attendance
        result, status_code = attendance_service.mark_attendance(
            user_id=user_id,
            status=status,
            location=data.get('location', 'Main Gate'),
            source=AttendanceSource.API
        )

        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_attendance(user_id):
    """Get attendance records for a specific user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only view their own attendance unless they're admin
        if current_user.role != UserRole.ADMIN and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            start_date = datetime.fromisoformat(start_date).date()
        if end_date:
            end_date = datetime.fromisoformat(end_date).date()

        records = attendance_service.get_user_attendance(user_id, start_date, end_date)

        return jsonify({'records': records}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_attendance():
    """Get today's attendance summary"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role != UserRole.ADMIN:
            # Regular users see their own attendance
            today = date.today()
            record = AttendanceRecord.query.filter(
                and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == today)
            ).first()

            return jsonify({
                'record': record.to_dict() if record else None
            }), 200

        # Admin sees summary for all users
        summary = attendance_service.get_today_summary()
        return jsonify({'summary': summary}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/report', methods=['GET'])
@jwt_required()
def get_attendance_report():
    """Generate attendance report"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Access denied'}), 403

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')

        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date required'}), 400

        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()

        # Get attendance records with filters
        query = AttendanceRecord.query.filter(
            AttendanceRecord.date_only.between(start_date, end_date)
        )

        if department:
            query = query.join(User).filter(User.department == department)

        records = query.all()

        # Group by user and calculate statistics
        report_data = {}
        for record in records:
            uid = record.user_id
            if uid not in report_data:
                user = User.query.get(uid)
                report_data[uid] = {
                    'user_id': uid,
                    'name': user.name,
                    'department': user.department,
                    'total_days': 0,
                    'present_days': 0,
                    'absent_days': 0,
                    'late_days': 0
                }

            report_data[uid]['total_days'] += 1
            if record.status == AttendanceStatus.PRESENT:
                report_data[uid]['present_days'] += 1
            elif record.status == AttendanceStatus.ABSENT:
                report_data[uid]['absent_days'] += 1
            elif record.status == AttendanceStatus.LATE:
                report_data[uid]['late_days'] += 1

        # Calculate percentages
        for uid in report_data:
            total = report_data[uid]['total_days']
            if total > 0:
                report_data[uid]['attendance_percentage'] = round(
                    (report_data[uid]['present_days'] / total) * 100, 2
                )

        return jsonify({
            'report': list(report_data.values()),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/<record_id>', methods=['PUT'])
@admin_required
def update_attendance_record(record_id):
    """Update attendance record (admin only)"""
    try:
        record = AttendanceRecord.query.get(record_id)
        if not record:
            return jsonify({'error': 'Attendance record not found'}), 404

        data = request.get_json()
        if 'status' in data:
            record.status = data['status']
        if 'location' in data:
            record.location = data['location']

        db.session.commit()

        return jsonify({
            'message': 'Attendance record updated successfully',
            'record': record.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/bulk-mark', methods=['POST'])
@admin_required
def bulk_mark_attendance():
    """Bulk mark attendance for multiple users (admin only)"""
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        attendance_date = data.get('date', date.today().isoformat())
        status = data.get('status', AttendanceStatus.PRESENT.value)
        location = data.get('location', 'Office')

        attendance_date = datetime.fromisoformat(attendance_date).date()

        results = []
        for user_id in user_ids:
            # Check if already marked
            existing = AttendanceRecord.query.filter(
                and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == attendance_date)
            ).first()

            if existing:
                results.append({
                    'user_id': user_id,
                    'status': 'already_marked',
                    'record': existing.to_dict()
                })
                continue

            # Mark attendance
            result, _ = attendance_service.mark_attendance(
                user_id=user_id,
                status=status,
                location=location,
                source=AttendanceSource.MANUAL
            )

            results.append({
                'user_id': user_id,
                'status': 'marked' if result.get('success') else 'failed',
                'record_id': result.get('record_id')
            })

        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
