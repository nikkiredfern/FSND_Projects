import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL - COMPLETED
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:S3V3nDW4rf$2809@localhost:5432/fyyurapp'
