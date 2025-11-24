class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class AuthorizationError(Exception):
    """Raised when authorization fails"""
    pass

class NotFoundError(Exception):
    """Raised when a resource is not found"""
    pass

class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass

def handle_validation_error(error):
    """Handle ValidationError exceptions"""
    return {'error': str(error)}, 400

def handle_authentication_error(error):
    """Handle AuthenticationError exceptions"""
    return {'error': str(error)}, 401

def handle_authorization_error(error):
    """Handle AuthorizationError exceptions"""
    return {'error': str(error)}, 403

def handle_not_found_error(error):
    """Handle NotFoundError exceptions"""
    return {'error': str(error)}, 404

def handle_database_error(error):
    """Handle DatabaseError exceptions"""
    return {'error': str(error)}, 500

def handle_generic_error(error):
    """Handle generic exceptions"""
    return {'error': 'Internal server error'}, 500
