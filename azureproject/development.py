import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ['DBUSER'],
    dbpass=os.environ['DBPASS'],
    dbhost=os.environ['DBHOST'],
    dbname=os.environ['DBNAME']
)
SECRET_KEY =  "myappquantifie"
SECURITY_TOKEN_MAX_AGE=3600
SECURITY_UNAUTHORIZED_VIEW = None
SECURITY_USERNAME_ENABLE=True
SECURITY_TOKEN_AUTHENTICATION_HEADER="A-T"
SECURITY_PASSWORD_SALT='secret'
CORS_SUPPORTS_CREDENTIALS=True
CORS_EXPOSE_HEADERS='A-T'
WTF_CSRF_ENABLED = False
TIME_ZONE = 'UTC'

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_URL = 'static/'
