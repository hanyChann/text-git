# Contoh ini menggunakan koneksi dasar dengan PyMySQL (jika Anda menggunakannya)
import pymysql.cursors
from dotenv import load_dotenv
import os

load_dotenv()

# Konfigurasi Database
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'db_praktikum')

def get_db_connection():
    """Mengembalikan objek koneksi database baru."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor # Gunakan DictCursor untuk mempermudah handling
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        # Dalam lingkungan produksi, lebih baik raise exception
        return None