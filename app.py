import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for,jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_security import login_required,login_user,logout_user,auth_required,current_user
from flask_security import Security,hash_password,verify_password
from flask_cors import CORS

from flask_restful import Api


app = Flask(__name__, static_folder='static')
# csrf = CSRFProtect(app)

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
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Appliance,Device,Users,user_datastore

#Security init
security = Security(app,user_datastore)
CORS(app)
app.app_context().push()

api= Api(app)
app.app_context().push()

from api import *
api.add_resource(UserApi,'/api/user/<string:username>','/api/user')
api.add_resource(DeviceApi,'/api/devices/<int:id>','/api/devices')
api.add_resource(LoginApi,'/api/login')
api.add_resource(ApplianceApi,'/api/log/<int:log_id>','/api/log')

@app.login_manager.unauthorized_handler
def unauth_handler():
    if request.is_json:
        return jsonify(message='Authorize please to access this page.'), 401
    else:
        return render_template('errors.html'), 401


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        uname=request.form.get('username')
        passd=request.form.get('password')
        try:
            user=Users.query.filter(Users.username==uname).first()
            if user==None:
                raise Exception("usernotfound")
        except Exception as e:
            print(e)
            return render_template('login.html',error='incorrect password or username')
        if verify_password(passd,user.password):
            login_user(user,True) #session login
            return index()
    else:
        return render_template('login.html')
#---------------------------
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        uname=request.form.get('username')
        passd=request.form.get('password')
        email=request.form.get('email')
        if uname not in [i.username for i in Users.query.all()] and email_valid(email):
            user_datastore.create_user(username=uname,email=email, password=hash_password(passd))
            db.session.commit()
            return login()
        return render_template('notfound.html',error="invalid email")
    return render_template('signup.html')

@app.route('/index', methods=['GET'])
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
