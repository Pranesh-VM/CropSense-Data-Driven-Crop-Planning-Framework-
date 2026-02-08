"""
Authentication Module for CropSense

Handles farmer registration, login, and session management.
"""

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


class AuthManager:
    """Handles authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    @staticmethod
    def create_token(farmer_id: int, username: str, email: str) -> str:
        """
        Create a JWT token for authenticated user.
        
        Args:
            farmer_id: Database ID of farmer
            username: Farmer's username
            email: Farmer's email
            
        Returns:
            JWT token string
        """
        payload = {
            'farmer_id': farmer_id,
            'username': username,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        try:
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            # PyJWT 2.0+ returns string directly, older versions return bytes
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            return token
        except Exception as e:
            raise Exception(f"Token creation failed: {str(e)}")
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """
        Extract JWT token from Authorization header.
        
        Args:
            auth_header: Authorization header value (e.g., "Bearer <token>")
            
        Returns:
            Token string if valid format, None otherwise
        """
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


# Decorator for protected routes
def require_auth(f):
    """
    Decorator to protect routes that require authentication.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route(current_user):
            # current_user contains farmer_id, username, email
            return jsonify({'message': f'Hello {current_user["username"]}'})
    """
    from functools import wraps
    from flask import request, jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        token = AuthManager.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Verify token
        payload = AuthManager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Pass user info to route handler
        return f(current_user=payload, *args, **kwargs)
    
    return decorated_function


class FarmerAuthService:
    """Service for farmer authentication operations with database."""
    
    def __init__(self, db_manager):
        """
        Initialize with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.auth = AuthManager()
    
    def register_farmer(
        self,
        username: str,
        email: str,
        password: str,
        name: str,
        phone: str = None,
        location: str = None,
        latitude: float = None,
        longitude: float = None
    ) -> Dict:
        """
        Register a new farmer.
        
        Args:
            username: Unique username
            email: Unique email
            password: Plain text password (will be hashed)
            name: Farmer's full name
            phone: Phone number (optional)
            location: Location string (optional)
            latitude, longitude: GPS coordinates (optional)
            
        Returns:
            Dictionary with success status and token/error
        """
        # Validate inputs
        if len(username) < 3:
            return {'success': False, 'error': 'Username must be at least 3 characters'}
        
        if len(password) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}
        
        if '@' not in email:
            return {'success': False, 'error': 'Invalid email format'}
        
        # Hash password
        password_hash = self.auth.hash_password(password)
        
        # Insert into database
        try:
            with self.db.get_connection() as (conn, cursor):
                cursor.execute("""
                    INSERT INTO farmers (
                        username, email, password_hash, name, phone, 
                        location, latitude, longitude
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING farmer_id, username, email, name
                """, (username, email, password_hash, name, phone, location, latitude, longitude))
                
                farmer = dict(cursor.fetchone())
                
                # Create default field
                cursor.execute("""
                    INSERT INTO fields (farmer_id, field_name, area_hectares)
                    VALUES (%s, 'Main Field', 1.0)
                    RETURNING field_id
                """, (farmer['farmer_id'],))
                
                field = cursor.fetchone()
                
                # Generate token
                token = self.auth.create_token(
                    farmer['farmer_id'],
                    farmer['username'],
                    farmer['email']
                )
                
                return {
                    'success': True,
                    'farmer': farmer,
                    'field_id': field['field_id'],
                    'token': token,
                    'message': 'Registration successful'
                }
                
        except Exception as e:
            error_msg = str(e)
            if 'username' in error_msg and 'unique' in error_msg.lower():
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in error_msg and 'unique' in error_msg.lower():
                return {'success': False, 'error': 'Email already registered'}
            else:
                return {'success': False, 'error': f'Registration failed: {error_msg}'}
    
    def login_farmer(self, username_or_email: str, password: str) -> Dict:
        """
        Login a farmer.
        
        Args:
            username_or_email: Username or email
            password: Plain text password
            
        Returns:
            Dictionary with success status and token/error
        """
        try:
            with self.db.get_connection() as (conn, cursor):
                # Find farmer by username or email
                cursor.execute("""
                    SELECT farmer_id, username, email, password_hash, name, is_active
                    FROM farmers
                    WHERE username = %s OR email = %s
                """, (username_or_email, username_or_email))
                
                farmer = cursor.fetchone()
                
                if not farmer:
                    return {'success': False, 'error': 'Invalid credentials'}
                
                farmer = dict(farmer)
                
                # Check if account is active
                if not farmer['is_active']:
                    return {'success': False, 'error': 'Account is disabled'}
                
                # Verify password
                if not self.auth.verify_password(password, farmer['password_hash']):
                    return {'success': False, 'error': 'Invalid credentials'}
                
                # Update last login
                cursor.execute("""
                    UPDATE farmers 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE farmer_id = %s
                """, (farmer['farmer_id'],))
                
                # Get farmer's field
                cursor.execute("""
                    SELECT field_id FROM fields 
                    WHERE farmer_id = %s 
                    ORDER BY field_id 
                    LIMIT 1
                """, (farmer['farmer_id'],))
                
                field = cursor.fetchone()
                field_id = field['field_id'] if field else None
                
                # Generate token
                token = self.auth.create_token(
                    farmer['farmer_id'],
                    farmer['username'],
                    farmer['email']
                )
                
                return {
                    'success': True,
                    'farmer': {
                        'farmer_id': farmer['farmer_id'],
                        'username': farmer['username'],
                        'email': farmer['email'],
                        'name': farmer['name']
                    },
                    'field_id': field_id,
                    'token': token,
                    'message': 'Login successful'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    def get_farmer_profile(self, farmer_id: int) -> Optional[Dict]:
        """Get farmer profile information."""
        try:
            with self.db.get_connection() as (conn, cursor):
                cursor.execute("""
                    SELECT 
                        farmer_id, username, email, name, phone, 
                        location, latitude, longitude, created_at, last_login
                    FROM farmers
                    WHERE farmer_id = %s
                """, (farmer_id,))
                
                farmer = cursor.fetchone()
                return dict(farmer) if farmer else None
                
        except Exception as e:
            print(f"Error getting farmer profile: {e}")
            return None


if __name__ == "__main__":
    """Test authentication functions."""
    print("=" * 80)
    print("Authentication Module Test")
    print("=" * 80)
    
    auth = AuthManager()
    
    # Test password hashing
    print("\n1. Testing Password Hashing:")
    password = "test123"
    hashed = auth.hash_password(password)
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    print(f"   Verification: {auth.verify_password(password, hashed)}")
    print(f"   Wrong password: {auth.verify_password('wrong', hashed)}")
    
    # Test JWT token creation
    print("\n2. Testing JWT Tokens:")
    token = auth.create_token(1, 'testuser', 'test@example.com')
    print(f"   Token: {token[:50]}...")
    
    payload = auth.verify_token(token)
    print(f"   Verified: {payload}")
    
    # Test invalid token
    invalid = auth.verify_token('invalid.token.here')
    print(f"   Invalid token result: {invalid}")
    
    print("\n" + "=" * 80)
    print("Authentication Tests Complete ✓")
    print("=" * 80)
