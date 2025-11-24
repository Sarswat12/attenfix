from flask import Blueprint, request, jsonify
import traceback
import logging
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from app import db
from app.models.user import User, UserStatus, UserRole
from app.models.settings import UserSettings
from app.utils.validators import validate_email, validate_password
from app.utils.errors import ValidationError, AuthenticationError
from app.services.auth_service import AuthService
from app.models.auth_token import AuthToken
from flask_jwt_extended import decode_token
import hashlib
import uuid
from app.utils.logger import setup_logger

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_service = AuthService()
logger = setup_logger()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()

        # Validate input: accept either `name` or `first_name`+`last_name`
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        if not data.get('name') and not (data.get('first_name') and data.get('last_name')):
            return jsonify({'error': 'Missing name (provide "name" or "first_name" and "last_name")'}), 400

        if not data.get('email') or not data.get('password') or not data.get('role'):
            return jsonify({'error': 'Email, password and role are required'}), 400

        # Normalize and validate
        email = data['email'].strip().lower()
        validate_email(email)
        validate_password(data['password'])

        # Check if email exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Build display name
        if data.get('name'):
            name = data['name'].strip()
        else:
            name = f"{data.get('first_name').strip()} {data.get('last_name').strip()}"

        # Create user id and role enum
        user_id = f"{data['role'].upper()[:3]}{str(uuid.uuid4().int)[-3:]}"
        # Resolve role: accept either name (ADMIN/EMPLOYEE) or value (admin/employee)
        role_raw = data['role'].strip()
        # Try resolving by name (case-insensitive) then by value
        try:
            role_enum = UserRole[role_raw.upper()]
        except KeyError:
            # try matching by value (e.g., 'employee')
            matched = None
            for r in UserRole:
                if r.value.lower() == role_raw.lower():
                    matched = r
                    break
            if not matched:
                return jsonify({'error': 'Invalid role provided. Valid roles: ADMIN, EMPLOYEE, STUDENT'}), 400
            role_enum = matched

        # Store the role as the Enum member so SQLAlchemy persists it correctly
        # Store role as the Enum NAME to match DB enum values (preexisting DB may use names)
        # e.g., store 'EMPLOYEE' instead of 'employee'
        user = User(
            id=user_id,
            name=name,
            email=email,
            role=role_enum.name,
            status=UserStatus.ACTIVE,
            join_date=datetime.now().date()
        )
        user.set_password(data['password'])

        # Create user settings
        settings = UserSettings(user_id=user_id)

        db.session.add(user)
        db.session.add(settings)
        db.session.commit()

        logger.info(f"User registered successfully: {user_id} ({email})")

        # Generate token (include role and name in claims)
        access_token = create_access_token(identity=user_id, additional_claims={
            'role': role_enum.name,
            'name': name
        })

        # Store token metadata in DB (session)
        try:
            auth_service.store_token(access_token, user_id, device_name=request.headers.get('User-Agent'), ip_address=request.remote_addr)
        except Exception:
            pass

        # Return values using local variables to avoid triggering Enum lookup errors
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'token': access_token,
            'name': name,
            'role': role_enum.name
        }), 201

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        # Include traceback in response temporarily for debugging (remove in production)
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        email = data['email'].strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        if user.status == UserStatus.SUSPENDED:
            return jsonify({'error': 'Account suspended'}), 403

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate token (include role and name in claims)
        # Normalize role for token: if stored as Enum, use .name, else str
        # Normalize stored role whether it's an Enum or a string (some DBs contain names, others values)
        try:
            # If stored as Enum member
            stored_role_name = user.role.name
        except LookupError:
            # Enum value in DB didn't match defined Enum values; fetch raw value and normalize
            row = db.session.execute("SELECT role FROM users WHERE id = :id", {'id': user.id}).fetchone()
            raw_role = row[0] if row else str(user.role)
            stored_role_name = None
            try:
                stored_role_name = UserRole[str(raw_role).upper()].name
            except Exception:
                for r in UserRole:
                    if str(raw_role).lower() in (r.value.lower(), r.name.lower()):
                        stored_role_name = r.name
                        break
            if not stored_role_name:
                stored_role_name = str(raw_role).upper()
        except Exception:
            # Other unexpected errors: fallback
            stored_role_name = str(user.role).upper()

        access_token = create_access_token(identity=user.id, additional_claims={
            'role': stored_role_name,
            'name': user.name
        })

        # Store token metadata in DB (session)
        try:
            auth_service.store_token(access_token, user.id, device_name=request.headers.get('User-Agent'), ip_address=request.remote_addr)
        except Exception:
            pass

        logger.info(f"User logged in: {user.id} ({email})")

        return jsonify({
            'token': access_token,
            'user_id': user.id,
            'name': user.name,
            'role': stored_role_name
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout - revoke token"""
    try:
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        jti = jwt_data.get('jti')

        # Revoke token by jti
        auth_service.revoke_token(jti, 'User logout')

        logger.info(f"User logged out: {user_id}")

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

        logging.info(f"Token verified for user: {user_id}")

        # Normalize role for response: handle Enum or plain string stored in DB
        try:
            role_value = user.role.value
        except Exception:
            try:
                role_value = user.role.name
            except Exception:
                role_value = str(user.role)

        return jsonify({
            'valid': True,
            'user_id': user_id,
            'name': user.name,
            'role': role_value
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 401
