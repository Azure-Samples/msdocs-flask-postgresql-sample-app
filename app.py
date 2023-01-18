from flask import Flask, request, render_template, Response, make_response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import psycopg2
from model import *
from dotenv import load_dotenv
import os
import bcrypt
import json
import pandas as pd
import openpyxl
import io
from datetime import datetime


app = Flask(__name__,template_folder='templates')

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR")
db = SQLAlchemy(app)
scheduler = APScheduler()
scheduler.api_enabled = True

with app.app_context():
    scheduler.init_app(app)
    scheduler.start()


# Schema BDD
class Produits(db.Model):
    """
    Declaration of the table 'produits' that contained every products of the shop
    """
    __tablename__ = 'produits'
    id_magasin = db.Column(db.Integer,primary_key=True)
    id_article = db.Column(db.BigInteger,primary_key=True)
    carbone_kg = db.Column(db.String())
    carbone_unite = db.Column(db.String())
    name = db.Column(db.String())
    date= db.Column(db.String())

    def __init__(self, id_magasin,id_article, carbone_kg,name,date,carbone_unite):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.carbone_kg = carbone_kg
        self.carbone_unite=carbone_unite
        self.name=name
        self.date=date
        
        
class ProduitsManquants(db.Model):
    """
    Declaration of the table produitManquants that contained every products of the shop that are actually in the database
    """
    __tablename__ = 'produitsManquants'
    id_magasin = db.Column(db.Integer,primary_key=True)
    id_article = db.Column(db.BigInteger,primary_key=True)
    name = db.Column(db.String())
    date= db.Column(db.String())

    def __init__(self, id_magasin,id_article,name,date):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.name=name
        self.date=date

class Utilisateur(db.Model):
    """
    Declaration of the table Utilisateur that contained every shops that has accessed to our database
    """
    __tablename__ = 'utilisateur'
    id_magasin = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Text)

    def __init__(self, id_user,password):
        self.id_magasin=id_user
        self.password=password

with app.app_context():
    @scheduler.task('cron', #launch at regular time
                    id='maj_journaliere_prod_manquants',
                    week='*', 
                    day_of_week='mon-sun',
                    timezone="Europe/Paris",
                    hour=os.getenv("HOUR_DAILY_UPDATE"),
                    minute=os.getenv("MINUTE_DAILY_UPDATE"))
    def maj_produits_manquants():
        """
        Daily update of the database produitsManquants
    
        Returns
        -------
        None.
    
        """
        
        print("Launch maj produits manquants")
        qry_produits=db.engine.execute("select * from produits")
        prod_dict = dict(((x[0],x[1]),{"id_magasin":x[0],
                                       "id_article":x[1],
                                       "carbone_kg":x[2],
                                       "name":x[3],
                                       "date":x[4],
                                       "carbone_unite":x[5]}) for x in list(qry_produits))
        #qry_produits_manquants=db.engine.execute(f"select * from produitsManquants")
        #prod_manquants_dict = dict(((x[0],x[1]),{"id_magasin":x[0],"id_article":x[1],"carbone":x[2],"name":x[3]}) for x in list(qry_produits_manquants))
        qry_produits_manquants=ProduitsManquants.query.all()
        prod_manquants_dict={}
        for record in qry_produits_manquants:
            prod_manquants_dict[(record.id_magasin,record.id_article)]={"id_magasin":record.id_magasin,
                                                                        "id_article":record.id_article,
                                                                        "date":record.date,
                                                                        "name":record.name}
        for key in prod_dict:
            if key in prod_manquants_dict:
                if prod_dict[key]["carbone_kg"]!=None or prod_dict[key]["carbone_unite"]!=None:
                    ProduitsManquants.query.filter_by(id_magasin=prod_dict[key]["id_magasin"],
                                                      id_article=prod_dict[key]["id_article"]).delete()
            else:
                if prod_dict[key]["carbone_kg"]==None and prod_dict[key]["carbone_unite"]==None:
                    prod_temp=ProduitsManquants(prod_dict[key]["id_magasin"],
                                                prod_dict[key]["id_article"],
                                                prod_dict[key]["name"],
                                                str(datetime.now().strftime("%d/%m/%Y")))
                    db.session.add(prod_temp) 
        db.session.commit()



@app.route('/')
def hello():
    """
    Welcome message of the API

    Returns
    -------
    str
        DESCRIPTION.

    """
    return render_template("home.html")
    #return "Bienvenue sur l'API de Tickarbone: https://www.tickarbone.fr/"






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
    """
    Select a product of a shop given the password, id article and id of the shop
    ex: https://tickarbone.azurewebsites.net/select/avec_protection?id_magasin=1&password=jaimelebio&id_article=2220383
    
    Returns
    -------
    dict
        json with the product

    """
    
    mdp=request.args.get('password')
    id_magasin=request.args.get('id_magasin')
    id_article=request.args.get('id_article')
    res = password(id_magasin,mdp)
    
    if res ==True:
        qry=Produits.query.filter_by(id_magasin=id_magasin).filter_by(id_article=id_article)
        print(qry)
        return {'data': [
         {'id_article':record.id_article, 
          'id_magasin':record.id_magasin, 
          'name' :record.name,
          'carbone_kg' :record.carbone_kg,
          'carbone_unite' :record.carbone_unite,
          'date':record.date}
        for record in qry
       ]}
    else:
        return {"statut":"nom d'utilisateur ou mot de passe incorrect."}

# selectionner toute la base d'un magasin
@app.route('/select/magasin',methods=['GET'])
def select_4():
    """
    Select all the data of a shop given the password and id of the shop
    ex: https://tickarbone.azurewebsites.net/select/magasin?id_magasin=1&password=jaimelebio
    
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
         {'id_article':record.id_article, 
          'id_magasin':record.id_magasin, 
          'name' :record.name,
          'carbone_kg' :record.carbone_kg,
          'carbone_unite' :record.carbone_unite,
          'date':record.date}
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
    return_json={}
    # verification des types
    try:
        id_magasin=int(id_magasin)
    except (ValueError):
        return_json["statut"]="type de id_magasin incorrect, doit etre un int"
        return_json["data"]=[]
    try:
        mdp=str(mdp)
    except (ValueError):
        return_json["statut"]="type de mdp incorrect, doit etre un string"
        return_json["data"]=[]
    
    if id_magasin == None or mdp == None or content_type==None:
        return_json["statut"]="Vous avez une erreur dans votre header (orthographe des headers ou oubli d'un header ou valeur null dans l'un des headers)"
        return_json["data"]=[]        
    
    #verification du mdp dans la base de donnees
    res = password(id_magasin,mdp) # bool
    if res== True:
        if (content_type == 'application/json'):
            try:
                json_data = request.json
            except Exception as e:
                return_json["statut"]="Votre fichier json est incorrect."
                return_json["data"]=[]

            # recupere la liste des produits du magasin (id_article + carbone)
            qry2 = db.engine.execute(f"select id_article,carbone_kg,carbone_unite from produits where id_magasin = {id_magasin}")
            qry_temp=list(qry2) # cree une copie car qry2 est un curseur
            
            qry3 = dict((x[0],{"carbone_kg":x[1],"carbone_unite":x[2]}) for x in list(qry_temp)) # cree un dictionnaire clé: id_article, valeur: carbone
            qry4=list(map(lambda x: (str(x[0])),list(qry_temp))) # cree une liste des id_articles

            new_json=[] # liste contenant la liste des produits à renvoyer
            try:
                for i in json_data['data']:
                    if str(i["id_article"]) in qry4:
                        new_json.append({"id_article":i["id_article"],'carbone_kg':qry3[i["id_article"]]["carbone_kg"],'carbone_unite':qry3[i["id_article"]]["carbone_unite"]})
                    else:
                        # ajouter au json de retour
                        new_json.append({"id_article":i["id_article"],'carbone_kg':None,'carbone_unite':None})
                        # ajouter à la base des produits manquants et des produits
                        produitsManquants =  ProduitsManquants(int(id_magasin), int(i["id_article"]),str(i["name"]),str(datetime.now().strftime("%d/%m/%Y")))# cree l'element qu'on n a pas dans produits
                        db.session.add(produitsManquants) 
                        produits =  Produits(int(id_magasin), int(i["id_article"]),None,str(i["name"]),str(datetime.now().strftime("%d/%m/%Y")),None)# cree l'element qu'on n a pas dans produits manquants
                        db.session.add(produits) 
                db.session.commit()
                return_json["statut"]="ok"
                return_json["data"]=new_json
            except(KeyError):
                return_json["statut"]="Votre fichier json est incorrect: les cles du json ne sont pas compatibles avec le format necessaire à l'API tickarbone"
                return_json["data"]=[]
        else:
            return_json["statut"]="type de contenu non supporte."
            return_json["data"]=[]
    else:
        return_json["statut"]="nom d'utilisateur ou mot de passe incorrect."
        return_json["data"]=[]
    
    return return_json

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
    message=0 # message: 0:rien faire, 1:fichier uploade, 2:echec upload
    if request.files['file'].filename != '': # check if file doesn't exist
        file = request.files['file']
        try: # check if the file has a good format
            update_or_insert(file)  
            message=2
        except:
            message=1
    else:
        message=3        
    return render_template('index.html',message=message)



@app.route('/download_everything')
def download_everything():
    qry=Produits.query.all()
    df = pd.DataFrame()
    for record in qry:
        df1=pd.DataFrame({'id_article':record.id_article, 'id_magasin':record.id_magasin,'date':record.date, 'name' :record.name,'carbone_kg':record.carbone_kg,'carbone_unite':record.carbone_unite},index=[1])
        df=pd.concat([df,df1],ignore_index=True)
    
    # Creating output and writer (pandas excel writer)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')

   
    # Export data frame to excel
    df.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
    writer.save()

   
    # Flask create response 
    r = make_response(out.getvalue())

    
    # Defining correct excel headers
    date_actual=str(datetime.now().strftime("%d/%m/%Y")) #date of download
    r.headers["Content-Disposition"] = f"attachment; filename=tickarbone_database_{date_actual}.xlsx"
    r.headers["Content-type"] = "application/x-xls"

    
    # Finally return response
    return r



@app.route('/exceldownload')
def download_file(colonne_carbone_kg=os.getenv("CARBONE_KG"),
                  colonne_carbone_unite=os.getenv("CARBONE_UNITE"),
                  colonne_name=os.getenv("NAME"),
                  colonne_id_magasin=os.getenv("ID_MAGASIN"),
                  colonne_id_produit=os.getenv("ID_ARTICLE"),
                  colonne_date=os.getenv("DATE")):
    qry=ProduitsManquants.query.all()
    df = pd.DataFrame()
    for record in qry:
        df1=pd.DataFrame({colonne_id_produit:record.id_article,colonne_id_magasin :record.id_magasin,colonne_date:record.date, colonne_name :record.name,colonne_carbone_kg:None,colonne_carbone_unite:None},index=[1])
        df=pd.concat([df,df1],ignore_index=True)
    
    # Creating output and writer (pandas excel writer)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')

   
    # Export data frame to excel
    df.to_excel(excel_writer=writer, index=False, sheet_name='Page1')
    writer.save()

   
    # Flask create response 
    r = make_response(out.getvalue())

    
    # Defining correct excel headers
    date_actual=str(datetime.now().strftime("%d/%m/%Y")) #date of download
    r.headers["Content-Disposition"] = f"attachment; filename=produits_manquants_{date_actual}.xlsx"
    r.headers["Content-type"] = "application/x-xls"

    
    # Finally return response
    return r


@app.route('/user')
def user():
    return render_template('handleuser.html')


@app.route('/handle_user',methods=['POST'])
def handle_user_():
    # 0: base, 1: utilisateur a ete ajouté, 2: utilisateur n'existe pas, 3: fail, 4: utilisateur existe deja, 5: l'utilisateur a été supprime
    utilisateur = request.form.get('utilisateur')
    mdp = request.form.get('mdp')
    return_box=0
    existence_user=False
    
    if(bool(Utilisateur.query.filter_by(id_magasin=int(utilisateur)).first())):# check if user exists
        existence_user=True
    
    if mdp == None:
        if existence_user:
            Utilisateur.query.filter_by(id_magasin=int(utilisateur)).delete()
            return_box=5
        else:
            return_box=2   
    else:
        if existence_user:
            return_box=4
        else:
            hashed=create_hash(mdp)
            user=Utilisateur(int(utilisateur),hashed)
            db.session.add(user) 
            return_box=1
    db.session.commit()
    return render_template('handleuser.html',message=return_box)


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
    if (bool(Utilisateur.query.where(Utilisateur.id_magasin==id_magasin).first()) or type(id_magasin) is not int):
        qry = Utilisateur.query.where(Utilisateur.id_magasin==id_magasin).first()
        hashed=qry.password
        hashed=hashed.encode('utf-8')
        result = bcrypt.checkpw(mdp_encoded, hashed)
    return result
    


def update_or_insert(lien,colonne_carbone_kg=os.getenv("CARBONE_KG"),
                       colonne_carbone_unite=os.getenv("CARBONE_UNITE"),
                       colonne_name=os.getenv("NAME"),
                       colonne_id_magasin=os.getenv("ID_MAGASIN"),
                       colonne_id_produit=os.getenv("ID_ARTICLE"),
                       colonne_date=os.getenv("DATE")):
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
    qry_magasin=db.engine.execute(f"select * from produits")
    qry2 = dict(((x[0],x[1]),{colonne_id_magasin:x[0],
                              colonne_id_produit:x[1],
                              colonne_carbone_kg:x[2],
                              colonne_name:x[3],
                              colonne_date:x[4],
                              colonne_carbone_unite:x[5]}) for x in list(qry_magasin))
    for i in range(len(df)):
        key_id=(df.iloc[i][colonne_id_magasin],df.iloc[i][colonne_id_produit])
        if key_id in qry2:
            if str(df.iloc[i][colonne_carbone_kg])!=str(qry2[key_id][colonne_carbone_kg]) or str(df.iloc[i][colonne_name])!=str(qry2[key_id][colonne_name]) or str(df.iloc[i][colonne_carbone_unite])!=str(qry2[key_id][colonne_carbone_unite]) :
                update_elem=Produits.query.filter_by(id_magasin=int(df.iloc[i][colonne_id_magasin]),
                                                     id_article=int(df.iloc[i][colonne_id_produit])).first()
                update_elem.name=str(df.iloc[i][colonne_name])
                update_elem.carbone_unite=str(df.iloc[i][colonne_carbone_unite])
                update_elem.carbone_kg=str(df.iloc[i][colonne_carbone_kg])
                update_elem.date=str(datetime.now().strftime("%d/%m/%Y"))
                db.session.commit()
        else:
            prod=Produits(int(df.iloc[i][colonne_id_magasin]),
                          int(df.iloc[i][colonne_id_produit]),
                          str(df.iloc[i][colonne_carbone_kg]),
                          str(df.iloc[i][colonne_name]),
                          str(datetime.now().strftime("%d/%m/%Y")),
                          str(df.iloc[i][colonne_carbone_unite]))
            db.session.add(prod)
    db.session.commit()
    


def create_hash(mdp):
    mdp_encoded=mdp.encode('utf-8')
    salt=bcrypt.gensalt() # genere le sel
    hashed = bcrypt.hashpw(mdp_encoded, salt) # cree le mot de passe hashe
    return hashed.decode()
    
    



if __name__ == '__main__':
    app.run(port=8080,debug=False)