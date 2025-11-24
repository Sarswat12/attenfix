import sys
import os

# Ensure backend package is importable when running this script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    # Update role values to uppercase names to match DB enum values
    try:
        from sqlalchemy import text
        db.session.execute(text("UPDATE users SET role = UPPER(role) WHERE role IS NOT NULL"))
        db.session.commit()
        print('Updated existing user roles to uppercase.')
    except Exception as e:
        db.session.rollback()
        print('Failed to update roles:', e)
