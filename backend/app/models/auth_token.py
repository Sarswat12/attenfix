from app import db
from datetime import datetime

class AuthToken(db.Model):
    __tablename__ = 'auth_tokens'

    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    device_id = db.Column(db.String(100))
    device_name = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    issued_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    last_used_at = db.Column(db.DateTime)
    is_revoked = db.Column(db.Boolean, default=False, index=True)
    revoked_at = db.Column(db.DateTime)
    revocation_reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'issued_at': self.issued_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_revoked': self.is_revoked
        }
