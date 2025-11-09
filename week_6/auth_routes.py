from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt, os
from datetime import datetime, timedelta
from koneksi_pool import get_db_connection
from dotenv import load_dotenv

load_dotenv()
bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

JWT_SECRET = os.getenv('JWT_SECRET', 'supersecretkey')
JWT_ALGORITHM = 'HS256' 
JWT_EXP_MINUTES = 60 
print("DEBUG JWT_SECRET:", JWT_SECRET)

@auth_bp.route('/login', methods=['POST'])
def login():
    # 1. Terima username dan password dari JSON body
    data = request.get_json() or {} 
    username = data.get('username')
    password = data.get('password') 

    if not username or not password:
        return jsonify({'error': 'Username dan password wajib diisi'}), 400 

    conn = get_db_connection() 
    cur = conn.cursor() 
    
    # 2. Ambil record user (beserta nama role) dari DB
    sql = """
        SELECT u.id AS user_id, u.username, u.password_hash, r.name AS role
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = %s
    """ 
    cur.execute(sql, (username,)) 
    user_row = cur.fetchone() 
    cur.close() 
    conn.close() 

    if not user_row:
        return jsonify({'error': 'Kredensial salah'}), 401 

    # Handle hasil query (asumsi menggunakan DictCursor dari koneksi_pool.py)
    if isinstance(user_row, dict): 
        password_hash = user_row['password_hash'] 
        user_id = user_row['user_id'] 
        role = user_row['role'] 
    else: # Jika menggunakan tuple (asumsi urutan: id, username, password_hash, role)
        password_hash = user_row[2] 
        user_id = user_row[0] 
        role = user_row[3] 


    # 4. Verifikasi password dengan bcrypt.check_password_hash
    if not bcrypt.check_password_hash(password_hash, password):
        return jsonify({'error': 'Kredensial salah'}), 401 

    # 5. Jika valid, buat payload JWT yang memuat sub (user_id) dan role
    payload = {
        'sub': str(user_id), # Subject: user ID
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    
    # 6. Kembalikan token
    return jsonify({
        'access_token': token,
        'role': role,
        'user_id': user_id
    }), 200 