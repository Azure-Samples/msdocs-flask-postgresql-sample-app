import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from flask import Flask, jsonify





os.urandom(24)

app = Flask(__name__, static_folder='static')



#csrf = CSRFProtect(app)



# Set the secret key for CSRF protection
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Usa una clave secreta segura

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')


# Configuración
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI', 'sqlite:///restaurants.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)






# Los modelos deben ser importados después de la inicialización de la base de datos
from models import Restaurant, Review, ImageUpload

# Rutas existentes...
@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    restaurants = Restaurant.query.all()
    images = ImageUpload.query.order_by(ImageUpload.upload_time.desc()).all()
    return render_template('index.html', restaurants=restaurants, images=images)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant == id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

# Nueva ruta para subir imágenes
@app.route('/upload', methods=['GET', 'POST'])
#@csrf.exempt  # Desactivar CSRF solo para esta ruta
def upload_image():
    if request.method == 'POST':
        # Verificar si hay un archivo en la solicitud
        if 'image_file' not in request.files:
            return "No file part", 400
        file = request.files['image_file']

        # Si no seleccionaron un archivo
        if file.filename == '':
            return "No selected file", 400

        if file and allowed_file(file.filename):
            # Asegurarse de que el nombre del archivo es seguro
            filename = secure_filename(file.filename)
            # Guardar el archivo en la carpeta uploads en la raíz del proyecto
            upload_folder = os.path.join(app.root_path, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Obtener la hora de la subida
            upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Registrar la subida de la imagen en la base de datos (si deseas hacerlo)
            image_record = ImageUpload(image_path=filename, upload_time=upload_time) 
            db.session.add(image_record)
            db.session.commit()

            return f"Image uploaded successfully! Uploaded at: {upload_time}"

    return render_template('upload_image.html')  # Página con el formulario de carga de imág

# Método para verificar que el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'uploads'), filename)

#@app.route('/health', methods=['GET'])
#def health_check():
    #return jsonify({"status": "healthy"}), 200


# Rutas adicionales y utilidades...

if __name__ == '__main__':
    app.run()
