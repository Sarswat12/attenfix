from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from app import db
from app.models.user import User, UserRole
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.department import Department
from app.utils.decorators import admin_required
from sqlalchemy import func, and_, case

statistics_bp = Blueprint('statistics', __name__, url_prefix='/api/statistics')

@statistics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        today = date.today()

        if current_user.role == UserRole.ADMIN:
            # Admin dashboard
            total_users = User.query.filter_by(status='Active').count()
            total_departments = Department.query.filter_by(status='Active').count()

            # Today's attendance
            today_present = AttendanceRecord.query.filter(
                and_(AttendanceRecord.date_only == today, AttendanceRecord.status == 'Present')
            ).count()

            today_absent = total_users - today_present

            # This week's attendance trend
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)

            weekly_stats = db.session.query(
                AttendanceRecord.date_only,
                func.count(case((AttendanceRecord.status == 'Present', 1))).label('present')
            ).filter(
                AttendanceRecord.date_only.between(week_start, week_end)
            ).group_by(AttendanceRecord.date_only).all()

            weekly_trend = {str(stat.date_only): stat.present for stat in weekly_stats}

            return jsonify({
                'total_users': total_users,
                'total_departments': total_departments,
                'today_present': today_present,
                'today_absent': today_absent,
                'weekly_trend': weekly_trend
            }), 200

        else:
            # Employee dashboard
            # Personal attendance stats
            total_days = AttendanceRecord.query.filter_by(user_id=user_id).count()
            present_days = AttendanceRecord.query.filter(
                and_(AttendanceRecord.user_id == user_id, AttendanceRecord.status == 'Present')
            ).count()

            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0

            # Today's status
            today_record = AttendanceRecord.query.filter(
                and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == today)
            ).first()

            return jsonify({
                'total_days': total_days,
                'present_days': present_days,
                'attendance_rate': round(attendance_rate, 2),
                'today_status': today_record.status.value if today_record else None,
                'today_time': today_record.time_only.isoformat() if today_record and today_record.time_only else None
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/attendance/rate', methods=['GET'])
@jwt_required()
def get_attendance_rate():
    """Get attendance rate statistics"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Access denied'}), 403

        period = request.args.get('period', 'month')  # month, quarter, year
        department = request.args.get('department')

        # Calculate date range
        today = date.today()
        if period == 'month':
            start_date = today.replace(day=1)
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            start_date = date(today.year, (quarter - 1) * 3 + 1, 1)
        elif period == 'year':
            start_date = date(today.year, 1, 1)
        else:
            start_date = today.replace(day=1)

        # Get attendance rates by user
        query = db.session.query(
            User.id,
            User.name,
            User.department,
            func.count(AttendanceRecord.id).label('total_days'),
            func.sum(case((AttendanceRecord.status == 'Present', 1), else_=0)).label('present_days')
        ).outerjoin(AttendanceRecord, and_(
            AttendanceRecord.user_id == User.id,
            AttendanceRecord.date_only.between(start_date, today)
        )).filter(User.status == 'Active')

        if department:
            query = query.filter(User.department == department)

        results = query.group_by(User.id, User.name, User.department).all()

        stats = []
        for result in results:
            attendance_rate = (result.present_days / result.total_days * 100) if result.total_days > 0 else 0
            stats.append({
                'user_id': result.id,
                'name': result.name,
                'department': result.department,
                'total_days': result.total_days,
                'present_days': result.present_days,
                'attendance_rate': round(attendance_rate, 2)
            })

        return jsonify({
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': today.isoformat(),
            'statistics': stats
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/attendance/trends', methods=['GET'])
@jwt_required()
def get_attendance_trends():
    """Get attendance trends over time"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Access denied'}), 403

        days = int(request.args.get('days', 30))
        department = request.args.get('department')

        start_date = date.today() - timedelta(days=days)

        query = db.session.query(
            AttendanceRecord.date_only,
            func.count(case((AttendanceRecord.status == 'Present', 1))).label('present'),
            func.count(case((AttendanceRecord.status == 'Absent', 1))).label('absent'),
            func.count(case((AttendanceRecord.status == 'Late', 1))).label('late')
        ).filter(AttendanceRecord.date_only.between(start_date, date.today()))

        if department:
            query = query.join(User).filter(User.department == department)

        results = query.group_by(AttendanceRecord.date_only).order_by(AttendanceRecord.date_only).all()

        trends = []
        for result in results:
            trends.append({
                'date': result.date_only.isoformat(),
                'present': result.present,
                'absent': result.absent,
                'late': result.late
            })

        return jsonify({
            'trends': trends,
            'period_days': days
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_department_stats():
    """Get statistics by department"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Access denied'}), 403

        today = date.today()

        # Get department-wise statistics
        stats = db.session.query(
            Department.id,
            Department.name,
            func.count(User.id).label('total_employees'),
            func.sum(case((AttendanceRecord.status == 'Present', 1), else_=0)).label('present_today'),
            func.sum(case((AttendanceRecord.status == 'Absent', 1), else_=0)).label('absent_today')
        ).outerjoin(User, and_(User.department == Department.id, User.status == 'Active')
        ).outerjoin(AttendanceRecord, and_(
            AttendanceRecord.user_id == User.id,
            AttendanceRecord.date_only == today
        )).filter(Department.status == 'Active'
        ).group_by(Department.id, Department.name).all()

        department_stats = []
        for stat in stats:
            attendance_rate = (stat.present_today / stat.total_employees * 100) if stat.total_employees > 0 else 0
            department_stats.append({
                'department_id': stat.id,
                'department_name': stat.name,
                'total_employees': stat.total_employees,
                'present_today': stat.present_today or 0,
                'absent_today': stat.absent_today or 0,
                'attendance_rate': round(attendance_rate, 2)
            })

        return jsonify({'department_stats': department_stats}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistics_bp.route('/user/<user_id>/summary', methods=['GET'])
@jwt_required()
def get_user_attendance_summary(user_id):
    """Get attendance summary for a specific user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only view their own summary unless they're admin
        if current_user.role != UserRole.ADMIN and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        period = request.args.get('period', 'month')  # month, quarter, year

        # Calculate date range
        today = date.today()
        if period == 'month':
            start_date = today.replace(day=1)
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            start_date = date(today.year, (quarter - 1) * 3 + 1, 1)
        elif period == 'year':
            start_date = date(today.year, 1, 1)
        else:
            start_date = today.replace(day=1)

        # Get user's attendance statistics
        stats = db.session.query(
            func.count(AttendanceRecord.id).label('total_days'),
            func.sum(case((AttendanceRecord.status == 'Present', 1), else_=0)).label('present_days'),
            func.sum(case((AttendanceRecord.status == 'Absent', 1), else_=0)).label('absent_days'),
            func.sum(case((AttendanceRecord.status == 'Late', 1), else_=0)).label('late_days')
        ).filter(
            and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only.between(start_date, today))
        ).first()

        attendance_rate = (stats.present_days / stats.total_days * 100) if stats.total_days > 0 else 0

        return jsonify({
            'user_id': user_id,
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': today.isoformat(),
            'total_days': stats.total_days,
            'present_days': stats.present_days,
            'absent_days': stats.absent_days,
            'late_days': stats.late_days,
            'attendance_rate': round(attendance_rate, 2)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
