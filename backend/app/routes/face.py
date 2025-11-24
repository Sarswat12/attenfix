from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os
import base64
import numpy as np
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
from PIL import Image
import io
from app import db
from app.models.face_encoding import FaceEncoding, FaceEncodingStatus
from app.models.user import User
from app.services.face_service import FaceService
from app.utils.decorators import admin_required
from config import Config

face_bp = Blueprint('face', __name__, url_prefix='/api/face')
face_service = FaceService()

@face_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_face():
    """Enroll face for current user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if user already has verified face encodings
        verified_count = FaceEncoding.query.filter_by(
            user_id=user_id,
            status=FaceEncodingStatus.VERIFIED
        ).count()

        if verified_count >= Config.MAX_FACE_IMAGES:
            return jsonify({'error': 'Maximum face images already enrolled'}), 400

        # Get image from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']

        # Process image
        image = Image.open(image_file)
        image_array = np.array(image)

        # Detect faces
        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) == 0:
            return jsonify({'error': 'No face detected in image'}), 400
        elif len(face_locations) > 1:
            return jsonify({'error': 'Multiple faces detected. Please provide image with single face'}), 400

        # Get face encoding
        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if len(face_encodings) == 0:
            return jsonify({'error': 'Could not encode face'}), 400

        encoding = face_encodings[0]

        # Save image file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{user_id}_{timestamp}.jpg"
        image_path = os.path.join(Config.UPLOAD_FOLDER, 'faces', image_filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)

        # Create face encoding record
        face_encoding_id = f"FACE_ENC_{user_id}_{timestamp}"
        face_encoding = FaceEncoding(
            id=face_encoding_id,
            user_id=user_id,
            encoding_vector=encoding.tobytes(),
            image_url=image_path,
            captured_at=datetime.utcnow(),
            quality_score=1.0,  # TODO: Implement quality scoring
            face_confidence=1.0,  # TODO: Implement confidence scoring
            status=FaceEncodingStatus.PENDING
        )

        db.session.add(face_encoding)
        db.session.commit()

        return jsonify({
            'message': 'Face enrolled successfully. Awaiting verification.',
            'face_encoding_id': face_encoding_id,
            'status': 'pending'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@face_bp.route('/recognize', methods=['POST'])
def recognize_face():
    """Recognize face and mark attendance"""
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        location = request.form.get('location', 'Main Gate')

        # Process image
        image = Image.open(image_file)
        image_array = np.array(image)

        # Detect and encode face
        face_locations = face_recognition.face_locations(image_array)
        if len(face_locations) == 0:
            return jsonify({'error': 'No face detected'}), 400

        face_encodings = face_recognition.face_encodings(image_array, face_locations)
        if len(face_encodings) == 0:
            return jsonify({'error': 'Could not encode face'}), 400

        unknown_encoding = face_encodings[0]

        # Find best match
        result = face_service.recognize_face(unknown_encoding, threshold=Config.FACE_RECOGNITION_THRESHOLD)

        if not result['recognized']:
            return jsonify({
                'recognized': False,
                'message': 'Face not recognized'
            }), 404

        # Mark attendance
        from app.services.attendance_service import AttendanceService
        attendance_service = AttendanceService()

        attendance_result, status_code = attendance_service.mark_attendance(
            user_id=result['user_id'],
            status='Present',
            face_encoding_id=result['face_encoding_id'],
            location=location,
            source='face_recognition'
        )

        if status_code == 409:
            # Already marked today
            return jsonify({
                'recognized': True,
                'user_id': result['user_id'],
                'user_name': result['user_name'],
                'message': 'Attendance already marked for today',
                'confidence': result['confidence']
            }), 200

        return jsonify({
            'recognized': True,
            'user_id': result['user_id'],
            'user_name': result['user_name'],
            'message': 'Attendance marked successfully',
            'confidence': result['confidence'],
            'attendance_record': attendance_result
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@face_bp.route('/user/<user_id>/encodings', methods=['GET'])
@jwt_required()
def get_user_face_encodings(user_id):
    """Get face encodings for a user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only view their own encodings unless they're admin
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        encodings = FaceEncoding.query.filter_by(user_id=user_id).all()

        return jsonify({
            'encodings': [enc.to_dict() for enc in encodings]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@face_bp.route('/encodings/<encoding_id>/verify', methods=['PUT'])
@admin_required
def verify_face_encoding(encoding_id):
    """Verify face encoding (admin only)"""
    try:
        encoding = FaceEncoding.query.get(encoding_id)
        if not encoding:
            return jsonify({'error': 'Face encoding not found'}), 404

        data = request.get_json()
        status = data.get('status', 'verified')
        notes = data.get('notes')

        encoding.status = status
        if notes:
            encoding.verification_notes = notes

        db.session.commit()

        return jsonify({
            'message': 'Face encoding updated successfully',
            'encoding': encoding.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@face_bp.route('/encodings/<encoding_id>', methods=['DELETE'])
@jwt_required()
def delete_face_encoding(encoding_id):
    """Delete face encoding"""
    try:
        current_user_id = get_jwt_identity()
        encoding = FaceEncoding.query.get(encoding_id)

        if not encoding:
            return jsonify({'error': 'Face encoding not found'}), 404

        # Users can only delete their own encodings unless they're admin
        current_user = User.query.get(current_user_id)
        if current_user.role != 'admin' and encoding.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403

        # Delete image file
        if os.path.exists(encoding.image_url):
            os.remove(encoding.image_url)

        db.session.delete(encoding)
        db.session.commit()

        return jsonify({'message': 'Face encoding deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@face_bp.route('/status/<user_id>', methods=['GET'])
@jwt_required()
def get_face_enrollment_status(user_id):
    """Get face enrollment status for user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # Users can only view their own status unless they're admin
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403

        total_encodings = FaceEncoding.query.filter_by(user_id=user_id).count()
        verified_encodings = FaceEncoding.query.filter_by(
            user_id=user_id,
            status=FaceEncodingStatus.VERIFIED
        ).count()

        return jsonify({
            'user_id': user_id,
            'total_encodings': total_encodings,
            'verified_encodings': verified_encodings,
            'is_enrolled': verified_encodings >= Config.MIN_FACE_IMAGES,
            'min_required': Config.MIN_FACE_IMAGES,
            'max_allowed': Config.MAX_FACE_IMAGES
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
