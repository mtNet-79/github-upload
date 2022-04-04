# import pprint
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
# Enable debug mode.
DEBUG = True
# change to name of your database; add path if necessary
db_name = 'fyyurapp'
# Connect to the database
# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:AudrinaB12@localhost:5432/'+db_name
SQLALCHEMY_TRACK_MODIFICATIONS = False

