import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from O365 import Account
import json
from config import client_id, client_secret

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# Load secret key from environment variable
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

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
from models import Restaurant, Review, Profile

# Microsoft OAuth Credentials
credentials = (client_id, client_secret)
scopes = ['Mail.ReadWrite', 'Mail.Send']

# Simple in-memory database for OAuth flow
class MyDB:
    def __init__(self):
        self.storage = {}

    def store_flow(self, flow):
        self.storage['flow'] = flow

    def get_flow(self):
        return self.storage.get('flow')

my_db = MyDB()

def serialize(flow):
    return json.dumps(flow)

def deserialize(flow_str):
    return json.loads(flow_str)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/creat')
def index():
    return render_template('add_profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        pass_word = request.form.get("pass_word")

        # Check if user exists in the database
        user = Profile.query.filter_by(first_name=first_name).first()

        if user and user.check_password(pass_word):  # Verify hashed password
            return "Login Successful!"
        else:
            return "Invalid username or password!"

    return render_template('log.html')  # Show login form for GET requests

@app.route('/stepone')
def auth_step_one():
    callback = url_for('auth_step_two_callback', _external=True).replace("127.0.0.1", "localhost")

    account = Account(credentials)
    url, flow = account.con.get_authorization_url(requested_scopes=scopes, redirect_uri=callback)

    my_db.store_flow(serialize(flow))  # Store flow for Step 2

    return redirect(url)

@app.route('/steptwo')
def auth_step_two_callback():
    account = Account(credentials)

    my_saved_flow_str = my_db.get_flow()
    if not my_saved_flow_str:
        return "Flow state not found. Restart authentication.", 400

    my_saved_flow = deserialize(my_saved_flow_str)

    requested_url = request.url  # Get current URL with auth code

    result = account.con.request_token(requested_url, flow=my_saved_flow)

    if result:
        return render_template('auth_complete.html')

    return "Authentication failed", 400

@app.route('/add', methods=["POST"])
def profile():
    first_name = request.form.get("first_name")
    pass_word = request.form.get("pass_word")

    if first_name and pass_word:
        p = Profile(first_name=first_name)
        p.set_password(pass_word)  # Hash password before storing
        db.session.add(p)
        db.session.commit()
        return redirect('/stepone')
    else:
        return redirect('/')

@app.route('/delete/<int:id>')
def erase(id):
    data = Profile.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
    return redirect('/')

@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant == id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add_restaurant', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()

        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        db.session.add(review)
        db.session.commit()

    return redirect(url_for('details', id=id))

@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.where(Review.restaurant == id)

        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                            'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()