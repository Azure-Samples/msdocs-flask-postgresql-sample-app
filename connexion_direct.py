import pyodbc
import sqlalchemy as sal
from sqlalchemy import create_engine, MetaData, update
from sqlalchemy.orm.session import sessionmaker,Session
from sqlalchemy.orm import relationship
from sqlalchemy import (Column, Integer, String, ForeignKey, BigInteger, Text)
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import os
from dotenv import load_dotenv
import bcrypt


load_dotenv() #import des variables d'environnement

# Definition de l'engine
engine = create_engine("postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR"))

# Classe de base du modele
Base = declarative_base(engine)

# Create the Metadata Object
metadata_obj = MetaData(bind=engine)
MetaData.reflect(metadata_obj)

conn = engine.connect()
Session = sessionmaker(bind=engine)
s = Session()


# classes representant les tables
class Produits(Base):
    __tablename__ = 'produits'
    id_magasin = Column(Integer, primary_key=True)
    id_article = Column(BigInteger, primary_key=True)
    carbone = Column(String())
    name = Column(String())

    def __init__(self,id_magasin, id_article, carbone,name):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.carbone = carbone
        self.name=name

    def __repr__(self):
        return f"<Produit {self.id_magasin, self.id_article, self.name, self.carbone}>"
    
class Utilisateur(Base):
    __tablename__ = 'utilisateur'
    id_magasin = Column(Integer, primary_key=True)
    password = Column(Text)

    def __init__(self, id_magasin,password):
        self.id_magasin=id_magasin
        self.password=password
    
    def __repr__(self):
        return f"<Utilisateur {self.id_magasin, self.password}>"


class ProduitsManquants(Base):
    __tablename__ = 'produitsManquants'
    id_magasin = Column(Integer,primary_key=True)
    id_article = Column(BigInteger,primary_key=True)
    name = Column(String())

    def __init__(self, id_magasin,id_article,name):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.name=name

    def __repr__(self):
        return f"<ProduitsManquants {self.id_magasin, self.id_article, self.name}>"
    
    

# Fonction creation et destruction des bases
def drop_database():
    Base.metadata.drop_all(bind=engine)
    
def init_database():
    Base.metadata.create_all(bind=engine)


def printTableName():
    print(metadata_obj.tables.keys())


# Fonction gestion des produits
def load_database(lien):
    db=pd.read_excel(lien,header=0, names=None, index_col=None, usecols=None)
    id_magasin=db.iloc[0]["ID magasin"]
    k=1
    products_to_insert=[]
    for i in range(len(db)):
        if db.iloc[i]["ID magasin"]!= id_magasin:
            k+=1
            id_magasin=db.iloc[i]["ID magasin"]
        products_to_insert.append(Produits(int(k),int(db.iloc[i]["ID article"]),db.iloc[i]["(kgCO2/kgproduit)"],db.iloc[i]["Libellé"]))
    s.bulk_save_objects(products_to_insert)
    s.commit()
    
def update_produit_test():
    """
    Ex update
    
    upd = update(tablename)
    val = upd.values({"column_name":"value"})
    cond = val.where(tablename.c.column_name == value)
    
    ex:
    # Get the `books` table from the Metadata object
    BOOKS = meta.tables['books']
     
    # update
    u = update(BOOKS)
    u = u.values({"book_name": "2022 future ahead"})
    u = u.where(BOOKS.c.book_id == 3)
    engine.execute(u)
    
    OU
    
    stmt = BOOKS.update().where(BOOKS.c.genre == 'non-fiction'
                           ).values(genre = 'sci-fi')
    engine.execute(stmt)
    """
    PRODUITS=metadata_obj.tables["produits"]
    stmt= PRODUITS.update().where(PRODUITS.c.id_article==3760213050052 and PRODUITS.c.carbone==None).values(carbone='100')
    engine.execute(stmt)

def update_or_insert(lien,id_magasin):
    db=pd.read_excel(lien,header=0, names=None, index_col=None, usecols=None)
    qry_exist = s.query(Produits).filter_by(id_magasin=id_magasin).count()
    if qry_exist==0:
        products_to_insert=[]
        for i in range(len(db)):
            products_to_insert.append(Produits(int(id_magasin),int(db.iloc[i]["ID article"]),db.iloc[i]["(kgCO2/kgproduit)"],db.iloc[i]["Libellé"]))
        s.bulk_save_objects(products_to_insert)
    else:
        qry_magasin=s.query(Produits).filter_by(id_magasin=id_magasin).all()
        for i in range(len(db)):
            flag=False
            for j in range(len(qry_magasin)):
                if db.iloc[i]["ID article"] == qry_magasin[j].id_article:
                    PRODUITS=metadata_obj.tables["produits"]
                    stmt= PRODUITS.update().where(PRODUITS.c.id_article==int(db.iloc[i]["ID article"])).values(carbone=db.iloc[i]["(kgCO2/kgproduit)"])
                    engine.execute(stmt)
                    flag=True
            if flag == False:
                prod=Produits(int(id_magasin),int(db.iloc[i]["ID article"]),db.iloc[i]["(kgCO2/kgproduit)"],db.iloc[i]["Libellé"])
                s.add(prod)
    s.commit()
    
      
def query_test():
    id_magasin=3
    qry_magasin=s.query(Produits).filter_by(id_magasin=id_magasin).all()
    print(qry_magasin[0])
    print(qry_magasin[0].id_article)
    

# Fonctions gestion des utilisateurs
def create_hash(mdp):
    mdp_encoded=mdp.encode('utf-8')
    salt=bcrypt.gensalt() # genere le sel
    hashed = bcrypt.hashpw(mdp_encoded, salt) # cree le mot de passe hashe
    return hashed.decode()
    
def check_user(mdp,hashed):
    mdp_encode = mdp.encode('utf-8') # encode le mot de passe
    return bcrypt.checkpw(mdp_encode, hashed) # verifie le mot de passe
    
def insert_user(utilisateur,mdp):
    hashed=create_hash(mdp)
    print(hashed)
    user=Utilisateur(utilisateur,hashed)
    s.add(user)
    s.commit()

def delete_user(utilisateur):
    user=s.query(Utilisateur).where(Utilisateur.id_magasin==utilisateur)
    s.delete(user)
    s.commit()
    
def update_user_mdp(utilisateur,nouveau_mdp):
    UTILISATEUR=metadata_obj.tables["utilisateur"]
    hashed=create_hash(nouveau_mdp)
    stmt= UTILISATEUR.update().where(UTILISATEUR.c.id_magasin==utilisateur).values(password=hashed)
    engine.execute(stmt)

def update_or_insert_2(lien,colonne_carbone,colonne_name,colonne_id_magasin,colonne_id_produit):

    # Definition de l'engine
    engine = create_engine("postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR"))

    # Classe de base du modele
    Base = declarative_base(engine)

    # Create the Metadata Object
    metadata_obj = MetaData(bind=engine)
    MetaData.reflect(metadata_obj)

    conn = engine.connect()
    Session = sessionmaker(bind=engine)
    s = Session()

    db=pd.read_excel(lien,header=0, names=None, index_col=None, usecols=None)
    #qry_exist = s.query(Produits).filter_by(id_magasin=id_magasin).count()
    #id_all_magasin = list(db[colonne_id_magasin]).unique()
    qry_magasin=s.query(Produits).all()
    for i in range(len(db)):
        flag=False
        for j in range(len(qry_magasin)):
            if db.iloc[i][colonne_id_produit] == qry_magasin[j].id_article and db.iloc[i][colonne_id_magasin] == qry_magasin[j].id_magasin :
                PRODUITS=metadata_obj.tables["produits"]
                stmt= PRODUITS.update().where(PRODUITS.c.id_article==int(db.iloc[i][colonne_id_produit])).values(carbone=db.iloc[i][colonne_carbone])
                engine.execute(stmt)
                flag=True
                break
        if flag == False:
            print("passe")
            prod=Produits(int(db.iloc[i][colonne_id_magasin]),int(db.iloc[i][colonne_id_produit]),db.iloc[i][colonne_carbone],db.iloc[i][colonne_name])
            s.add(prod)
    s.commit()
    
def insert_produits_manquants_test():
    engine = create_engine("postgresql+psycopg2://" + os.getenv("UTILISATEUR")+":"+os.getenv("MDP")+"@"+os.getenv("SERVEUR"))

    # Classe de base du modele
    Base = declarative_base(engine)

    # Create the Metadata Object
    metadata_obj = MetaData(bind=engine)
    MetaData.reflect(metadata_obj)

    conn = engine.connect()
    Session = sessionmaker(bind=engine)
    s = Session()
    for i in range(10):
        prod=ProduitsManquants(1,i,"name_"+str(i))
        s.add(prod)
    s.commit()

# select data
def select_user():
    print(s.query(Utilisateur).all())

def select_data():
    print(s.query(Produits).all())
    
def select_prod_manquants():
    print(s.query(ProduitsManquants).all())
    
# fonctions supports
def read_database_temp(lien):
    db=pd.read_excel(lien,header=0, names=None, index_col=None, usecols=None)
    print(db.iloc[0].keys())
    
    
if __name__ == "__main__":
    """
    drop_database()
    init_database()
    load_database("./database/tickarbase-v0.1.xlsx")
    insert_produits_manquants_test()
    insert_user(1,"jaimelebio")
    insert_user(2,"laviesaine")
    insert_user(3,"lavieclaire")
    insert_user(4,"cbiocbon")
    
    select_user()
    select_data()
    update_produit_test()
    
    query_test()
    
    drop_database()
    init_database()
    insert_user(1,"test")
    insert_user(2,"test")
    insert_user(3,"test")
    
    #update_or_insert("./database/tickarbase-v0.1_test3.xlsx",2)
    
    select_prod_manquants()
    """
    select_user()




































































    
    
    
    