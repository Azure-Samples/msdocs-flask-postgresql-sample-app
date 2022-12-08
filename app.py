from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from model import *
from dotenv import load_dotenv
import os
import bcrypt

app = Flask(__name__)

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR")
db = SQLAlchemy(app)

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

db.create_all()
db.session.commit()

@app.route('/')
def hello():
    return {"hello": "world"}


@app.route('/temp')
def temp():
    return {"hello": "temp"}


@app.route('/insert')
def insert():
    prod = Magasins(1,2, '128')
    db.session.add(prod)
    db.session.commit()
    return "done"

@app.route('/select/all') 
def select():
    qry=Produits.query.all()
    return {'data': [
         {'id_produit':record.id_article, 'id_magasin':
            record.id_magasin, 'name' :record.name,'carbone' :record.carbone}
        for record in qry
       ]}


@app.route('/select/sans_protection',methods=['GET'])
def select_2():
    id_magasin=request.args.get('id_magasin')
    id_article=request.args.get('id_article')
    qry=Produits.query.filter_by(id_magasin=id_magasin).filter_by(id_article=id_article)
    return {'data': [
         {'id_article':record.id_article, 'id_magasin':
            record.id_magasin, 'name' :record.name,'carbone' :record.carbone}
        for record in qry
       ]}

#selectionne un produit
@app.route('/select/avec_protection',methods=['GET'])
def select_3():
    mdp=request.args.get('password')
    id_magasin=request.args.get('id_magasin')
    id_article=request.args.get('id_article')
    res = password(id_magasin,mdp)
    if res ==True:
        qry=Produits.query.filter_by(id_magasin=id_magasin).filter_by(id_article=id_article)
        print(qry)
        return {'data': [
         {'id_article':record.id_article, 'id_magasin':
            record.id_magasin, 'name' :record.name,'carbone' :record.carbone}
        for record in qry
       ]}
    else:
        return {"statut":"nom d'utilisateur ou mot de passe incorrect."}

# selectionner toute la base d'un magasin
@app.route('/select/magasin',methods=['GET'])
def select_4():
    mdp=request.args.get('password')
    id_magasin=request.args.get('id_magasin')
    res = password(id_magasin,mdp)
    if res ==True:
        qry=Produits.query.filter_by(id_magasin=id_magasin)
        print(qry)
        return {'data': [
         {'id_article':record.id_article, 'id_magasin':
            record.id_magasin, 'name' :record.name,'carbone' :record.carbone}
        for record in qry
       ]}
    else:
        return {"statut":"nom d'utilisateur ou mot de passe incorrect."}

@app.route('/drop_all')
def drop():
    db.drop_all()
    return "done"


# Fonctions support
def password(id_magasin,password):
    mdp_encoded=password.encode('utf-8')
    qry = Utilisateur.query.where(Utilisateur.id_magasin==id_magasin).first()
    hashed=qry.password
    hashed=hashed.encode('utf-8')
    result = bcrypt.checkpw(mdp_encoded, hashed)
    return result
    

if __name__ == '__main__':
    app.run(port=8080,debug=True)