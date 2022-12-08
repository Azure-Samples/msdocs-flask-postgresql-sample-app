from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import validates
"""
from app import db

class Produits(db.Model):
    __tablename__ = 'produits'
    id_magasin = db.Column(db.Integer,primary_key=True)
    id_article = db.Column(db.BigInteger,primary_key=True)
    carbone = db.Column(db.String())
    name = db.Column(db.String())

    def __init__(self, id_magasin,id_article, carbone,name):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.carbone = carbone
        self.name=name

class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'
    id_magasin = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text)

    def __init__(self, id_user,password):
        self.id_magasin=id_user
        self.password=password
"""