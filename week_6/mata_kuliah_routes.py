from flask import Blueprint, jsonify, request
from koneksi_pool import get_db_connection
from utils_auth import jwt_required, role_required

mata_kuliah_bp = Blueprint('mata_kuliah', __name__)

# Contoh Rute GET ALL: hanya admin yang boleh melihat
@mata_kuliah_bp.route('/', methods=['GET'])
@jwt_required
@role_required(['admin']) 
def get_all_mata_kuliah():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT kode_mk, nama_mk, sks FROM mata_kuliah')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows), 200

# Contoh Rute POST: hanya admin yang boleh menambah
@mata_kuliah_bp.route('/', methods=['POST'])
@jwt_required
@role_required(['admin']) 
def create_mata_kuliah():
    data = request.get_json() or {}
    kode_mk = data.get('kode_mk')
    nama_mk = data.get('nama_mk')
    sks = data.get('sks')

    if not kode_mk or not nama_mk or not sks:
        return jsonify({'error': 'Data mata kuliah tidak lengkap'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO mata_kuliah (kode_mk, nama_mk, sks) VALUES (%s, %s, %s)',
            (kode_mk, nama_mk, sks)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': f'Gagal menambahkan data: {e}'}), 500

    cur.close()
    conn.close()
    return jsonify({'message': 'Mata kuliah berhasil ditambahkan'}), 201

# **Terapkan logika @jwt_required + @role_required(['admin']) untuk PUT dan DELETE rute lainnya**