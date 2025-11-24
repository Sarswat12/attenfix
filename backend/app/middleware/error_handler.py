from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.activity_log import ActivityLog, LogStatus
from app import db

def register_error_handlers(app):
    """Register all error handlers with the Flask app"""

    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors"""
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request data'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle authentication errors"""
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': str(error.description) if hasattr(error, 'description') else 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle authorization errors"""
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(error.description) if hasattr(error, 'description') else 'Access denied'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors"""
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': str(error.description) if hasattr(error, 'description') else 'Resource not found'
        }), 404

    @app.errorhandler(409)
    def conflict(error):
        """Handle conflict errors"""
        return jsonify({
            'success': False,
            'error': 'Conflict',
            'message': str(error.description) if hasattr(error, 'description') else 'Resource conflict'
        }), 409

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors"""
        db.session.rollback()
        app.logger.exception('Internal server error')
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        """Handle database errors"""
        db.session.rollback()
        app.logger.error(f'Database error: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': 'A database error occurred'
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        db.session.rollback()
        # Log full exception with traceback so container logs contain diagnostics
        app.logger.exception(f'Unexpected error: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'Unexpected Error',
            'message': 'An unexpected error occurred'
        }), 500
