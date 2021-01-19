from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class Company(db.Model):
    store_id = db.Column(db.String(64), primary_key=True, index=True)
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
    orders = db.relationship('Order_header', backref='pertenece', lazy='dynamic')

    def __repr__(self):
        return '<Company {} - {}>'.format(self.platform, self.store_name )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    store = db.Column(db.Integer, db.ForeignKey('company.store_id'))
    transaction = db.relationship('Transaction_log', backref='realizo', lazy='dynamic')
    
    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.store)

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


class Order_header(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, index=True)
    order_id_anterior = db.Column(db.Integer)
    creation_date = db.Column(db.String(35), index=True)
    last_update_date = db.Column(db.String(35))
    payment_method = db.Column(db.String(10))
    payment_card = db.Column(db.String(10))
    courier_order_id = db.Column(db.String(64), index=True)
    status = db.Column(db.String(15))
    sub_status = db.Column(db.String(15))
    customer_address = db.Column(db.String(64))
    customer_number = db.Column(db.String(10))
    customer_floor = db.Column(db.String(10))
    customer_zipcode = db.Column(db.String(8))
    customer_locality = db.Column(db.String(64))
    customer_city = db.Column(db.String(64))
    customer_province = db.Column(db.String(64))
    customer_country = db.Column(db.String(64))
    detalle = db.relationship('Order_detail', backref='productos', lazy='dynamic')
    transaction = db.relationship('Transaction_log', backref='transaccion', lazy='dynamic')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    store = db.Column(db.Integer, db.ForeignKey('company.store_id'))

    def __repr__(self):
        return '<Order {} - {} - {}>'.format(self.order_number, self.creation_date, self.status)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(15))
    orders = db.relationship('Order_header', backref='buyer', lazy='dynamic')

    def __repr__(self):
        return '<Cliente {}>'.format(self.name) 


class Order_detail(db.Model):
    order_line_number = db.Column(db.String, primary_key=True)
    line_number = db.Column(db.Integer)
    prod_id = db.Column(db.Integer)
    name = db.Column(db.String(120))
    variant = db.Column(db.Integer)
    accion = db.Column(db.String(10))
    accion_cambiar_por = db.Column(db.Integer)
    accion_cantidad = db.Column(db.Integer)
    motivo = db.Column(db.String(50))
    monto_a_devolver = db.Column(db.Float)
    gestionado = db.Column(db.String(10))
    order = db.Column(db.Integer, db.ForeignKey('order_header.id'))

    def __repr__(self):
        return '<Order_Detail {} {} {}>'.format(self.order_line_number, self.line_number, self.prod_id, self.name)


class Transaction_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_status = db.Column(db.String(15))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(64))
    order_id = db.Column(db.Integer, db.ForeignKey('order_header.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))