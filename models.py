from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates
from datetime import datetime

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



class ImageData(db.Model):
    __tablename__ = 'image_data'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    pixel_red = Column(String, nullable=False)     # Ej: "1234"
    pixel_green = Column(String, nullable=False)   # Ej: "5678"
    pixel_blue = Column(String, nullable=False)    # Ej: "9101"
    username = Column(String(100), nullable=False)
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<ImageData {self.filename} by {self.username} at {self.upload_time}>"