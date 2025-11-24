from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User, UserRole

def jwt_required_custom(fn):
    """Custom JWT required decorator that returns JSON error"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'details': str(e)}), 401
    return wrapper

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or user.role != UserRole.ADMIN:
                return jsonify({'error': 'Admin access required'}), 403

            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'details': str(e)}), 401
    return wrapper

def role_required(*roles):
    """Decorator to require specific roles"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user or user.role not in roles:
                    return jsonify({'error': f'One of the following roles required: {", ".join(r.value for r in roles)}'}), 403

                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authentication required', 'details': str(e)}), 401
        return wrapper
    return decorator
