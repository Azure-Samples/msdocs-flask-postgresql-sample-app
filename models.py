from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import validates
from flask_security import UserMixin,RoleMixin,SQLAlchemyUserDatastore

from app import db

class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name

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
        return f"{self.user_name}: {self.review_date:%x}"


class User(db.Model):
    id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(20),nullable=False,unique=True)
    password=Column(String(20),nullable=False)
    email = Column(String(100), unique=True)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    admin= Column(Boolean,default=False)
