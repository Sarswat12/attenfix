from app import db
from datetime import datetime
from enum import Enum

class FaceEncodingStatus(Enum):
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'

class FaceEncoding(db.Model):
    __tablename__ = 'face_encodings'

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False, index=True)
    encoding_vector = db.Column(db.LargeBinary, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    image_hash = db.Column(db.String(64), index=True)
    captured_at = db.Column(db.DateTime, nullable=False)
    quality_score = db.Column(db.Float)
    face_confidence = db.Column(db.Float)
    status = db.Column(db.Enum(FaceEncodingStatus), default=FaceEncodingStatus.PENDING, index=True)
    verification_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='face_encoding', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'captured_at': self.captured_at.isoformat(),
            'quality_score': self.quality_score,
            'face_confidence': self.face_confidence,
            'status': self.status.value
        }
