from app import db
from datetime import datetime
from enum import Enum
import bcrypt

class UserRole(Enum):
    ADMIN = 'admin'
    EMPLOYEE = 'employee'
    STUDENT = 'student'

class UserStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    SUSPENDED = 'Suspended'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, index=True)
    department = db.Column(db.String(50), db.ForeignKey('departments.id'), index=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    status = db.Column(db.Enum(UserStatus), default=UserStatus.ACTIVE, index=True)
    join_date = db.Column(db.Date, nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, index=True)

    # Relationships
    face_encodings = db.relationship('FaceEncoding', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    auth_tokens = db.relationship('AuthToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role.value,
            'department': self.department,
            'status': self.status.value,
            'join_date': self.join_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
