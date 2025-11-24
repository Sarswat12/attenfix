from app import db
from datetime import datetime
from enum import Enum

class ReportStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

class ReportFormat(Enum):
    CSV = 'csv'
    PDF = 'pdf'
    EXCEL = 'excel'

class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False, index=True)
    report_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    filters = db.Column(db.JSON)
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_format = db.Column(db.Enum(ReportFormat), nullable=False)
    record_count = db.Column(db.Integer)
    status = db.Column(db.Enum(ReportStatus), default=ReportStatus.PENDING, index=True)
    error_message = db.Column(db.Text)
    generated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'title': self.title,
            'file_format': self.file_format.value,
            'status': self.status.value,
            'record_count': self.record_count,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat()
        }
