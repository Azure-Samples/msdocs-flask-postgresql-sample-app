import os, json
from datetime import datetime

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    jsonify,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.exc import IntegrityError



app = Flask(__name__, static_folder="static")
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if "WEBSITE_HOSTNAME" not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object("azureproject.development")
else:
    # production
    print("Loading config.production.")
    app.config.from_object("azureproject.production")

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get("DATABASE_URI"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Restaurant, Review, Lambda


# @app.route("/", methods=["GET"])
# def index():
#     print("Request for index page received")
#     restaurants = Restaurant.query.all()
#     return render_template("index.html", restaurants=restaurants)


# @app.route("/<int:id>", methods=["GET"])
# def details(id):
#     restaurant = Restaurant.query.where(Restaurant.id == id).first()
#     reviews = Review.query.where(Review.restaurant == id)
#     return render_template("details.html", restaurant=restaurant, reviews=reviews)


# @app.route("/create", methods=["GET"])
# def create_restaurant():
#     print("Request for add restaurant page received")
#     return render_template("create_restaurant.html")


# @app.route("/add", methods=["POST"])
# @csrf.exempt
# def add_restaurant():
#     try:
#         name = request.values.get("restaurant_name")
#         street_address = request.values.get("street_address")
#         description = request.values.get("description")
#     except KeyError:
#         # Redisplay the question voting form.
#         return render_template(
#             "add_restaurant.html",
#             {
#                 "error_message": "You must include a restaurant name, address, and description",
#             },
#         )
#     else:
#         restaurant = Restaurant()
#         restaurant.name = name
#         restaurant.street_address = street_address
#         restaurant.description = description
#         db.session.add(restaurant)
#         db.session.commit()

#         return redirect(url_for("details", id=restaurant.id))


# @app.route("/review/<int:id>", methods=["POST"])
# @csrf.exempt
# def add_review(id):
#     try:
#         user_name = request.values.get("user_name")
#         rating = request.values.get("rating")
#         review_text = request.values.get("review_text")
#     except KeyError:
#         # Redisplay the question voting form.
#         return render_template(
#             "add_review.html",
#             {
#                 "error_message": "Error adding review",
#             },
#         )
#     else:
#         review = Review()
#         review.restaurant = id
#         review.review_date = datetime.now()
#         review.user_name = user_name
#         review.rating = int(rating)
#         review.review_text = review_text
#         db.session.add(review)
#         db.session.commit()

#     return redirect(url_for("details", id=id))


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
#         return {
#             "avg_rating": avg_rating,
#             "review_count": review_count,
#             "stars_percent": stars_percent,
#         }

#     return dict(star_rating=star_rating)


# @app.route("/favicon.ico")
# def favicon():
#     return send_from_directory(
#         os.path.join(app.root_path, "static"),
#         "favicon.ico",
#         mimetype="image/vnd.microsoft.icon",
#     )


@app.route("/up")
@csrf.exempt
def test():
    return jsonify({"message": "Service is running..."})


@app.route("/", methods=["GET"])
@csrf.exempt
def get():
    if request.args.get("deviceId"):

        data = Lambda.query.filter(
            Lambda.device_id == request.args.get("deviceId")
        ).all()

    else:
        data = Lambda.query.all()

    # return jsonify(Lambda.query.first())
    objects_dict = [obj.__dict__ for obj in data]

    # Remove any internal keys added by SQLAlchemy
    for obj in objects_dict:
        obj.pop("_sa_instance_state", None)

    return jsonify(objects_dict)


# Define a route for the POST request
@app.route("/create", methods=["POST"])
@csrf.exempt
def post():
    # Check if the request contains JSON data
    if request.is_json:
        data = request.get_json()

        # Access specific fields from the JSON data
        device_id = data.get("deviceId")
        device_name = data.get("deviceName")
        water_detected = data.get("waterDetected", False)
        battery_level = data.get("batteryLevel")

        lambda_data_entry = Lambda(
            device_id=device_id,
            device_name=device_name,
            water_detected=water_detected,
            battery_level=battery_level,
        )

        db.session.add(lambda_data_entry)
        try:
            db.session.commit()

        except IntegrityError as err:
            return jsonify({"error": f"DeviceId {device_id} already exists"}), 409

        # Process the data (in this example, just echoing back the received data)
        response = {"message": f"Saved record for {device_id}"}

        # Return a JSON response
        return jsonify(response), 200
    else:
        # If the request does not contain JSON data, return an error response
        return jsonify({"error": "Invalid JSON"}), 400


@app.route("/update/<device_id>", methods=["PUT"])
@csrf.exempt
def put(device_id):
    if request.method == "PUT":
        data = request.get_json()
        device_name = data.get("deviceName")
        water_detected = data.get("waterDetected", False)
        battery_level = data.get("batteryLevel")

        if device_id is None:
            return jsonify({"error": "Value must be provided."}), 400

        lambda_entry = Lambda.query.get(device_id)

        if lambda_entry is None:
            return jsonify({"error": f"Device Id {device_id} does not exist"}), 400

        lambda_entry.water_detected = water_detected
        lambda_entry.battery_level = battery_level
        db.session.commit()

        return (
            jsonify(
                {"message": f"Data with device id {device_id} updated successfully."}
            ),
            200,
        )


if __name__ == "__main__":
    app.run()
