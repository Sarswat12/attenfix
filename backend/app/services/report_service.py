import pandas as pd
from datetime import datetime, date
from app import db
from app.models.attendance import AttendanceRecord
from app.models.user import User
from app.models.department import Department
import os
from config import Config

class ReportService:
    """Service for generating various reports"""

    def generate_attendance_report(self, start_date: date, end_date: date,
                                  department: str = None, user_id: str = None) -> pd.DataFrame:
        """Generate attendance report as DataFrame"""

        query = db.session.query(
            AttendanceRecord,
            User.name.label('user_name'),
            User.email.label('user_email'),
            User.department.label('department'),
            Department.name.label('department_name')
        ).join(User, AttendanceRecord.user_id == User.id
        ).outerjoin(Department, User.department == Department.id
        ).filter(AttendanceRecord.date_only.between(start_date, end_date))

        if department:
            query = query.filter(User.department == department)
        if user_id:
            query = query.filter(AttendanceRecord.user_id == user_id)

        results = query.order_by(AttendanceRecord.date_only, User.name).all()

        # Convert to DataFrame
        data = []
        for record, user_name, user_email, dept_id, dept_name in results:
            data.append({
                'Date': record.date_only,
                'User ID': record.user_id,
                'Name': user_name,
                'Email': user_email,
                'Department': dept_name or dept_id,
                'Time': record.time_only,
                'Status': record.status.value,
                'Location': record.location,
                'Source': record.source.value
            })

        return pd.DataFrame(data)

    def generate_user_report(self, department: str = None, status: str = None) -> pd.DataFrame:
        """Generate user report"""

        query = User.query

        if department:
            query = query.filter_by(department=department)
        if status:
            query = query.filter_by(status=status)

        users = query.all()

        data = []
        for user in users:
            data.append({
                'User ID': user.id,
                'Name': user.name,
                'Email': user.email,
                'Role': user.role.value,
                'Department': user.department,
                'Status': user.status.value,
                'Join Date': user.join_date,
                'Phone': user.phone,
                'Address': user.address
            })

        return pd.DataFrame(data)

    def generate_department_report(self) -> pd.DataFrame:
        """Generate department-wise attendance summary"""

        today = date.today()

        results = db.session.query(
            Department.name,
            db.func.count(User.id).label('total_employees'),
            db.func.sum(
                db.case(
                    (AttendanceRecord.status == 'Present', 1),
                    else_=0
                )
            ).label('present_today')
        ).outerjoin(User, db.and_(User.department == Department.id, User.status == 'Active')
        ).outerjoin(AttendanceRecord, db.and_(
            AttendanceRecord.user_id == User.id,
            AttendanceRecord.date_only == today
        )).filter(Department.status == 'Active'
        ).group_by(Department.id, Department.name).all()

        data = []
        for dept_name, total, present in results:
            absent = total - (present or 0)
            rate = (present / total * 100) if total > 0 else 0

            data.append({
                'Department': dept_name,
                'Total Employees': total or 0,
                'Present Today': present or 0,
                'Absent Today': absent,
                'Attendance Rate (%)': round(rate, 2)
            })

        return pd.DataFrame(data)

    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to CSV file"""
        filepath = os.path.join(Config.UPLOAD_FOLDER, 'reports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        df.to_csv(filepath, index=False)
        return filepath

    def export_to_excel(self, df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to Excel file"""
        filepath = os.path.join(Config.UPLOAD_FOLDER, 'reports', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        df.to_excel(filepath, index=False, engine='openpyxl')
        return filepath

    def generate_report(self, report_type: str, start_date: str = None,
                       end_date: str = None, filters: dict = None) -> dict:
        """
        Generate report based on type

        Args:
            report_type: Type of report ('attendance', 'users', 'departments')
            start_date: Start date for attendance reports
            end_date: End date for attendance reports
            filters: Additional filters

        Returns:
            Dict with report data and download URL
        """
        filters = filters or {}

        if report_type == 'attendance':
            if not start_date or not end_date:
                raise ValueError("Start date and end date required for attendance reports")

            start = datetime.fromisoformat(start_date).date()
            end = datetime.fromisoformat(end_date).date()

            df = self.generate_attendance_report(
                start, end,
                department=filters.get('department'),
                user_id=filters.get('user_id')
            )

        elif report_type == 'users':
            df = self.generate_user_report(
                department=filters.get('department'),
                status=filters.get('status')
            )

        elif report_type == 'departments':
            df = self.generate_department_report()

        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{report_type}_report_{timestamp}"

        # Export format
        export_format = filters.get('format', 'csv')

        if export_format == 'csv':
            filepath = self.export_to_csv(df, f"{filename}.csv")
            download_url = f"/downloads/reports/{filename}.csv"
        elif export_format == 'excel':
            filepath = self.export_to_excel(df, f"{filename}.xlsx")
            download_url = f"/downloads/reports/{filename}.xlsx"
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        return {
            'report_id': f"{report_type}_{timestamp}",
            'filename': filename,
            'format': export_format,
            'download_url': download_url,
            'filepath': filepath,
            'record_count': len(df)
        }
