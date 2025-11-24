from app import db
from datetime import datetime
from enum import Enum

class AttendanceStatus(Enum):
    PRESENT = 'Present'
    ABSENT = 'Absent'
    LATE = 'Late'
    LEAVE = 'Leave'

class AttendanceSource(Enum):
    FACE_RECOGNITION = 'face_recognition'
    MANUAL = 'manual'
    API = 'api'

class VerificationStatus(Enum):
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'), nullable=False, index=True)
    face_encoding_id = db.Column(db.String(50), db.ForeignKey('face_encodings.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    date_only = db.Column(db.Date, nullable=False, index=True)
    time_only = db.Column(db.Time)
    status = db.Column(db.Enum(AttendanceStatus), nullable=False, index=True)
    recognition_confidence = db.Column(db.Float)
    recognition_distance = db.Column(db.Float)
    location = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
    source = db.Column(db.Enum(AttendanceSource), default=AttendanceSource.FACE_RECOGNITION, index=True)
    verification_status = db.Column(db.Enum(VerificationStatus), default=VerificationStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date_only', name='uq_attendance_user_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date_only.isoformat(),
            'time': self.time_only.isoformat() if self.time_only else None,
            'status': self.status.value,
            'confidence': self.recognition_confidence,
            'location': self.location,
            'source': self.source.value
        }
