import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_moment import Moment

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
class DatabaseURI:
    DATABASE_NAME = 'fyyurproject'
    username = 'postgres'
    password = 'yourpassword'
    url = 'localhost:5432'

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{DatabaseURI.username}:{DatabaseURI.password}@{DatabaseURI.url}/{DatabaseURI.DATABASE_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
