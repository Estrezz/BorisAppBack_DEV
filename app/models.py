from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class Company(db.Model):
    store_id = db.Column(db.String(64), primary_key=True, index=True, unique=True)
    platform = db.Column(db.String(64), index=True)
    store_name = db.Column(db.String(64))
    admin_email = db.Column(db.String(120))
    param_logo = db.Column(db.String(120))
    param_fondo = db.Column(db.String(120))
    param_config = db.Column(db.String(120))
    contact_name = db.Column(db.String(64))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(120))
    correo_usado = db.Column(db.String(64))
    correo_apikey = db.Column(db.String(50))
    correo_id = db.Column(db.String(50))
    shipping_address = db.Column(db.String(64))
    shipping_number = db.Column(db.String(64))
    shipping_floor = db.Column(db.String(64))
    shipping_zipcode = db.Column(db.String(64))
    shipping_city = db.Column(db.String(64))
    shipping_province = db.Column(db.String(64))
    shipping_country = db.Column(db.String(64))
    shipping_info = db.Column(db.String(120))
    users = db.relationship('User', backref='empleado', lazy='dynamic')
    orders = db.relationship('Order', backref='pertenece', lazy='dynamic')

    def __repr__(self):
        return '<Company {} - {}>'.format(self.platform, self.store_name )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('company.store_id'))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Order(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, index=True)
    payment_method = db.Column(db.String(10))
    payment_card = db.Column(db.String(10))
    courier = db.Column(db.String(64))
    status = db.Column(db.String(15))
    sub_status = db.Column(db.String(15))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    products = db.relationship('Product', backref='articulos', lazy='dynamic')
    company_id = db.Column(db.Integer, db.ForeignKey('company.store_id'))

    def __repr__(self):
        return '<Order {} - {} - {}>'.format(self.id, self.creation_date, self.status)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(64))
    number = db.Column(db.String(10))
    floor = db.Column(db.String(10))
    zipcode = db.Column(db.String(8))
    locality = db.Column(db.String(64))
    city = db.Column(db.String(64))
    province = db.Column(db.String(64))
    country = db.Column(db.String(64))
    orders = db.relationship('Order', backref='buyer', lazy='dynamic')

    def __repr__(self):
        return '<Cliente {}>'.format(self.name) 


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    accion = db.Column(db.String(10))
    accion_cambiar_por = db.Column(db.Integer)
    accion_cantidad = db.Column(db.Integer)
    motivo = db.Column(db.String(50))
    monto_a_devolver = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

    def __repr__(self):
        return '<Product {}>'.format(self.name)
