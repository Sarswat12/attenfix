from app import db
from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    ATTENDANCE = 'attendance'
    ALERT = 'alert'
    REMINDER = 'reminder'
    REPORT = 'report'
    SYSTEM = 'system'

class NotificationPriority(Enum):
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False, index=True)
    notification_type = db.Column(db.Enum(NotificationType), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_url = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notification_type': self.notification_type.value,
            'title': self.title,
            'message': self.message,
            'action_url': self.action_url,
            'is_read': self.is_read,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat()
        }

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
