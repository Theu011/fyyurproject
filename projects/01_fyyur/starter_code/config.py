import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


# Connect to the database
class DatabaseURI:
    DATABASE_NAME = 'fyyurproject'
    username = 'postgres'
    password = 'rockstar01'
    url = 'localhost:5432'

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{DatabaseURI.username}:{DatabaseURI.password}@{DatabaseURI.url}/{DatabaseURI.DATABASE_NAME}'
