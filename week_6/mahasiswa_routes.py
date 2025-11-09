from flask import Blueprint, jsonify, request, g
from koneksi_pool import get_db_connection
from utils_auth import jwt_required, role_required

mahasiswa_bp = Blueprint('mahasiswa', __name__)

# Hanya boleh diakses oleh Admin
@mahasiswa_bp.route('/', methods=['GET'])
@jwt_required 
@role_required(['admin']) 
def get_all_mahasiswa():
    conn = get_db_connection() 
    cur = conn.cursor() 
    cur.execute('SELECT nim, nama, jurusan, user_id FROM mahasiswa') 
    rows = cur.fetchall() 
    cur.close() 
    conn.close() 

    result = []
    for row in rows:
        result.append(row) 
    return jsonify(result), 200


@mahasiswa_bp.route('/<nim>', methods=['GET'])
@jwt_required 
def get_mahasiswa_by_nim(nim):
    user_role = g.user['role']
    user_id = g.user['user_id']

    conn = get_db_connection() 
    cur = conn.cursor() 
    cur.execute('SELECT nim, nama, jurusan, user_id FROM mahasiswa WHERE nim = %s', (nim,))
    row = cur.fetchone() 
    cur.close() 
    conn.close() 

    if not row:
        return jsonify({'error': 'Mahasiswa tidak ditemukan'}), 404
    
    # Asumsi DictCursor
    if isinstance(row, dict):
        mahasiswa_user_id = row['user_id']
        result = {k: row[k] for k in ['nim', 'nama', 'jurusan']}
    else: # Jika menggunakan Tuple
        mahasiswa_user_id = row[3]
        result = {'nim': row[0], 'nama': row[1], 'jurusan': row[2]} 

    # Admin bisa akses semua data
    if user_role == 'admin': 
        return jsonify(result), 200 

    # Mahasiswa hanya boleh akses data dirinya sendiri
    elif user_role == 'mahasiswa':
        # user_id di JWT harus sama dengan mahasiswa_user_id di database
        if mahasiswa_user_id is None or int(mahasiswa_user_id) != int(user_id):
            return jsonify({'error': 'Forbidden: → akses ditolak'}), 403
        return jsonify(result), 200 
    # Role lain ditolak
    else: 
        return jsonify({'error': 'Forbidden'}), 403


# --- CREATE Mahasiswa ---
# Hanya boleh diakses oleh Admin
@mahasiswa_bp.route('/', methods=['POST'])
@jwt_required 
@role_required(['admin']) 
def create_mahasiswa():
    data = request.get_json() or {} 
    nim = data.get('nim') 
    nama = data.get('nama') 
    jurusan = data.get('jurusan')

    if not nim or not nama or not jurusan:
        return jsonify({'error': 'Data mahasiswa tidak lengkap'}), 400

    conn = get_db_connection() 
    cur = conn.cursor() 
    cur.execute(
        'INSERT INTO mahasiswa (nim, nama, jurusan) VALUES (%s, %s, %s)',
        (nim, nama, jurusan)
    ) 
    conn.commit() 
    cur.close() 
    conn.close() 
    return jsonify({'message': 'Mahasiswa berhasil ditambahkan'}), 201 


# --- UPDATE Mahasiswa ---
# Hanya boleh diakses oleh Admin
@mahasiswa_bp.route('/<nim>', methods=['PUT'])
@jwt_required 
@role_required(['admin'])
def update_mahasiswa(nim):
    data = request.get_json() or {}
    nama = data.get('nama') 
    jurusan = data.get('jurusan') 

    if not nama or not jurusan:
        return jsonify({'error': 'Data update tidak lengkap'}), 400 

    conn = get_db_connection() 
    cur = conn.cursor() 
    cur.execute(
        'UPDATE mahasiswa SET nama = %s, jurusan = %s WHERE nim=%s',
        (nama, jurusan, nim)
    ) 
    conn.commit() 
    cur.close() 
    conn.close() 
    return jsonify({'message': 'Mahasiswa berhasil diperbarui'}), 200 


# --- DELETE Mahasiswa ---
# Hanya boleh diakses oleh Admin
@mahasiswa_bp.route('/<nim>', methods=['DELETE'])
@jwt_required 
@role_required(['admin']) 
def delete_mahasiswa(nim):
    conn = get_db_connection()
    cur = conn.cursor() 
    cur.execute('DELETE FROM mahasiswa WHERE nim = %s', (nim,)) 
    conn.commit() 
    cur.close() 
    conn.close() 
    return jsonify({'message': 'Mahasiswa berhasil dihapus'}), 200 