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


load_dotenv() #import les variables d'environnement

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

    id = Column(Integer, primary_key=True,autoincrement=True)
    id_magasin = Column(Integer)
    id_article = Column(BigInteger)
    carbone = Column(String())
    name = Column(String())

    def __init__(self,id_magasin, id_article, carbone,name):
        self.id_magasin=id_magasin
        self.id_article=id_article
        self.carbone = carbone
        self.name=name

    def __repr__(self):
        return f"<Produit {self.id, self.id_magasin, self.id_article, self.name, self.carbone}>"
    
class Utilisateur(Base):
    __tablename__ = 'utilisateur'

    id = Column(Integer, primary_key=True,autoincrement=True)
    id_magasin = Column(Integer)
    password = Column(Text)

    def __init__(self, id_magasin,password):
        self.id_magasin=id_magasin
        self.password=password
    
    def __repr__(self):
        return f"<Utilisateur {self.id, self.id_magasin, self.password}>"

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

# select data
def select_user():
    print(s.query(Utilisateur).all())

def select_data():
    print(s.query(Produits).all())
    
# fonctions supports
def read_database_temp(lien):
    db=pd.read_excel(lien,header=0, names=None, index_col=None, usecols=None)
    print(db.iloc[0].keys())
    print(db.iloc[0]["ID article"])
    
if __name__ == "__main__":
    """
    drop_database()
    init_database()
    load_database("./database/tickarbase-v0.1.xlsx")
    insert_user(1,"tom55")
    select_user()
    select_data()
    """
    update_produit_test()








































































    
    
    
    