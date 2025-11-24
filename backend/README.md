# Face Recognition Attendance System - Backend

A comprehensive Flask-based backend API for a face recognition attendance system with JWT authentication, SQLAlchemy ORM, and computer vision capabilities.

## Features

- **User Management**: Complete user lifecycle management with role-based access control
- **Face Recognition**: Advanced face detection and recognition using face_recognition library
- **Attendance Tracking**: Automated attendance marking with manual override capabilities
- **Real-time Statistics**: Dashboard analytics and reporting
- **Admin Panel**: Administrative functions for system management
- **RESTful API**: Well-documented REST API endpoints
- **Security**: JWT authentication, password hashing, input validation

## Technology Stack

- **Framework**: Flask 2.3+
- **Database**: MySQL 8.0+ with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **Face Recognition**: face_recognition, OpenCV, NumPy
- **Validation**: Marshmallow, email-validator
- **Deployment**: Gunicorn, Docker-ready

## Quick Start

1. **Clone and Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Database Setup**:
   ```bash
   # Ensure MySQL is running and database is created
   python run.py  # This will create tables automatically
   ```

4. **Run Development Server**:
   ```bash
   python run.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/verify-token` - Token verification

### Users
- `GET /api/users` - List users (admin) or get profile
- `GET /api/users/<user_id>` - Get specific user
- `POST /api/users` - Create user (admin)
- `PUT /api/users/<user_id>` - Update user
- `DELETE /api/users/<user_id>` - Delete user (admin)

### Attendance
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/user/<user_id>` - Get user attendance
- `GET /api/attendance/today` - Today's attendance summary
- `GET /api/attendance/report` - Generate attendance report

### Face Recognition
- `POST /api/face/enroll` - Enroll face
- `POST /api/face/recognize` - Recognize face and mark attendance
- `GET /api/face/user/<user_id>/encodings` - Get user face encodings
- `DELETE /api/face/encodings/<encoding_id>` - Delete face encoding

### Statistics
- `GET /api/statistics/dashboard` - Dashboard statistics
- `GET /api/statistics/attendance/rate` - Attendance rates
- `GET /api/statistics/attendance/trends` - Attendance trends
- `GET /api/statistics/departments` - Department statistics

### Admin
- `GET /api/admin/users` - Admin user management
- `PUT /api/admin/users/<user_id>/status` - Update user status
- `GET /api/admin/departments` - Department management
- `POST /api/admin/departments` - Create department
- `POST /api/admin/attendance/bulk` - Bulk attendance operations

### Health Check
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health check

## Database Schema

The system uses the following main tables:
- `users` - User accounts and profiles
- `face_encodings` - Face recognition data
- `attendance_records` - Attendance tracking
- `departments` - Department management
- `user_settings` - User preferences

## Configuration

Key configuration options in `.env`:

```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=face_attendance_db

# JWT
JWT_SECRET_KEY=your_jwt_secret

# Face Recognition
FACE_RECOGNITION_THRESHOLD=0.6
MIN_FACE_IMAGES_FOR_ENROLLMENT=5

# File Upload
UPLOAD_FOLDER=/storage
MAX_FILE_SIZE_MB=5
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Migration message"
flask db upgrade
```

## Deployment

### Production Setup
1. Set `FLASK_ENV=production` in environment
2. Use a production WSGI server like Gunicorn
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure database connection pooling

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens have expiration times
- Input validation on all endpoints
- CORS configuration for frontend integration
- File upload restrictions and validation
- SQL injection prevention through SQLAlchemy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
