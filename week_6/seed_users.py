from flask_bcrypt import Bcrypt
from koneksi_pool import get_db_connection

bcrypt = Bcrypt()

def get_value(row, key_or_index):
    """Ambil nilai baik dari dict maupun tuple"""
    if isinstance(row, dict):
        return row.get(key_or_index)
    elif isinstance(row, (list, tuple)):
        if isinstance(key_or_index, int):
            return row[key_or_index]
        else:
            return row[0] if len(row) > 0 else None
    return None

def seed_users():
    conn = get_db_connection()
    cur = conn.cursor()
    print("Menyiapkan data awal roles, users, dan update mahasiswa...\n")

    # 1 Buat roles jika belum ada
    cur.execute("SELECT COUNT(*) AS total FROM roles")
    total_roles = get_value(cur.fetchone(), 'total')

    if not total_roles or total_roles == 0:
        cur.executemany(
            "INSERT INTO roles (name) VALUES (%s)",
            [('admin',), ('mahasiswa',)]
        )
        conn.commit()
        print(" Roles berhasil dibuat")
    else:
        print("ℹ Roles sudah ada, skip...")

    # 2 Ambil role_id
    cur.execute("SELECT id FROM roles WHERE name='admin'")
    admin_role_id = get_value(cur.fetchone(), 'id')

    cur.execute("SELECT id FROM roles WHERE name='mahasiswa'")
    mahasiswa_role_id = get_value(cur.fetchone(), 'id')

    # 3 Hash password
    admin_pass = bcrypt.generate_password_hash("admin123").decode("utf-8")
    mhs_pass = bcrypt.generate_password_hash("mhs123").decode("utf-8")

    # 4 Tambah user admin jika belum ada
    cur.execute("SELECT COUNT(*) AS total FROM users WHERE username='admin'")
    total_admin = get_value(cur.fetchone(), 'total')
    if not total_admin or total_admin == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, role_id) VALUES (%s, %s, %s)",
            ('admin', admin_pass, admin_role_id)
        )
        conn.commit()
        print(" User admin berhasil dibuat")
    else:
        print(" User admin sudah ada, skip...")

    # 5 Buat user mahasiswa per NIM
    cur.execute("SELECT nim FROM mahasiswa")
    daftar_mahasiswa = cur.fetchall()

    for mhs in daftar_mahasiswa:
        nim = get_value(mhs, 'nim')
        username = f"mhs{nim}"

        # Cek apakah user sudah ada
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if not existing_user:
            cur.execute(
                "INSERT INTO users (username, password_hash, role_id) VALUES (%s, %s, %s)",
                (username, mhs_pass, mahasiswa_role_id)
            )
            conn.commit()
            user_id = cur.lastrowid
            print(f" User {username} dibuat (id: {user_id})")
        else:
            user_id = get_value(existing_user, 'id')
            print(f"ℹ User {username} sudah ada (id: {user_id})")

        # Update mahasiswa sesuai nim
        cur.execute(
            "UPDATE mahasiswa SET user_id = %s WHERE nim = %s",
            (user_id, nim)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("\n🎉 Semua mahasiswa sudah punya user_id yang sesuai!\n")

if __name__== "_main_":
    seed_users()