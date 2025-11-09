from flask import Flask, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

from auth_routes import auth_bp
from mahasiswa_routes import mahasiswa_bp
from mata_kuliah_routes import mata_kuliah_bp 

bcrypt = Bcrypt()
cors = CORS()

def create_app():
    """
    Fungsi factory untuk membuat dan mengkonfigurasi aplikasi Flask.
    """
    app = Flask(__name__)
    
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'ganti_dengan_secret_yang_kuat')
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    cors.init_app(app) 
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(mahasiswa_bp, url_prefix='/mahasiswa')
    app.register_blueprint(mata_kuliah_bp, url_prefix='/mata-kuliah')
    
    @app.route('/')
    def index():
        return jsonify({'message': 'API is running', 'version': 'v1.0 (JWT+RBAC)'}), 200

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)