import os
from dotenv import load_dotenv

load_dotenv()   # loads .env from the project root automatically

class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME      = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD      = os.environ.get('ADMIN_PASSWORD') or 'admin'
    MAIL_SERVER         = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT           = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS        = True
