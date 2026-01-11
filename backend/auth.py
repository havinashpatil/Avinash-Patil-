"""
Authentication and authorization module for Blood Sense AI.
Handles JWT tokens, password hashing, and role-based access control.
"""
import bcrypt
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from database import get_db
from typing import Tuple, Optional


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Authenticate a user with username and password.
    Returns: (success, user_data, error_message)
    """
    db = get_db()
    
    # Get user from database
    user = db.get_user_by_username(username)
    
    if not user:
        return False, None, "Invalid username or password"
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return False, None, "Invalid username or password"
    
    # Return user data (without password hash)
    user_data = {
        'id': user['_id'],
        'username': user['username'],
        'role': user['role'],
        'email': user['email']
    }
    
    return True, user_data, None


def create_token(user_data: dict) -> str:
    """Create JWT access token with user data"""
    additional_claims = {
        'role': user_data['role'],
        'username': user_data['username']
    }
    
    token = create_access_token(
        identity=user_data['id'],
        additional_claims=additional_claims
    )
    
    return token


def require_role(*allowed_roles):
    """
    Decorator to require specific roles for endpoint access.
    Usage: @require_role('technician', 'clinician')
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'This endpoint requires one of these roles: {", ".join(allowed_roles)}'
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def get_current_user() -> Optional[dict]:
    """
    Get current authenticated user from JWT token.
    Must be called within a JWT-protected route.
    """
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        return {
            'id': user_id,
            'username': claims.get('username'),
            'role': claims.get('role')
        }
    except:
        return None


def register_user(username: str, password: str, role: str, email: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Register a new user.
    Returns: (success, user_id, error_message)
    """
    db = get_db()
    
    # Validate role
    if role not in ['technician', 'clinician']:
        return False, None, "Invalid role. Must be 'technician' or 'clinician'"
    
    # Check if username already exists
    existing_user = db.get_user_by_username(username)
    if existing_user:
        return False, None, "Username already exists"
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    try:
        user_id = db.create_user(username, password_hash, role, email)
        return True, user_id, None
    except Exception as e:
        return False, None, f"Error creating user: {str(e)}"


# Response helpers
def success_response(data: dict, message: str = "Success", status_code: int = 200):
    """Create a success response"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }), status_code


def error_response(message: str, error: str = None, status_code: int = 400):
    """Create an error response"""
    response = {
        'success': False,
        'message': message
    }
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code
