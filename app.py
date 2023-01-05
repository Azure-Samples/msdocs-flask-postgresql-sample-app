from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from model import *
from dotenv import load_dotenv
import os
import bcrypt
import json
import pandas as pd
import openpyxl


app = Flask(__name__)

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR")
db = SQLAlchemy(app)

# Schema BDD
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
        
        
class ProduitsManquants(db.Model):
    __tablename__ = 'produitsManquants'
    id_magasin = db.Column(db.Integer,primary_key=True)
    id_article = db.Column(db.BigInteger,primary_key=True)
    name = db.Column(db.String())

    def __init__(self, id_magasin,id_article,name):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.name=name

class Utilisateur(db.Model):
    __tablename__ = 'utilisateur'
    id_magasin = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text)

    def __init__(self, id_user,password):
        self.id_magasin=id_user
        self.password=password


@app.route('/')
def hello():
    """
    

    Returns
    -------
    str
        DESCRIPTION.

    """
    return "Bienvenue sur l'API de Tickarbone: https://www.tickarbone.fr/"


# Fonctions non protegees
"""
@app.route('/temp')
def temp():
    return {"hello": "temp"}


@app.route('/insert')
def insert():
    prod = Produits(1,2, '128')
    db.session.add(prod)
    db.session.commit()
    return "done"

@app.route('/drop_all')
def drop():
    db.drop_all()
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
"""

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
    """
    
    
    Returns
    -------
    dict
        json with the products

    """
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


# recevoir un json et l'afficher
@app.route('/envoi_json',methods=['POST'])
def process_json():
    """
    
    Return a new  json with the id_magasin, id_product and carbone when given a json containing the id of the product
    
    Parameters
    ----------
    content_type: string
        type of the file (must be application/json)
    password : string
        password of the shop
    id_magasin : int
        id of the shop
    
    Returns
    -------
    Dict
        new json with carbon or error message

    """
    content_type = request.headers.get('Content-Type')
    id_magasin = request.headers.get('id_magasin')
    mdp= request.headers.get('password')   
    res = password(id_magasin,mdp)
    if res== True:
        if (content_type == 'application/json'):
            json_data = request.json

            # recupere la liste des produits du magasin (id_article + carbone)
            qry2 = db.engine.execute(f"select id_article,carbone from produits where id_magasin = {id_magasin}")
            qry_temp=list(qry2) # cree une copie car qry2 est un curseur
            
            qry3 = dict((x[0],x[1]) for x in list(qry_temp)) # cree un dictionnaire clé: id_article, valeur: carbone
            qry4=list(map(lambda x: (str(x[0])),list(qry_temp))) # cree une liste des id_articles

            new_json=[] # liste contenant la liste des produits à renvoyer
            for i in json_data['data']:
                if str(i["id_article"]) in qry4:
                    new_json.append({"id_article":i["id_article"],'carbone':qry3[i["id_article"]]})
                else:
                    #ajouter à la base des produits manquants
                    produitsManquants =  ProduitsManquants(id_magasin, i["id_article"],i["name"])
                    db.session.add(produitsManquants)
                    #prod_manquants.append({"id_magasin":id_magasin,"id_article":i["id_article"],"name":i["name"]})
            db.session.commit()
            return {"data":new_json}
        else:
            return 'Content-Type not supported!'
    else:
        return {"statut":"nom d'utilisateur ou mot de passe incorrect."}

@app.route('/index')
def index():
    """
    Endpoint to access the update page

    Returns
    -------
    Template index.html

    """
    return render_template('index.html')

@app.route('/excelupload',methods=['POST'])
def upload_file():
    """
    endpoint to sent the excel file for an update of the database

    Returns
    -------
    Template index.html
        .

    """
    file = request.files['file']
    update_or_insert_2(file,"(kgCO2/kgproduit)","Libellé","ID magasin","ID article")
    #colonne_carbone,colonne_name,colonne_id_magasin,colonne_id_produit
    
    qry=Produits.query.filter_by(id_magasin="7").all()
    return {'data': [
     {'id_article':record.id_article, 'id_magasin':
        record.id_magasin, 'name' :record.name,'carbone' :record.carbone}
    for record in qry
   ]}
    
    return render_template('index.html')



# Format envoi_json: curl -X POST -H "Content-type: application/json" -H "password: jaimelebio" -H "id_magasin: 1" -d "" "localhost:8080/envoi_json"
"""
@app.route('/test',methods=['POST'])
def test():
    json = request.data
    print(json)
    return str(json)
    #query=Produits.query.filter(Produits.id_article.in_(my_list)).all()
    #return str(query)
""" 


# Fonctions support
def password(id_magasin,password):
    """
    return true if the user is in the database and if the password is correct
    
    Parameters
    ----------
    id_magasin : int
        id of the shop
    password : string
        password of the shop

    Returns
    -------
    result : BOOL
        DESCRIPTION.

    """
    result=False
    mdp_encoded=password.encode('utf-8')
    if (bool(Utilisateur.query.where(Utilisateur.id_magasin==id_magasin).first())):
        qry = Utilisateur.query.where(Utilisateur.id_magasin==id_magasin).first()
        hashed=qry.password
        hashed=hashed.encode('utf-8')
        result = bcrypt.checkpw(mdp_encoded, hashed)
    return result
    

def update_or_insert_2(lien,colonne_carbone,colonne_name,colonne_id_magasin,colonne_id_produit):
    """
    insert in the database the information in an excel

    Parameters
    ----------
    lien : string
        link for the excel file
    colonne_carbone : string
        name of the carbon column in the excel
    colonne_name : string
        name of the name column in the excel
    colonne_id_magasin : string
        name of the magasin column in the excel
    colonne_id_produit : string
        name of the id product column

    Returns
    -------
    None.

    """
    df=pd.read_excel(lien,header=0, names=None, index_col=None, usecols=None)
    qry_magasin=Produits.query.all()
    for i in range(len(df)):
        flag=False
        for j in range(len(qry_magasin)):
            if df.iloc[i][colonne_id_produit] == qry_magasin[j].id_article and df.iloc[i][colonne_id_magasin] == qry_magasin[j].id_magasin :
                if df.iloc[i][colonne_carbone]!=qry_magasin[j].carbone and df.iloc[i][colonne_name]!=qry_magasin[j].name:
                    update_elem=Produits.query.filter_by(id_magasin=df.iloc[i][colonne_id_magasin],id_produit=df.iloc[i][colonne_id_produit])
                    update_elem.name=df.iloc[i][colonne_name]
                    update_elem.carbone=df.iloc[i][colonne_carbone]
                    db.session.commit()
                flag=True
                break
        if flag == False:
            print("passe")
            prod=Produits(int(df.iloc[i][colonne_id_magasin]),int(df.iloc[i][colonne_id_produit]),df.iloc[i][colonne_carbone],df.iloc[i][colonne_name])
            db.session.add(prod)
    db.session.commit()
    

if __name__ == '__main__':
    app.run(port=8080,debug=True)