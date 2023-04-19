from flask import Flask, request, render_template, Response, make_response, current_app, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
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
import asyncio



app = Flask(__name__,template_folder='templates')

load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR")
app.secret_key = 'super secret key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)




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

    conditionnement=db.Column(db.String)
    nom_fournisseur=db.Column(db.String)
    code_barres=db.Column(db.String)
    origine=db.Column(db.String)
    plus_commander=db.Column(db.String)

    def __init__(self, 
                 id_magasin,
                 id_article, 
                 carbone_kg,
                 name,
                 date,
                 carbone_unite,
                 conditionnement,
                 nom_fournisseur,
                 code_barres,
                 origine,
                 plus_commander
                 ):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.carbone_kg = carbone_kg
        self.carbone_unite=carbone_unite
        self.name=name
        self.date=date
        self.conditionnement=conditionnement
        self.nom_fournisseur=nom_fournisseur
        self.code_barres=code_barres
        self.origine=origine
        self.plus_commander=plus_commander

        
        
class ProduitsManquants(db.Model):
    """
    Declaration of the table produitManquants that contained every products of the shop that are actually in the database
    """
    __tablename__ = 'produits_manquants'
    id_magasin = db.Column(db.Integer,primary_key=True)
    id_article = db.Column(db.BigInteger,primary_key=True)
    name = db.Column(db.String())
    date= db.Column(db.String())

    conditionnement=db.Column(db.String)
    nom_fournisseur=db.Column(db.String)
    code_barres=db.Column(db.String)
    origine=db.Column(db.String)
    plus_commander=db.Column(db.String)

    def __init__(self, 
                 id_magasin,
                 id_article,
                 name,
                 date,
                 conditionnement,
                 nom_fournisseur,
                 code_barres,
                 origine,
                 plus_commander):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.name=name
        self.date=date
        self.conditionnement=conditionnement
        self.nom_fournisseur=nom_fournisseur
        self.code_barres=code_barres
        self.origine=origine
        self.plus_commander=plus_commander

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


class User_website(UserMixin,db.Model):
    """
    Declaration of the table User_website that contained every user that has accessed to our website
    """
    __tablename__ = 'utilisateur_web'
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    status=db.Column(db.String(1000))# status of the user
    
    
    def __init__(self, email,password,name,status):
        self.email=email
        self.password=password
        self.name=name
        self.status=status
        


@app.route('/drop_all')
def drop_all():
    db.drop_all()
    
@app.route('/create_all')
def create_all():
    db.create_all()

@app.route('/')
def home():
    """
    Welcome page of the API

    Returns
    -------
    str
        DESCRIPTION.

    """
    db.create_all() #in case of table dropping
    return render_template("login.html")
    #return "Bienvenue sur l'API de Tickarbone: https://www.tickarbone.fr/"


@app.route('/home')
def welcome():
    """
    Home page of the API

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    return render_template("home.html")

@login_manager.user_loader
def load_user(user_id):
    """
    Return the query containing the information of the user

    Parameters
    ----------
    user_id : TYPE
        id of the user

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User_website.query.get(int(user_id))

@app.route('/login')
def login():
    """
    Return the login.html page

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return render_template('login.html')




@app.route('/login', methods=['POST'])
def login_post():
    """
    If the email and password are ok give access to home else return login.html

    Returns
    -------
    None.

    """
    
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    user_table_exist=User_website.query.all()
    if len(user_table_exist)==0: # create the user if the base is empty
        new_user = User_website(email=email, name="admin", password=create_hash(password),status="admin")
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
    
    user = User_website.query.filter_by(email=email).first()
    
    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not password_user_website(user.password, password): 
        print("passe")
        flash('Please check your login details and try again.')
        return render_template("login.html") # if the user doesn't exist or password is wrong, reload the page
    
    
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return render_template("home.html")

@app.route('/logout')
def logout():
    """
    Logout the user from the website

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    logout_user()
    return render_template("login.html")


@app.route('/add_user_website')
@login_required
def add_user():
    """
    Return the user to the page ass_user_website.html

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return render_template('add_user_website.html')

@app.route('/add_user_website',methods=['POST'])
@login_required
def add_user_post():
    """
    Add user to the website

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    status=request.form.get('status')
    email_adder=request.form.get('adder_email')
    password_adder=request.form.get('adder_password')
    print("status",status)
    message=None
    # message: 0: L'utilisateur existe deja, 1 : Votre identifiant ou mot de passe est incorrect, 2: Votre statut est incorrect, 3: L'utilisateur a bien été créé.

    user = User_website.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        message=0
        print("passe1")
        return render_template('add_user_website.html',message=message)

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    admin=User_website.query.filter_by(email=email_adder).first()
    print("ap",admin.password)
    if admin==False or password_user_website(admin.password,password_adder)==False:
        message=1
        print("passe2")
        return render_template('add_user_website.html',message=message)
    print("as",admin.status)  
    if admin.status=="admin":
        new_user = User_website(email=email, name=name, password=create_hash(password),status=status)
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        print("passe3")
    else:
        message=2
        print("passe4")
        return render_template('add_user_website.html',message=message)
    message=3
    print("passe5")
    return render_template('add_user_website.html',message=message)


@app.route('/delete_user_website',methods=['POST'])
@login_required
def del_user_post():
    """
    Delete user of the website

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    email_adder=request.form.get('adder_email')
    password_adder=request.form.get('adder_password')
    email = request.form.get('email')
    
    
    
    # message: 4: L'utilisateur n'existe pas, 1 : Votre identifiant ou mot de passe est incorrect, 2: Votre statut est incorrect, 7: L'utilisateur a bien été supprimé.
    
    
    user = User_website.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if user == False: # if a user is not found, we want to redirect back to signup page so user can try again
        message=4    
        return render_template('add_user_website.html',message=message)

        
    admin=User_website.query.filter_by(email=email_adder).first()
    if admin==False or password_user_website(admin.password,password_adder)==False:
        message=1
        return render_template('add_user_website.html',message=message)
        
    
    if admin.status=="admin":
        # delete the user in the database
        User_website.query.filter_by(email=email).delete()
        db.session.commit()
    else:
        message=2
        return render_template('add_user_website.html',message=message)
    
    message=5
    return render_template('add_user_website.html',message=message)
    
    
    return render_template('add_user_website.html')
    
    


def password_user_website(user_password,password):
    """
    Evaluate if the user password and the password of the database are the same

    Parameters
    ----------
    user_password : TYPE
        DESCRIPTION.
    password : TYPE
        DESCRIPTION.

    Returns
    -------
    result : bool
    """
    result=False
    print(user_password)
    print(password)
    password_encoded=password.encode('utf-8')
    hashed=user_password
    hashed=hashed.encode('utf-8')
    result = bcrypt.checkpw(password_encoded, hashed)
    return result




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
            {
            'id_article':record.id_article, 
            'id_magasin':record.id_magasin, 
            'name' :record.name,
            'carbone_kg' :record.carbone_kg,
            'carbone_unite' :record.carbone_unite,
            'date':record.date,
            'conditionnement':record.conditionnement,
            'nom_fournisseur':record.nom_fournisseur,
            'code_barres':record.code_barres,
            'origine':record.origine,
            'plus_commander':record.plus_commander
            }
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
          'date':record.date,
          'conditionnement':record.conditionnement,
          'nom_fournisseur':record.nom_fournisseur,
          'code_barres':record.code_barres,
          'origine':record.origine,
          'plus_commander':record.plus_commander}
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
            qry2=None
            with db.engine.connect() as conn:
                qry2 = conn.execute(f"select id_article,carbone_kg,carbone_unite from produits where id_magasin = {id_magasin}")
            #qry2 = db.engine.execute(f"select id_article,carbone_kg,carbone_unite from produits where id_magasin = {id_magasin}")
            qry_temp=list(qry2) # cree une copie car qry2 est un curseur
            
            qry3 = dict((x[0],{"carbone_kg":x[1],"carbone_unite":x[2]}) for x in list(qry_temp)) # cree un dictionnaire clé: id_article, valeur: carbone
            qry4=list(map(lambda x: (str(x[0])),list(qry_temp))) # cree une liste des id_articles

            new_json=[] # liste contenant la liste des produits à renvoyer
            try:

                produit_manquant_exist=ProduitsManquants.query.all()
                if len(produit_manquant_exist)==0: # create the user if the base is empty
                    new_pm = ProduitsManquants(0,0, "creation table", str(datetime.now().strftime("%Y-%m-%d")),None,None,None,None,None)
                    # add the new user to the database
                    db.session.add(new_pm)
                    db.session.commit()

                bdd_produitsManquants=pd.read_sql(sql="select * from produits_manquants",con=db.engine)
                for i in json_data['data']:
                    if str(i["id_article"]) in qry4:
                        new_json.append({"id_article":i["id_article"],'carbone_kg':qry3[i["id_article"]]["carbone_kg"],'carbone_unite':qry3[i["id_article"]]["carbone_unite"]})
                    else:
                        # ajouter au json de retour
                        new_json.append({"id_article":i["id_article"],'carbone_kg':None,'carbone_unite':None})
                        # ajouter à la base des produits manquants et des produits
                        produits =  Produits(int(id_magasin), 
                                                int(i["id_article"]),
                                                None,
                                                str(i["name"]),
                                                str(datetime.now().strftime("%Y-%m-%d")),
                                                None,
                                                str(i["conditionnement"]),
                                                str(i["nom_fournisseur"]),
                                                str(i["code_barres"]),
                                                str(i["origine"]),
                                                str(i["plus_commander"]))
                        # cree l'element qu'on n a pas dans produits manquants
                        db.session.add(produits) 
                        db.session.commit()

                        dict_temp={"id_magasin":int(id_magasin),
                                    "id_article": int(i["id_article"]),
                                    "name":str(i["name"]),
                                    "date":str(datetime.now().strftime("%Y-%m-%d")),
                                    "conditionnement":str(i["conditionnement"]),
                                    "nom_fournisseur":str(i["nom_fournisseur"]),
                                    "code_barres":str(i["code_barres"]),
                                    "origine":str(i["origine"]),
                                    "plus_commander":str(i["plus_commander"])
                                    }
                        bdd_produitsManquants=bdd_produitsManquants.append(dict_temp, ignore_index=True)
                        
                bdd_produitsManquants.to_sql(name="produits_manquants",con=db.engine,if_exists="replace",index=False)   
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
@login_required
def index():
    """
    Endpoint to access the update page

    Returns
    -------
    Template index.html

    """
    return render_template('index.html')





@app.route('/download_everything')
@login_required
def download_everything():
    """
    Download all the product database

    Returns
    -------
    r : TYPE
        DESCRIPTION.

    """
    
    
    df=pd.read_sql(sql="select * from produits",con=db.engine)
    
    # Creating output and writer (pandas excel writer)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='openpyxl')

   
    # Export data frame to excel
    df.to_excel(excel_writer=writer, index=False, sheet_name='Sheet1')
    #writer.save()
    writer.close()
   
    # Flask create response 
    r = make_response(out.getvalue())

    
    # Defining correct excel headers
    date_actual=str(datetime.now().strftime("%d/%m/%Y")) #date of download
    r.headers["Content-Disposition"] = f"attachment; filename=tickarbone_database_{date_actual}.xlsx"
    r.headers["Content-type"] = "application/x-xls"

    
    # Finally return response
    return r



@app.route('/exceldownload')
@login_required
def download_file(colonne_carbone_kg=os.getenv("CARBONE_KG"),
                  colonne_carbone_unite=os.getenv("CARBONE_UNITE"),
                  colonne_name=os.getenv("NAME"),
                  colonne_id_magasin=os.getenv("ID_MAGASIN"),
                  colonne_id_produit=os.getenv("ID_ARTICLE"),
                  colonne_date=os.getenv("DATE")):
    """
    Download all the muissing product database
    
    Parameters
    ----------
    colonne_carbone_kg : TYPE, optional
        DESCRIPTION. The default is os.getenv("CARBONE_KG").
    colonne_carbone_unite : TYPE, optional
        DESCRIPTION. The default is os.getenv("CARBONE_UNITE").
    colonne_name : TYPE, optional
        DESCRIPTION. The default is os.getenv("NAME").
    colonne_id_magasin : TYPE, optional
        DESCRIPTION. The default is os.getenv("ID_MAGASIN").
    colonne_id_produit : TYPE, optional
        DESCRIPTION. The default is os.getenv("ID_ARTICLE").
    colonne_date : TYPE, optional
        DESCRIPTION. The default is os.getenv("DATE").

    Returns
    -------
    r : TYPE
        DESCRIPTION.

    """

    try:
        df=pd.read_sql(sql="select * from produits_manquants",con=db.engine)
        print("passe ici2")
    except:
        print("passe ici3")
        df = pd.DataFrame(columns=["id_article","id_magasin","date","name","carbone_kg","carbone_unite","conditionnement","nom_fournisseur","code_barres","origine","plus_commander"],index=None)
        
        
    
    # Creating output and writer (pandas excel writer)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='openpyxl')

   
    # Export data frame to excel
    df.to_excel(excel_writer=writer, index=False, sheet_name='Page1')
    #writer.save()
    writer.close()

   
    # Flask create response 
    r = make_response(out.getvalue())

    
    # Defining correct excel headers
    date_actual=str(datetime.now().strftime("%d/%m/%Y")) #date of download
    r.headers["Content-Disposition"] = f"attachment; filename=produits_manquants_{date_actual}.xlsx"
    r.headers["Content-type"] = "application/x-xls"

    
    # Finally return response
    return r


@app.route('/user')
@login_required
def user():
    """
    Render the template handleuser.html

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return render_template('handleuser.html')


@app.route('/handle_user',methods=['POST'])
@login_required
def handle_user_():
    """
    Render the template handleuser.html and send a message if a modification has been done with this page

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
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
    
def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

    

 
    
@app.route('/excelupload',methods=['POST'])
@login_required
def upload_file():
    
    """
    endpoint to sent the excel file for an update of the database

    Returns
    -------
    Template index.html
        

    """
    message=0 # message: 0:rien faire, 2:fichier uploade, 1:echec upload
    if request.files['file'].filename != '': # check if file doesn't exist
        file = request.files['file']
        df=pd.read_excel(file,header=0, names=None, index_col=None, usecols=None)
        df["date"]=pd.Timestamp.today().strftime("%d/%m/%Y")
        qry_sql=pd.read_sql(sql="select * from produits",con=db.engine) # base magasin
        
        if len(qry_sql)==0:
            print("passe1")
            qry_sql = pd.DataFrame(columns=["id_article","id_magasin","date","name","carbone_kg","carbone_unite","conditionnement","nom_fournisseur","code_barres","origine","plus_commander"],index=None) # mettre colonne dans le bon ordre
        if ((len(qry_sql.columns.difference(df.columns))==0) and (len(df.columns.difference(qry_sql.columns))==0)):
            try: # check if the file has a good format
                print("passe2")
                df_append=pd.concat([qry_sql,df],axis=0,ignore_index=True)
                df_reduced=df_append.drop_duplicates(subset=["id_article","id_magasin"],keep="last")
                df_reduced.to_sql(name="produits",con=db.engine,if_exists="replace",index=False)            
                task_maj_produits_manquants()
                message=2
            except:
                print("passe3")
                message=1
        else:
           message=1
    else:
        message=3
    return render_template('index.html',message=message)

    

    
    
    
    
@app.route('/test',methods=['GET'])
@login_required
def test():
    print(db.engine.table_names())
    db.engine.execute("drop table if exists produits")
    db.engine.execute("drop table if exists produits_manquants")
    db.create_all()
    return {"statut":"done"}
     
   
def task_maj_produits_manquants():
    """
    Update of the database produitsManquants

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
                                   "carbone_unite":x[5],
                                   "conditionnement":x[6],
                                   "nom_fournisseur":x[7],
                                   "code_barres":x[8],
                                   "origine":x[9],
                                   "plus_commander":x[10]}) for x in list(qry_produits))
    #qry_produits_manquants=db.engine.execute(f"select * from produitsManquants")
    #prod_manquants_dict = dict(((x[0],x[1]),{"id_magasin":x[0],"id_article":x[1],"carbone":x[2],"name":x[3]}) for x in list(qry_produits_manquants))
    qry_produits_manquants=ProduitsManquants.query.all()
    prod_manquants_dict={}
    for record in qry_produits_manquants:
        prod_manquants_dict[(record.id_magasin,record.id_article)]={"id_magasin":record.id_magasin,
                                                                    "id_article":record.id_article,
                                                                    "date":record.date,
                                                                    "name":record.name,
                                                                    "conditionnement":record.conditionnement,
                                                                    "nom_fournisseur":record.nom_fournisseur,
                                                                    "code_barres":record.code_barres,
                                                                    "origine":record.origine,
                                                                    "plus_commander":record.plus_commander}
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
                                            str(datetime.now().strftime("%Y-%m-%d")),
                                            prod_dict[key]["conditionnement"],
                                            prod_dict[key]["nom_fournisseur"],
                                            prod_dict[key]["code_barres"],
                                            prod_dict[key]["origine"],
                                            prod_dict[key]["plus_commander"],)
                db.session.add(prod_temp) 
    db.session.commit()

def create_hash(mdp):
    """
    Return the hash equivalent of the password

    Parameters
    ----------
    mdp : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    mdp_encoded=mdp.encode('utf-8')
    salt=bcrypt.gensalt() # genere le sel
    hashed = bcrypt.hashpw(mdp_encoded, salt) # cree le mot de passe hashe
    return hashed.decode()
    
    



if __name__ == '__main__':
    app.run(port=8080,debug=False)