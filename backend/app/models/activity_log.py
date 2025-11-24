from app import db
from datetime import datetime
from enum import Enum

class LogStatus(Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    WARNING = 'warning'

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    action_description = db.Column(db.Text, nullable=False)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.String(50))
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    status = db.Column(db.Enum(LogStatus), default=LogStatus.SUCCESS, index=True)
    error_message = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'action_description': self.action_description,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat()
        }
