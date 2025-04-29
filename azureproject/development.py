import os

# Configuración de la URI de la base de datos para desarrollo
DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ.get('DBUSER', 'dev_user'),
    dbpass=os.environ.get('DBPASS', 'dev_password'),
    dbhost=os.environ.get('DBHOST', 'localhost'),
    dbname=os.environ.get('DBNAME', 'dev_db')
)

# Otras configuraciones específicas del entorno de desarrollo
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
