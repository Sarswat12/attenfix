from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, UserStatus, UserRole
from app.models.settings import UserSettings
from app.utils.decorators import admin_required
from app.utils.validators import validate_email
from app.utils.errors import ValidationError, NotFoundError
import uuid

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only) or current user"""
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)

        if current_user.role == UserRole.ADMIN:
            # Admin can see all users
            role_filter = request.args.get('role')
            status_filter = request.args.get('status')
            department_filter = request.args.get('department')

            query = User.query

            if role_filter:
                query = query.filter_by(role=role_filter)
            if status_filter:
                query = query.filter_by(status=status_filter)
            if department_filter:
                query = query.filter_by(department=department_filter)

            users = query.all()
            return jsonify({
                'users': [user.to_dict() for user in users]
            }), 200
        else:
            # Regular users can only see their own profile
            return jsonify({
                'user': current_user.to_dict()
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user by ID"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only view their own profile unless they're admin
        if current_user.role != UserRole.ADMIN and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        validate_email(data['email'])

        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Generate user ID
        user_id = f"{data['role'].upper()[:3]}{str(uuid.uuid4().int)[-3:]}"

        user = User(
            id=user_id,
            name=data['name'],
            email=data['email'],
            role=data['role'],
            department=data.get('department'),
            phone=data.get('phone'),
            address=data.get('address'),
            status=UserStatus.ACTIVE,
            join_date=data.get('join_date', datetime.now().date())
        )
        user.set_password(data['password'])

        # Create user settings
        settings = UserSettings(user_id=user_id)

        db.session.add(user)
        db.session.add(settings)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only update their own profile unless they're admin
        if current_user.role != UserRole.ADMIN and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        allowed_fields = ['name', 'phone', 'address', 'department']
        if current_user.role == UserRole.ADMIN:
            allowed_fields.extend(['email', 'role', 'status'])

        for field in allowed_fields:
            if field in data:
                if field == 'email':
                    validate_email(data[field])
                    # Check if email is taken by another user
                    existing = User.query.filter_by(email=data[field]).first()
                    if existing and existing.id != user_id:
                        return jsonify({'error': 'Email already in use'}), 409
                setattr(user, field, data[field])

        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Soft delete by setting deleted_at
        user.deleted_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile with settings"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        settings = user.settings

        return jsonify({
            'user': user.to_dict(),
            'settings': settings.to_dict() if settings else None
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
