import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

# Configure Postgres database based on connection string of the libpq Keyword/Value form
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=conn_str_params['user'],
    dbpass=conn_str_params['password'],
    dbhost=conn_str_params['host'],
    dbname=conn_str_params['dbname']
)
SECRET_KEY =  "myenvision"
SECURITY_TOKEN_MAX_AGE=3600
SECURITY_UNAUTHORIZED_VIEW = None
SECURITY_USERNAME_ENABLE=True
SECURITY_TOKEN_AUTHENTICATION_HEADER="A-T"
SECURITY_PASSWORD_SALT='secret'
CORS_SUPPORTS_CREDENTIALS=True
CORS_EXPOSE_HEADERS='A-T'
