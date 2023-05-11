import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Appliance,Device,Users

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    devices = Device.query.all()
    return render_template('index.html', devices=devices)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    device = Device.query.where(Device.id == id).first()
    appliances = Appliance.query.where(Appliance.device == id)
    return render_template('details.html', device=device, appliances=appliances)

@app.route('/create', methods=['GET'])
def create_device():
    print('Request for add device page received')
    return render_template('create_device.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_device():
    try:
        id = request.values.get('unique_id')
        name = request.values.get('device_name')
        location = request.values.get('device_location')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_device.html', {
            'error_message': "You must include a device name, address, and description",
        })
    else:
        device = Device()
        device.name = name
        device.location = location
        device.id = id
        db.session.add(device)
        db.session.commit()

        return redirect(url_for('details', id=device.id))

@app.route('/appliance/<int:id>', methods=['POST'])
@csrf.exempt
def add_appliance(id):
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        appliance_text = request.values.get('appliance_text')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_appliance.html', {
            'error_message': "Error adding appliance",
        })
    else:
        appliance = Appliance()
        appliance.device = id
        appliance.appliance_date = datetime.now()
        appliance.user_name = user_name
        appliance.rating = int(rating)
        appliance.appliance_text = appliance_text
        db.session.add(appliance)
        db.session.commit()

    return redirect(url_for('details', id=id))

@app.context_processor
def utility_processor():
    def star_rating(id):
        appliances = Appliance.query.where(Appliance.device == id)

        ratings = []
        appliance_count = 0
        for appliance in appliances:
            ratings += [appliance.rating]
            appliance_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if appliance_count > 0 else 0
        return {'avg_rating': avg_rating, 'appliance_count': appliance_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
