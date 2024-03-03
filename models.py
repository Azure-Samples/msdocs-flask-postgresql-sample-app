from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UUID, Boolean
from sqlalchemy.orm import validates

from app import db


class Restaurant(db.Model):
    __tablename__ = "restaurant"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name


class Review(db.Model):
    __tablename__ = "review"
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey("restaurant.id", ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates("rating")
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"


class Lambda(db.Model):
    __tablename__ = "lambda"
    device_id = Column(UUID, primary_key=True)
    device_name = Column(String(255))
    water_detected = Column(Boolean)
    battery_level = Column(Integer)
