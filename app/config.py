import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuration base de données
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'taskmanager'
    DB_USER = os.environ.get('DB_USER') or 'taskmanager'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'password'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    
    # URL de connexion PostgreSQL
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration AWS
    AWS_REGION = os.environ.get('AWS_REGION') or 'eu-west-1'
    S3_BUCKET = os.environ.get('S3_BUCKET') or 'taskmanager-static-assets'
    
    # Configuration de l'environnement
    ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'dev'
    DEBUG = ENVIRONMENT == 'dev'