from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from model import *
from dotenv import load_dotenv
import os
import bcrypt

#http://localhost:5000/select/avec_protection?id_magasin=2&id_article=100764&password=test
#http://localhost:5000/select/magasin?id_magasin=2&password=test

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR")
db = SQLAlchemy(app)


db.create_all()
db.session.commit()

@app.route('/')
def hello():
    return {"hello": "world"}

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
    app.run(debug=True)