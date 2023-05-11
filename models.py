from sqlalchemy import Column, DateTime, ForeignKey, Integer,Float, String, Boolean
from sqlalchemy.orm import validates
from flask_security import UserMixin,RoleMixin,SQLAlchemyUserDatastore

from app import db


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

roles_users = db.Table('roles_users',
        Column('user_id', Integer(), ForeignKey('users.id')),
        Column('role_id', Integer(), ForeignKey('role.id')))

class Appliance(db.Model):
    __tablename__="appliance"
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(8), nullable=False)
    type = Column(String(10), nullable=False)
    value= Column(Float,nullable=True)
    device_id= Column(Integer, ForeignKey('device.id'),nullable=False)

class Device(db.Model):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    name = Column(String(8), unique=True, nullable=False)
    location = Column(String(50))
    user_id= Column(Integer, ForeignKey('users.id'),nullable=False)
    device_appliance= db.relationship('Appliance', backref='device', lazy=True)
    def __str__(self):
        return self.name

class Users(db.Model, UserMixin):
    __tablename__='users'
    id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(20),nullable=False,unique=True)
    password=Column(String(100),nullable=False)
    email = Column(String(100), unique=True)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    user_devices= db.relationship('Device', backref='user', lazy=True)
    admin= Column(Boolean,default=False)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users_role', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db,Users,Role)

