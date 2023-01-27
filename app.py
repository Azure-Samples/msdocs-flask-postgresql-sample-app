from datetime import datetime
import os

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash


app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if not 'WEBSITE_HOSTNAME' in os.environ:
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
from models import Restaurant, Review, Customer

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    customers = Customer.query.all()    
    return render_template('index.html', customers=customers)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Customer.query.where(Customer.id == id).first()
    reviews = Review.query.where(Review.restaurant==id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_customer():
    print('Request for add restaurant page received')
    return render_template('create_customer.html')

@app.route('/add', methods=['POST'])
@csrf.exempt

def add_customer():
    try:
        first_name = request.values.get('first_name')
        last_name = request.values.get('last_name')
        email = request.values.get('email')
        password = request.values.get('password')
    except (KeyError):
        #Redisplay the form.
        return render_template('add_customer.html', {
            'error_message': "Error adding customer",
        })
    else:
        customer = Customer()
        customer.first_name = first_name
        customer.last_name = last_name
        customer.email = email
        customer.password = generate_password_hash(password)
        db.session.add(customer)
        db.session.commit()

        return redirect(url_for('details', id=customer.id))

def add_restaurant():
    try:
        name = request.values.get('first_name')
        street_address = request.values.get('last_name')
        description = request.values.get('email')
        description = request.values.get('password')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_restaurant.html', {
            'error_message': "You must include a customer name, address, and description",
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
        reviews = Review.query.where(Review.restaurant==id)

        ratings = []
        review_count = 0;        
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings)/len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
   app.run()
