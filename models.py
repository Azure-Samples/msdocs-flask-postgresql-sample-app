from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import validates

from app import db


class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))
    def __str__(self):
        return self.name

class Customer(db.Model):
    id = Column(db.Integer, primary_key=True)
    first_name = Column(db.String(255), nullable=False)
    last_name = Column(db.String(255), nullable=False)
    email = Column(db.String(255), nullable=False)
    password = Column(db.String(255), nullable=False)
    created_at = Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return self.restaurant.name + " (" + self.review_date.strftime("%x") +")"
