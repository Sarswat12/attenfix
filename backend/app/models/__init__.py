from app import db

# Import all models
from .user import User
from .face_encoding import FaceEncoding
from .attendance import AttendanceRecord
from .settings import UserSettings
from .department import Department
from .activity_log import ActivityLog
from .auth_token import AuthToken
from .report import Report
from .system_config import SystemConfig
from .notification import Notification

__all__ = [
    'User',
    'FaceEncoding',
    'AttendanceRecord',
    'UserSettings',
    'Department',
    'ActivityLog',
    'AuthToken',
    'Report',
    'SystemConfig',
    'Notification'
]
