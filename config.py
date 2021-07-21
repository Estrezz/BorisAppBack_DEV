""" Este es el modulo de configuracion """
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """ Clas para configurar app """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['soporte@borisreturns.com']
    POSTS_PER_PAGE = int(os.environ.get('POST_PER_PAGE') or 20)
    FILES_PEDIDOS_URL = os.environ.get('FILES_PEDIDOS_URL')
    SERVER_ROLE = os.environ.get('SERVER_ROLE')

    CLIENT_ID_TN=os.environ.get('CLIENT_ID_TN')
    CLIENT_SECRET_TN=os.environ.get('CLIENT_SECRET_TN')
    