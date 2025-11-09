from functools import wraps
from flask import request, jsonify, g
import jwt, os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET', 'supersecretkey')
JWT_ALGORITHM = 'HS256'
print("DEBUG JWT_SECRET:", JWT_SECRET)

def jwt_required(f):
    """Decorator untuk memeriksa token JWT di header Authorization."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 1. Ambil header Authorization
        auth_header = request.headers.get('Authorization')
        print("DEBUG HEADER RAW:", auth_header)  # 👈 tambahkan ini
        
        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401 

        # 2. Pastikan format Bearer <token>
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid Authorization header format'}), 401 
        
        token = parts[1] 
        print("DEBUG TOKEN DECODE ATTEMPT:", token)  # 👈 tambahkan ini
        
        # 3. Decode token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]) 
        except jwt.ExpiredSignatureError:
            # Tangkap ExpiredSignatureError → kembalikan 401
            return jsonify({'error': 'Token expired'}), 401 
        except jwt.InvalidTokenError:
            # Tangkap InvalidTokenError → kembalikan 401
            return jsonify({'error': 'Invalid token'}), 401

        # 4. Simpan payload di flask.g
        g.user = {
            'user_id': payload.get('sub'),
            'role': payload.get('role')
        } 
        # 5. Lanjutkan eksekusi fungsi route
        return f(*args, **kwargs) 
    return wrapper

def role_required(allowed_roles):
    """Decorator untuk memastikan user punya role tertentu (RBAC)."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Pastikan jwt_required sudah berjalan dan g.user sudah ada
            if not hasattr(g, 'user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = g.user.get('role')
            
            # Cek apakah role user ada di dalam daftar role yang diizinkan
            if user_role not in allowed_roles:
                return jsonify({'error': 'Forbidden: role tidak memiliki akses'}), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator