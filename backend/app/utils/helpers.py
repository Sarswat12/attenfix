import uuid
import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
from config import Config

def generate_user_id(role_prefix: str = 'EMP') -> str:
    """Generate a unique user ID with role prefix"""
    return f"{role_prefix}{str(uuid.uuid4().int)[-6:]}"

def generate_face_encoding_id(user_id: str) -> str:
    """Generate a unique face encoding ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"FACE_ENC_{user_id}_{timestamp}"

def allowed_file(filename: str, allowed_extensions: list = None) -> bool:
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, subfolder: str = 'uploads') -> str:
    """Save uploaded file and return path"""
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid file type")

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    upload_dir = os.path.join(Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, unique_filename)
    file.save(filepath)

    return filepath

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def format_datetime(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_date(d: date) -> str:
    """Format date to readable string"""
    return d.strftime('%Y-%m-%d')

def parse_date(date_str: str) -> date:
    """Parse date string to date object"""
    return datetime.fromisoformat(date_str).date()

def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def clean_filename(filename: str) -> str:
    """Clean filename for safe storage"""
    return secure_filename(filename)

def generate_random_string(length: int = 8) -> str:
    """Generate random string"""
    return uuid.uuid4().hex[:length]

def is_valid_uuid(uuid_str: str) -> bool:
    """Check if string is valid UUID"""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False
