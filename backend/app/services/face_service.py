import numpy as np
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
from app import db
from app.models.face_encoding import FaceEncoding, FaceEncodingStatus
from app.models.user import User
from config import Config
from typing import Dict, List, Tuple, Optional

class FaceService:
    """Face recognition service using face_recognition library"""

    def __init__(self):
        self.threshold = Config.FACE_RECOGNITION_THRESHOLD

    def recognize_face(self, unknown_encoding: np.ndarray, threshold: float = None) -> Dict:
        """
        Recognize face by comparing with stored encodings

        Args:
            unknown_encoding: Face encoding of unknown face
            threshold: Recognition threshold (optional)

        Returns:
            Dict with recognition results
        """
        if threshold is None:
            threshold = self.threshold

        # Get all verified face encodings
        verified_encodings = FaceEncoding.query.filter_by(status=FaceEncodingStatus.VERIFIED).all()

        if not verified_encodings:
            return {
                'recognized': False,
                'message': 'No verified face encodings in database'
            }

        # Extract encodings and user IDs
        known_encodings = []
        user_ids = []
        encoding_ids = []

        for enc in verified_encodings:
            encoding_vector = np.frombuffer(enc.encoding_vector, dtype=np.float64)
            known_encodings.append(encoding_vector)
            user_ids.append(enc.user_id)
            encoding_ids.append(enc.id)

        # Convert to numpy arrays
        known_encodings = np.array(known_encodings)

        # Calculate face distances
        face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)

        # Find best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]

        if best_distance <= threshold:
            user_id = user_ids[best_match_index]
            user = User.query.get(user_id)

            return {
                'recognized': True,
                'user_id': user_id,
                'user_name': user.name if user else 'Unknown',
                'face_encoding_id': encoding_ids[best_match_index],
                'confidence': 1.0 - best_distance,  # Convert distance to confidence
                'distance': best_distance
            }
        else:
            return {
                'recognized': False,
                'message': 'Face not recognized',
                'best_distance': best_distance
            }

    def enroll_face(self, user_id: str, image_path: str) -> Tuple[bool, str]:
        """
        Enroll a new face for a user

        Args:
            user_id: User ID
            image_path: Path to face image

        Returns:
            Tuple of (success, message)
        """
        try:
            # Load and process image
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                return False, "No face detected in image"

            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please provide image with single face"

            # Get face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if len(face_encodings) == 0:
                return False, "Could not encode face"

            encoding = face_encodings[0]

            # Check if user already has maximum encodings
            verified_count = FaceEncoding.query.filter_by(
                user_id=user_id,
                status=FaceEncodingStatus.VERIFIED
            ).count()

            if verified_count >= Config.MAX_FACE_IMAGES:
                return False, f"Maximum {Config.MAX_FACE_IMAGES} face images already enrolled"

            # Save encoding to database
            face_encoding = FaceEncoding(
                user_id=user_id,
                encoding_vector=encoding.tobytes(),
                image_url=image_path,
                status=FaceEncodingStatus.PENDING
            )

            db.session.add(face_encoding)
            db.session.commit()

            return True, "Face enrolled successfully. Awaiting verification."

        except Exception as e:
            db.session.rollback()
            return False, f"Error enrolling face: {str(e)}"

    def verify_face_quality(self, image_path: str) -> Dict:
        """
        Verify face image quality

        Args:
            image_path: Path to face image

        Returns:
            Dict with quality metrics
        """
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                return {'quality_score': 0, 'issues': ['No face detected']}

            if len(face_locations) > 1:
                return {'quality_score': 0, 'issues': ['Multiple faces detected']}

            # Get face encoding to check if face is clear
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if len(face_encodings) == 0:
                return {'quality_score': 0, 'issues': ['Could not encode face']}

            # Basic quality checks
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top

            issues = []

            # Check face size (should be at least 100x100 pixels)
            if face_width < 100 or face_height < 100:
                issues.append('Face too small')

            # Check if face is centered (basic check)
            image_height, image_width = image.shape[:2]
            face_center_x = (left + right) / 2
            face_center_y = (top + bottom) / 2

            if abs(face_center_x - image_width/2) > image_width * 0.3:
                issues.append('Face not centered horizontally')

            if abs(face_center_y - image_height/2) > image_height * 0.3:
                issues.append('Face not centered vertically')

            # Calculate quality score
            quality_score = 1.0
            if issues:
                quality_score -= len(issues) * 0.2
                quality_score = max(0, quality_score)

            return {
                'quality_score': quality_score,
                'issues': issues,
                'face_location': face_locations[0]
            }

        except Exception as e:
            return {'quality_score': 0, 'issues': [f'Error analyzing image: {str(e)}']}

    def get_user_encodings(self, user_id: str) -> List[FaceEncoding]:
        """Get all face encodings for a user"""
        return FaceEncoding.query.filter_by(user_id=user_id).all()

    def delete_user_encodings(self, user_id: str) -> int:
        """Delete all face encodings for a user"""
        deleted_count = FaceEncoding.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return deleted_count
