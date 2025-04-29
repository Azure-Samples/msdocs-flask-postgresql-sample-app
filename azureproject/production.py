import os

# Configuración de la URI de la base de datos para producción
DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.getenv('AZURE_POSTGRESQL_USER'),
    dbpass=os.getenv('AZURE_POSTGRESQL_PASSWORD'),
    dbhost=os.getenv('AZURE_POSTGRESQL_HOST'),
    dbname=os.getenv('AZURE_POSTGRESQL_NAME')
)
# hola
# Otras configuraciones específicas del entorno de producción
DEBUG = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
