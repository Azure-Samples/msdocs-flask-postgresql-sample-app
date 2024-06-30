import os
from datetime import datetime
from http import HTTPStatus

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from urllib.error import HTTPError

from core import fetch_accounts, add_account

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
# db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
# migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
# from models import Restaurant, Review

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    #restaurants = Restaurant.query.all()
    return render_template('index.html')

# @app.route('/<int:id>', methods=['GET'])
# def details(id):
#     restaurant = Restaurant.query.where(Restaurant.id == id).first()
#     reviews = Review.query.where(Review.restaurant == id)
#     return render_template('details.html', restaurant=restaurant, reviews=reviews)

# @app.route('/create', methods=['POST'])
# @csrf.exempt
# def create_restaurant():
#     print('Request for add restaurant page received')
#     return render_template('create_restaurant.html')

# @app.route('/add', methods=['POST'])
# @csrf.exempt
# def add_restaurant():
#     try:
#         name = request.values.get('restaurant_name')
#         street_address = request.values.get('street_address')
#         description = request.values.get('description')
#     except (KeyError):
#         # Redisplay the question voting form.
#         return render_template('add_restaurant.html', {
#             'error_message': "You must include a restaurant name, address, and description",
#         })
#     else:
#         restaurant = Restaurant()
#         restaurant.name = name
#         restaurant.street_address = street_address
#         restaurant.description = description
#         db.session.add(restaurant)
#         db.session.commit()

#         return redirect(url_for('details', id=restaurant.id))


@app.route('/search', methods=['POST'])
@csrf.exempt
def search():
    account_ids = request.values.get('account_ids')
    return redirect(url_for('details', account_ids=account_ids))


@app.route('/add', methods=['POST'])
@csrf.exempt
def add():
    values = request.values
    try:
        account_type = values['account_type']
        account_number = values['account_number']
        depositor_1 = values['depositor_1']
        depositor_2 = values['depositor_2']
        try:
            amount = int(values['amount'])
        except ValueError:
            return _render_error_template(HTTPStatus.BAD_REQUEST, 'Invalid value found for amount. Please ensure it is integer value.')

        maturity_date = values['maturity_date']
        agent = values['agent']
        account_id = add_account(account_number, account_type, depositor_1, depositor_2, amount, maturity_date, agent)
        return redirect(url_for('details', account_ids=account_id))
    except KeyError:
        return _render_error_template(HTTPStatus.BAD_REQUEST, 'Please fill all required fields.')
    except ValueError as ve:
        return _render_error_template(HTTPStatus.BAD_REQUEST, ve.args[0])


@app.route('/details', methods=['GET'])
def details():
    joint_account_ids = request.args.get('account_ids')
    if joint_account_ids:
        try:
            account_ids = [int(id) for id in joint_account_ids.strip(',').split(',')]
            accounts = fetch_accounts(account_ids)
            return render_template('details.html', accounts=accounts)
        except ValueError:
            return _render_error_template(HTTPStatus.BAD_REQUEST, 'Invalid value received in list of account IDs.\nPlease ensure IDs are integer values. Multiple values must be comma separated.')
    else:
        return _render_error_template(HTTPStatus.BAD_REQUEST, 'You must include at least one account id or comma separated mutiple IDs. (E.g. - 1,2,3)')


def _render_error_template(category: HTTPStatus, message: str):
    error = {"category": category.phrase, "message": message}
    return render_template('error.html', error=error), category


# @app.route('/review/<int:id>', methods=['POST'])
# @csrf.exempt
# def add_review(id):
#     try:
#         user_name = request.values.get('user_name')
#         rating = request.values.get('rating')
#         review_text = request.values.get('review_text')
#     except (KeyError):
#         #Redisplay the question voting form.
#         return render_template('add_review.html', {
#             'error_message': "Error adding review",
#         })
#     else:
#         review = Review()
#         review.restaurant = id
#         review.review_date = datetime.now()
#         review.user_name = user_name
#         review.rating = int(rating)
#         review.review_text = review_text
#         db.session.add(review)
#         db.session.commit()

#     return redirect(url_for('details', id=id))

# @app.context_processor
# def utility_processor():
#     def star_rating(id):
#         reviews = Review.query.where(Review.restaurant == id)

#         ratings = []
#         review_count = 0
#         for review in reviews:
#             ratings += [review.rating]
#             review_count += 1

#         avg_rating = sum(ratings) / len(ratings) if ratings else 0
#         stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
#         return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

#     return dict(star_rating=star_rating)

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
