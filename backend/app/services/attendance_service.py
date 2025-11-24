from app import db
from app.models.attendance import AttendanceRecord, AttendanceStatus, AttendanceSource
from app.models.user import User
from datetime import datetime, date, time
from typing import Dict, List, Optional

class AttendanceService:
    """Attendance management service"""

    def mark_attendance(self, user_id: str, status: str = 'Present',
                       face_encoding_id: str = None, location: str = None,
                       source: str = 'api') -> tuple:
        """
        Mark attendance for a user

        Args:
            user_id: User ID
            status: Attendance status
            face_encoding_id: Face encoding ID (for face recognition)
            location: Location where attendance was marked
            source: Source of attendance (api, face_recognition, manual)

        Returns:
            Tuple of (result_dict, status_code)
        """
        try:
            today = date.today()
            current_time = datetime.now().time()

            # Check if already marked today
            existing_record = AttendanceRecord.query.filter(
                db.and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == today)
            ).first()

            if existing_record:
                return {
                    'message': 'Attendance already marked for today',
                    'record': existing_record.to_dict()
                }, 409

            # Create attendance record
            record = AttendanceRecord(
                user_id=user_id,
                date_only=today,
                time_only=current_time,
                status=status,
                face_encoding_id=face_encoding_id,
                location=location or 'Office',
                source=source
            )

            db.session.add(record)
            db.session.commit()

            return {
                'message': 'Attendance marked successfully',
                'record': record.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def get_user_attendance(self, user_id: str, start_date: date = None,
                           end_date: date = None) -> List[Dict]:
        """
        Get attendance records for a user within date range

        Args:
            user_id: User ID
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            List of attendance records
        """
        query = AttendanceRecord.query.filter_by(user_id=user_id)

        if start_date:
            query = query.filter(AttendanceRecord.date_only >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.date_only <= end_date)

        records = query.order_by(AttendanceRecord.date_only.desc()).all()
        return [r.to_dict() for r in records]

    def get_today_summary(self) -> List[Dict]:
        """
        Get today's attendance summary by department

        Returns:
            List of department summaries
        """
        from app.models.department import Department

        today = date.today()

        # Get department-wise summary
        results = db.session.query(
            Department.id,
            Department.name,
            db.func.count(User.id).label('total_employees'),
            db.func.sum(
                db.case(
                    (AttendanceRecord.status == 'Present', 1),
                    else_=0
                )
            ).label('present_count')
        ).outerjoin(User, db.and_(User.department == Department.id, User.status == 'Active')
        ).outerjoin(AttendanceRecord, db.and_(
            AttendanceRecord.user_id == User.id,
            AttendanceRecord.date_only == today
        )).filter(Department.status == 'Active'
        ).group_by(Department.id, Department.name).all()

        summary = []
        for result in results:
            absent_count = (result.total_employees or 0) - (result.present_count or 0)
            attendance_rate = (result.present_count / result.total_employees * 100) if result.total_employees > 0 else 0

            summary.append({
                'department_id': result.id,
                'department_name': result.name,
                'total_employees': result.total_employees or 0,
                'present_today': result.present_count or 0,
                'absent_today': absent_count,
                'attendance_rate': round(attendance_rate, 2)
            })

        return summary

    def get_attendance_report(self, start_date: date, end_date: date,
                             department: str = None, user_id: str = None) -> List[Dict]:
        """
        Generate attendance report

        Args:
            start_date: Report start date
            end_date: Report end date
            department: Department filter (optional)
            user_id: User ID filter (optional)

        Returns:
            List of attendance records with user details
        """
        query = db.session.query(
            AttendanceRecord,
            User.name,
            User.email,
            User.department
        ).join(User, AttendanceRecord.user_id == User.id
        ).filter(AttendanceRecord.date_only.between(start_date, end_date))

        if department:
            query = query.filter(User.department == department)
        if user_id:
            query = query.filter(AttendanceRecord.user_id == user_id)

        results = query.order_by(AttendanceRecord.date_only.desc(), User.name).all()

        report = []
        for record, user_name, user_email, user_department in results:
            report.append({
                'record_id': record.id,
                'user_id': record.user_id,
                'user_name': user_name,
                'user_email': user_email,
                'department': user_department,
                'date': record.date_only.isoformat(),
                'time': record.time_only.isoformat() if record.time_only else None,
                'status': record.status.value,
                'location': record.location,
                'source': record.source.value
            })

        return report

    def update_attendance_record(self, record_id: int, status: str,
                                location: str = None) -> tuple:
        """
        Update an attendance record

        Args:
            record_id: Attendance record ID
            status: New status
            location: New location (optional)

        Returns:
            Tuple of (result_dict, status_code)
        """
        try:
            record = AttendanceRecord.query.get(record_id)
            if not record:
                return {'error': 'Attendance record not found'}, 404

            record.status = status
            if location:
                record.location = location

            db.session.commit()

            return {
                'message': 'Attendance record updated successfully',
                'record': record.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    def bulk_mark_attendance(self, user_ids: List[str], attendance_date: date,
                           status: str = 'Present', location: str = 'Office',
                           source: str = 'manual') -> Dict:
        """
        Bulk mark attendance for multiple users

        Args:
            user_ids: List of user IDs
            attendance_date: Date for attendance
            status: Attendance status
            location: Location
            source: Source

        Returns:
            Dict with results
        """
        results = {'successful': [], 'failed': [], 'already_marked': []}

        for user_id in user_ids:
            try:
                # Check if already marked
                existing = AttendanceRecord.query.filter(
                    db.and_(AttendanceRecord.user_id == user_id, AttendanceRecord.date_only == attendance_date)
                ).first()

                if existing:
                    results['already_marked'].append(user_id)
                    continue

                # Mark attendance
                record = AttendanceRecord(
                    user_id=user_id,
                    date_only=attendance_date,
                    status=status,
                    location=location,
                    source=source
                )

                db.session.add(record)
                results['successful'].append(user_id)

            except Exception as e:
                results['failed'].append({'user_id': user_id, 'error': str(e)})

        db.session.commit()
        return results
