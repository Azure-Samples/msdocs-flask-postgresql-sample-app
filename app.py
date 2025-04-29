import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# Configuración igual que antes…
if 'WEBSITE_HOSTNAME' not in os.environ:
    app.config.from_object('azureproject.development')
else:
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI = app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importa tu nuevo modelo
from models import ImageUpload

# ---------------------------------------------------
# 1. Endpoint REST para recibir la subida de datos
# ---------------------------------------------------
@app.route('/api/upload_data', methods=['POST'])
@csrf.exempt
def upload_data():
    """
    Espera un JSON con:
      - filename:    nombre del fichero
      - red_pixels:   int
      - green_pixels: int
      - blue_pixels:  int
      - user_name:    string
    """
    payload = request.get_json(force=True)
    try:
        filename    = payload['filename']
        r_count     = int(payload['red_pixels'])
        g_count     = int(payload['green_pixels'])
        b_count     = int(payload['blue_pixels'])
        user_name   = payload['user_name']
    except (KeyError, ValueError):
        return jsonify({"error": "Payload inválido"}), 400

    # Creamos la fila y la guardamos
    upload = ImageUpload(
        filename    = filename,
        red_pixels   = r_count,
        green_pixels = g_count,
        blue_pixels  = b_count,
        user_name   = user_name,
        upload_date = datetime.utcnow()    # o dejar que el default lo ponga
    )
    db.session.add(upload)
    db.session.commit()

    return jsonify({
        "message": "Datos recibidos correctamente",
        "upload_id": upload.id
    }), 201

# ---------------------------------------------------
# 2. Vista web para ver el historial de subidas
# ---------------------------------------------------
@app.route('/uploads', methods=['GET'])
def view_uploads():
    uploads = ImageUpload.query.order_by(ImageUpload.upload_date.desc()).all()
    return render_template('uploads.html', uploads=uploads)

# ---------------------------------------------------
# 3. Ruta raíz (puedes mantener tu galería o landing)
# ---------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')   # O redirige a /uploads si quieres

# ---------------------------------------------------
# 4. Favicon, utilidades, etc. (quedan igual)
# ---------------------------------------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
