from app import db
from app.models.user import User
from app.models.auth_token import AuthToken
from datetime import datetime, timedelta
from flask_jwt_extended import decode_token
import hashlib


class AuthService:
    """Authentication service for JWT token management backed by DB"""

    def __init__(self):
        pass

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    def store_token(self, token: str, user_id: str, device_name: str = None, ip_address: str = None):
        """Store token metadata in DB for session management"""
        try:
            decoded = decode_token(token)
            jti = decoded.get('jti')
            exp = decoded.get('exp')
            expires_at = datetime.utcfromtimestamp(exp) if exp else datetime.utcnow() + timedelta(hours=24)

            token_hash = self._hash_token(token)

            auth_token = AuthToken(
                id=jti,
                user_id=user_id,
                token_hash=token_hash,
                device_name=device_name,
                ip_address=ip_address,
                issued_at=datetime.utcnow(),
                expires_at=expires_at,
                is_revoked=False
            )
            db.session.add(auth_token)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Failed to store auth token: {e}")
            return False

    def revoke_token(self, jti: str, reason='logout'):
        """Mark token as revoked by jti"""
        try:
            token = AuthToken.query.get(jti)
            if not token:
                print(f"No token row found for jti={jti}")
                return False
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            token.revocation_reason = reason
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Failed to revoke token {jti}: {e}")
            return False

    def is_token_revoked(self, jti: str) -> bool:
        """Return True if token with given jti is revoked or expired"""
        try:
            token = AuthToken.query.get(jti)
            if not token:
                # If token not found in DB, treat as revoked for safety
                return True
            if token.is_revoked:
                return True
            if token.expires_at and token.expires_at < datetime.utcnow():
                return True
            return False
        except Exception as e:
            print(f"Error checking token revocation: {e}")
            return True

    # Existing helpers for password reset are left unchanged (if present elsewhere)
