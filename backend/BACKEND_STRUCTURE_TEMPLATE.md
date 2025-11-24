# Backend Folder Structure & Setup Guide
## Complete Template for Flask/Python Backend Development

---

## Overview

This guide provides a complete backend folder structure template that matches the Fixed Schema Specification. Both frontend and backend teams should follow this structure exactly.

**Technology Stack**: Python 3.9+, Flask 2.3+, SQLAlchemy ORM  
**Database**: MySQL 8.0+ (face_attendance_db)  
**API Pattern**: RESTful with JWT authentication  

---

## Recommended Folder Structure

```
backend/
├── README.md                    # Backend documentation
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── run.py                      # Application entry point
├── config.py                   # Configuration management
│
├── app/
│   ├── __init__.py             # Flask app initialization
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py             # User model (maps to users table)
│   │   ├── face_encoding.py    # FaceEncoding model
│   │   ├── attendance.py       # AttendanceRecord model
│   │   ├── department.py       # Department model
│   │   └── ...
│   │
│   ├── routes/                 # API endpoints (grouped by function)
│   │   ├── __init__.py
│   │   ├── auth.py             # /api/auth/* endpoints
│   │   ├── users.py            # /api/users/* endpoints
│   │   ├── face.py             # /api/face/* endpoints
│   │   ├── attendance.py       # /api/attendance/* endpoints
│   │   ├── reports.py          # /api/reports/* endpoints
│   │   ├── admin.py            # /api/admin/* endpoints
│   │   └── health.py           # /api/health endpoint
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py     # User operations
│   │   ├── face_service.py     # Face recognition logic
│   │   ├── attendance_service.py # Attendance marking logic
│   │   ├── auth_service.py     # Authentication/JWT
│   │   ├── report_service.py   # Report generation
│   │   └── email_service.py    # Email notifications
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── decorators.py       # Custom decorators (auth, admin)
│   │   ├── validators.py       # Input validation
│   │   ├── helpers.py          # Helper functions
│   │   ├── errors.py           # Custom exceptions
│   │   └── constants.py        # Constants & enums
│   │
│   ├── middleware/             # Request/response middleware
│   │   ├── __init__.py
│   │   ├── jwt_middleware.py   # JWT token validation
│   │   ├── error_handler.py    # Global error handling
│   │   └── cors_middleware.py  # CORS configuration
│   │
│   └── static/                 # Static files
│       └── storage/            # File upload storage
│           ├── faces/          # Face images
│           ├── avatars/        # User avatars
│           └── reports/        # Generated reports
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── test_auth.py            # Auth endpoint tests
│   ├── test_users.py           # User endpoint tests
│   ├── test_face.py            # Face endpoint tests
│   ├── test_attendance.py      # Attendance tests
│   └── test_reports.py         # Report tests
│
├── migrations/                 # Database migrations (Alembic)
│   └── versions/
│
├── logs/                       # Application logs
│   └── app.log
│
└── docs/                       # Documentation
    ├── API_DOCUMENTATION.md    # Complete API docs
    ├── SETUP_INSTRUCTIONS.md   # Setup guide
    └── TROUBLESHOOTING.md      # Common issues
```

---

## Key Files Setup

### **1. requirements.txt**

```txt
# Web Framework
Flask==2.3.0
Flask-CORS==4.0.0
Flask-Migrate==4.0.0

# Database ORM
Flask-SQLAlchemy==3.0.3
SQLAlchemy==2.0.0
mysql-connector-python==8.0.33

# Authentication & Security
Flask-JWT-Extended==4.4.4
bcrypt==4.0.1
python-dotenv==1.0.0

# Face Recognition
numpy==1.24.0
opencv-python==4.7.0.72
face-recognition==1.3.5
Pillow==9.5.0

# Data Validation
marshmallow==3.18.0
email-validator==1.3.0

# Testing
pytest==7.3.1
pytest-cov==4.0.0
pytest-mock==3.10.0

# Logging & Monitoring
python-logging-loki==0.3.2

# Utilities
requests==2.31.0
python-dateutil==2.8.2
pytz==2023.3
pydantic==1.10.0

# Production
gunicorn==20.1.0
```

### **2. run.py (Entry Point)**

```python
import os
from app import create_app, db
from dotenv import load_dotenv

load_dotenv()

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {'db': db}

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', False)
    )
```

### **3. .env.example**

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=face_attendance_db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours in seconds

# Face Recognition Configuration
FACE_RECOGNITION_THRESHOLD=0.6
MIN_FACE_IMAGES_FOR_ENROLLMENT=5
MAX_FACE_IMAGES_FOR_ENROLLMENT=7

# Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Upload Configuration
MAX_FILE_SIZE_MB=5
UPLOAD_FOLDER=/storage
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### **4. config.py (Configuration)**

```python
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Face Recognition
    FACE_RECOGNITION_THRESHOLD = float(os.getenv('FACE_RECOGNITION_THRESHOLD', 0.6))
    MIN_FACE_IMAGES = int(os.getenv('MIN_FACE_IMAGES_FOR_ENROLLMENT', 5))
    MAX_FACE_IMAGES = int(os.getenv('MAX_FACE_IMAGES_FOR_ENROLLMENT', 7))
    
    # File Upload
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', 5)) * 1024 * 1024
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/storage')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

---

## Core Model Examples

### **User Model** (`app/models/user.py`)

```python
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
    department = db.Column(db.String(20), db.ForeignKey('departments.id'), index=True)
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
```

### **AttendanceRecord Model** (`app/models/attendance.py`)

```python
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
    
    # Relationships
    face_encoding = db.relationship('FaceEncoding', backref='attendance_records')
    
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
```

---

## Route Handler Example

### **Authentication Routes** (`app/routes/auth.py`)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.user import User, UserStatus
from app.models.settings import UserSettings
from app.utils.validators import validate_email, validate_password
from app.utils.errors import ValidationError, AuthenticationError
from app.services.auth_service import AuthService
import uuid

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not all(k in data for k in ('name', 'email', 'password', 'role')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        validate_email(data['email'])
        validate_password(data['password'])
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        user_id = f"{data['role'].upper()[:3]}{str(uuid.uuid4().int)[-3:]}"
        user = User(
            id=user_id,
            name=data['name'],
            email=data['email'],
            role=data['role'],
            status=UserStatus.ACTIVE,
            join_date=datetime.now().date()
        )
        user.set_password(data['password'])
        
        # Create user settings
        settings = UserSettings(user_id=user_id)
        
        db.session.add(user)
        db.session.add(settings)
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'token': access_token
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user.status == UserStatus.SUSPENDED:
            return jsonify({'error': 'Account suspended'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': access_token,
            'user_id': user.id,
            'name': user.name,
            'role': user.role.value
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout - revoke token"""
    try:
        user_id = get_jwt_identity()
        
        # Revoke token logic
        token = request.headers.get('Authorization').split()[1]
        auth_service.revoke_token(user_id, token, 'User logout')
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if token is valid"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.status == UserStatus.SUSPENDED:
            return jsonify({'valid': False}), 401
        
        return jsonify({
            'valid': True,
            'user_id': user_id,
            'name': user.name,
            'role': user.role.value
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 401
```

---

## Service Layer Example

### **Attendance Service** (`app/services/attendance_service.py`)

```python
from app import db
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.user import User
from datetime import datetime, date
from sqlalchemy import and_

class AttendanceService:
    
    @staticmethod
    def mark_attendance(user_id, status, face_encoding_id=None, location='Main Gate', source='face_recognition'):
        """Mark user attendance for today"""
        try:
            today = date.today()
            
            # Check if already marked today
            existing = AttendanceRecord.query.filter(
                and_(
                    AttendanceRecord.user_id == user_id,
                    AttendanceRecord.date_only == today
                )
            ).first()
            
            if existing:
                return {'success': False, 'message': 'Already marked for today'}, 409
            
            # Create new record
            record = AttendanceRecord(
                user_id=user_id,
                face_encoding_id=face_encoding_id,
                timestamp=datetime.utcnow(),
                date_only=today,
                time_only=datetime.now().time(),
                status=status,
                location=location,
                source=source
            )
            
            db.session.add(record)
            db.session.commit()
            
            return {'success': True, 'record_id': record.id}, 201
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500
    
    @staticmethod
    def get_user_attendance(user_id, start_date=None, end_date=None):
        """Get user's attendance records"""
        query = AttendanceRecord.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(AttendanceRecord.date_only >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.date_only <= end_date)
        
        records = query.order_by(AttendanceRecord.date_only.desc()).all()
        return [r.to_dict() for r in records]
    
    @staticmethod
    def get_today_summary():
        """Get today's attendance summary by department"""
        from app.models.department import Department
        
        today = date.today()
        
        departments = db.session.query(
            Department.id,
            Department.name,
            db.func.count(User.id).label('total'),
            db.func.sum(
                db.case(
                    (AttendanceRecord.status == 'Present', 1),
                    else_=0
                )
            ).label('present')
        ).outerjoin(User).outerjoin(AttendanceRecord).group_by(Department.id).all()
        
        return [
            {
                'department_id': d.id,
                'department_name': d.name,
                'total_employees': d.total or 0,
                'present': d.present or 0
            }
            for d in departments
        ]
```

---

## Backend Checklist

### **Setup Steps**

- [ ] Create Python virtual environment: `python -m venv venv`
- [ ] Activate venv: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Verify database connection
- [ ] Create folder structure as specified
- [ ] Implement all models
- [ ] Implement all routes
- [ ] Implement all services
- [ ] Add input validation
- [ ] Add error handling
- [ ] Add logging
- [ ] Write unit tests
- [ ] Test all endpoints with Postman/Insomnia
- [ ] Deploy to production

### **Development Commands**

```bash
# Start development server
python run.py

# Run tests
pytest tests/

# Generate coverage report
pytest --cov=app tests/

# Database migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## API Documentation Template

See `FIXED_SCHEMA_SPECIFICATION.md` for complete API endpoint mapping.

All 25+ endpoints are mapped to specific database operations and expected responses.

---

**This template is ready to use. Copy the structure and start implementing!**
