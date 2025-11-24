from app import db
from datetime import datetime
from enum import Enum

class ExportFormat(Enum):
    CSV = 'csv'
    PDF = 'pdf'
    EXCEL = 'excel'

class Language(Enum):
    EN = 'en'
    ES = 'es'
    FR = 'fr'
    DE = 'de'
    ZH = 'zh'

class Theme(Enum):
    LIGHT = 'light'
    DARK = 'dark'

class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), primary_key=True)
    camera_access_enabled = db.Column(db.Boolean, default=True)
    notifications_enabled = db.Column(db.Boolean, default=True)
    export_format = db.Column(db.Enum(ExportFormat), default=ExportFormat.CSV)
    lms_api_key = db.Column(db.String(255))
    hrm_api_key = db.Column(db.String(255))
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.Enum(Language), default=Language.EN)
    theme = db.Column(db.Enum(Theme), default=Theme.LIGHT)
    auto_logout_minutes = db.Column(db.Integer, default=30)
    enable_2fa = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'camera_access_enabled': self.camera_access_enabled,
            'notifications_enabled': self.notifications_enabled,
            'export_format': self.export_format.value,
            'timezone': self.timezone,
            'language': self.language.value,
            'theme': self.theme.value,
            'auto_logout_minutes': self.auto_logout_minutes,
            'enable_2fa': self.enable_2fa
        }
