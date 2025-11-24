from flask import Blueprint, jsonify, request
from app import db
from datetime import datetime
from app.utils.logger import setup_logger
from sqlalchemy import text as sa_text

health_bp = Blueprint('health', __name__, url_prefix='/api/health')
logger = setup_logger()

@health_bp.route('', methods=['GET'])
def health_check():
    """Basic health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'face-attendance-api'
    }), 200

@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with database connectivity"""
    try:
        # Test database connection using SQLAlchemy text()
        db.session.execute(sa_text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'

    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': db_status,
            'api': 'healthy'
        }
    }), 200 if db_status == 'healthy' else 503

@health_bp.route('/welcome', methods=['GET'])
def welcome():
    """
    Returns a welcome message
    """
    logger.info(f"Request received: {request.method} {request.path}")
    return jsonify({'message': 'Welcome to the Face Attendance API Service!'})
