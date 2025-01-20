import os

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.getenv('AZURE_POSTGRESQL_USER'),
    dbpass=os.getenv('AZURE_POSTGRESQL_PASSWORD'),
    dbhost=os.getenv('AZURE_POSTGRESQL_HOST'),
    dbname=os.getenv('AZURE_POSTGRESQL_NAME')
)