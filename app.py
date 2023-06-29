import os
import csv
import openai
import psycopg2
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

@app.route('/livecheck', methods=['GET'])
def livecheck():
    return 'OK'

@app.route('/insertintodb', methods=['GET'])
def insertintodb():
    try:
        return InsertQnA("my question", null, "my answer")
    except:
        return 'An exception occurred'

@app.route('/qnainit', methods=['GET'])
def qnainit():
    try:
        return do_init()
    except:
        return 'An exception occurred'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def do_init():
    logs = "logs:"

    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_type = os.getenv("OPENAI_TYPE")
        openai.api_version = os.getenv("OPENAI_VERSION")
        
        with open('./data/qna.csv', newline='\r\n') as srccsvfile:
             datareader = csv.reader(srccsvfile, delimiter=';')
            
             with open('./embeddings/embeddings.csv', 'a', newline='\r\n') as dstcsvfile:
                 tmpwriter = csv.writer(dstcsvfile, delimiter=';', quotechar='', quoting=csv.QUOTE_NONE)
                 for row in datareader:
                     question = row[0]
                     answer = row[1]
                    
                     response = openai.Embedding.create(
                         input=question,
                         engine=os.getenv("OPENAI_DEPLOYMENT_EMBEDDING")
                     )
                     embeddings = response['data'][0]['embedding']
                     logs += '\r\n\r\n' + question + ' ' + embeddings
                     tmpwriter.writerow([question,answer,embeddings])
                     InsertQnA(question, embeddings, answer)
        return 'success' + logs
    except:
        return 'error again in qnainit'


def InsertQnA(question, embeddings, answer):
    if question is not None and answer is not None:
        conn = psycopg2.connect(user="ATeam", password="4t34m!", host="ateam-qna-server.postgres.database.azure.com", port=5432, database="qna-embeddings-db")
        cur = conn.cursor()
        print(conn)
        print(cur)
        if embeddings is not None:
            insert_query = "INSERT INTO qna.questionanswers(question, embedding, answer) VALUES ('{0}', '{1}', '{2}')".format(question,embeddings,answer)
        else:
            insert_query = "INSERT INTO qna.questionanswers(question, embedding, answer) VALUES ('{0}', NULL, '{2}')".format(question,answer)
        cur.execute(insert_query)
        conn.commit()
        return "ok"
    else:
        return "question or answer null"

if __name__ == '__main__':
    app.run()
