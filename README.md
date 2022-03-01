# Deploy a Flask web app with PostgreSQL in Azure

This is a Python web app using the Flask framework and the Azure Database for PostgreSQL relational database service. The Flask app is hosted in a fully managed Azure App Service. This app is designed to be be run locally and then deployed to Azure. For more information on how to use this web app, see the tutorial [Deploy a Flask web app with PostgreSQL in Azure](TBD).

If you need an Azure account, you can [create on for free](https://azure.microsoft.com/en-us/free/).

Temporary instructions for running:

* clone
* specify .env variables based off of .env.example
* py -m venv .venv
* .venv\scripts\activate
* pip install -r requirements.txt
* flask db init and flask db migrate -m "first migration"  (roughly equivalent to django "python manage.py migrate")
* flask run (equivalent to django "python manage.py runserver")

To do:

* investigate /admin functionality with Flask-Admin
* handle 500 error in production
* move app.py to root folder to avoid need for startup.txt (command) and one less step, [details](https://docs.microsoft.com/en-us/azure/developer/python/tutorial-deploy-app-service-on-linux-04#flask-startup-commands)