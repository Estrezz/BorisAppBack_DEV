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
    platform_token_type = db.Column(db.String(30))
    platform_access_token = db.Column(db.String(64))
    store_name = db.Column(db.String(120))
    store_main_language = db.Column(db.String(20))
    store_main_currency = db.Column(db.String(20))
    store_country = db.Column(db.String(20))
    store_url = db.Column(db.String(120))
    store_plan = db.Column(db.String(64))
    store_phone = db.Column(db.String(30))
    store_address= db.Column(db.String(120))
    store_idfiscal = db.Column(db.String(20))
    admin_email = db.Column(db.String(120))
    communication_email = db.Column(db.String(120))
    communication_email_name = db.Column(db.String(120))
    param_logo = db.Column(db.String(200))
    param_fondo = db.Column(db.String(120))
    param_config = db.Column(db.String(120))
    contact_name = db.Column(db.String(64))
    contact_phone = db.Column(db.String(15))
    contact_email = db.Column(db.String(120))
    correo_usado = db.Column(db.String(64))
    correo_apikey = db.Column(db.String(50))
    correo_id = db.Column(db.String(50))
    correo_test = db.Column(db.Boolean)
    correo_cost = db.Column(db.String(15))
    stock_vuelve_config = db.Column(db.Boolean)
    correo_apikey_test = db.Column(db.String(50))
    correo_id_test = db.Column(db.String(50))
    shipping_address = db.Column(db.String(64))
    shipping_number = db.Column(db.String(64))
    shipping_floor = db.Column(db.String(64))
    shipping_zipcode = db.Column(db.String(64))
    shipping_city = db.Column(db.String(64))
    shipping_province = db.Column(db.String(64))
    shipping_country = db.Column(db.String(64))
    shipping_info = db.Column(db.String(120))
    aprobado_note = db.Column(db.String(2000))
    rechazado_note = db.Column(db.String(2000))
    envio_manual_note = db.Column(db.String(2000))
    envio_coordinar_note = db.Column(db.String(2000))
    envio_correo_note = db.Column(db.String(2000))
    cupon_generado_note = db.Column(db.String(2000))
    finalizado_note = db.Column(db.String(2000))
    confirma_manual_note = db.Column(db.String(2000))
    confirma_coordinar_note = db.Column(db.String(2000))
    confirma_domicilio_note = db.Column(db.String(2000))
    #### confirma_retiro_note se utilizaba para Moova
    confirma_retiro_note = db.Column(db.String(2000))
    
    ### Asuntos para mails
    orden_solicitada_asunto = db.Column(db.String(120))
    orden_iniciada_asunto = db.Column(db.String(120))
    orden_confirmada_asunto = db.Column(db.String(120))
    orden_rechazada_asunto = db.Column(db.String(120))
    orden_aprobada_asunto = db.Column(db.String(120))
    cupon_generado_asunto = db.Column(db.String(120))
    orden_finalizada_asunto = db.Column(db.String(120))

    ### Habilita o no el envío de mails en cada caso
    orden_solicitada_habilitado = db.Column(db.Boolean)
    orden_iniciada_habilitado = db.Column(db.Boolean)
    orden_confirmada_habilitado = db.Column(db.Boolean)
    orden_rechazada_habilitado = db.Column(db.Boolean)
    orden_aprobada_habilitado = db.Column(db.Boolean)
    cupon_generado_habilitado = db.Column(db.Boolean)
    orden_finalizada_habilitado = db.Column(db.Boolean)

    encuesta = db.Column(db.Boolean)
    habilitado = db.Column(db.Boolean)
    pagos = db.Column(db.Boolean)
    
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    demo_store = db.Column(db.Boolean)
    rubro_tienda = db.Column(db.String(64))
    plan_boris = db.Column(db.String(64))
    users = db.relationship('User', backref='empleado', lazy='dynamic')
    categories_filter = db.relationship('categories_filter', backref='filtroCategorias', lazy='dynamic')
    orders = db.relationship('Order_header', backref='pertenece', lazy='dynamic')

    def __repr__(self):
        return '<Company {} - {}>'.format(self.platform, self.store_name )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    identification = db.Column(db.String(64), index=True) 
    email = db.Column(db.String(120), index=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'))
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
            # algorithm='HS256').decode('utf-8')
            algorithm='HS256')

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
    order_id_anterior = db.Column(db.String(150))
    date_creation = db.Column(db.DateTime)
    date_closed = db.Column(db.DateTime)
    date_lastupdate = db.Column(db.DateTime)
    gastos_cupon = db.Column(db.Float)
    salientes = db.Column(db.String(10))
    gastos_gateway = db.Column(db.Float)
    gastos_shipping_owner = db.Column(db.Float)
    gastos_shipping_customer = db.Column(db.Float)
    gastos_promocion = db.Column(db.Float)
    payment_method = db.Column(db.String(35))
    payment_card = db.Column(db.String(35))
    courier_method = db.Column(db.String(64))
    metodo_envio_correo = db.Column(db.String(64))
    metodo_envio_guia = db.Column(db.String(64), index=True)
    metodo_envio_sucursal = db.Column(db.String(200))
    etiqueta_generada = db.Column(db.Boolean)
    courier_precio = db.Column(db.String(20))
    reembolsado = db.Column(db.Boolean)
    reembolso_metodo = db.Column(db.String(20))
    #### quitar
    # courier_coordinar_empresa es reemplazado por metodo_envio_correo
    # courier_coordinar_guia es reemplazado por metodo_envio_guia
    courier_coordinar_empresa = db.Column(db.String(120))
    courier_coordinar_guia = db.Column(db.String(250))
    #########
    courier_coordinar_roundtrip = db.Column(db.Boolean)
    nuevo_envio =  db.Column(db.String(100))
    nuevo_envio_costo =  db.Column(db.Float, default=0)
    nuevo_envio_total =  db.Column(db.Float, default=0)
    status = db.Column(db.String(25))
    sub_status = db.Column(db.String(25))
    status_resumen = db.Column(db.String(25))
    reject_reason = db.Column(db.String(350))
    customer_address = db.Column(db.String(250))
    customer_number = db.Column(db.String(50))
    customer_floor = db.Column(db.String(250))
    customer_zipcode = db.Column(db.String(8))
    customer_locality = db.Column(db.String(250))
    customer_city = db.Column(db.String(64))
    customer_province = db.Column(db.String(64))
    customer_country = db.Column(db.String(64))
    note = db.Column(db.Text)
    detalle = db.relationship('Order_detail', backref='productos', lazy='dynamic')
    transaction = db.relationship('Transaction_log', backref='transaccion', lazy='dynamic')
    customer_id = db.Column(db.String(150), db.ForeignKey('customer.id'))
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'))

    def __repr__(self):
        return '<Order {} - {} - {}>'.format(self.order_number, self.date_creation, self.status)


class Customer(db.Model):
    id = db.Column(db.String(150), primary_key=True)
    platform = db.Column(db.String(64), index=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True)
    identification = db.Column(db.String(20))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order_header', backref='buyer', lazy='dynamic')

    def __repr__(self):
        return '<Cliente {}>'.format(self.name) 


class Order_detail(db.Model):
    order_line_number = db.Column(db.String(150), primary_key=True)
    line_number = db.Column(db.Integer)
    prod_id = db.Column(db.String(64))
    name = db.Column(db.String(200))
    variant = db.Column(db.String(64))
    accion = db.Column(db.String(10))
    accion_cambiar_por = db.Column(db.String(64))
    accion_cambiar_por_prod_id = db.Column(db.String(64))
    accion_cambiar_por_desc = db.Column(db.String(120))
    accion_cantidad = db.Column(db.Integer)
    motivo = db.Column(db.String(50))
    monto_a_devolver = db.Column(db.Float)
    monto_devuelto = db.Column(db.Float, default=0)
    nuevo_envio =  db.Column(db.String(100))
    restock =  db.Column(db.String(30))
    precio = db.Column(db.Float)
    alto = db.Column(db.Float)
    largo = db.Column(db.Float)
    profundidad = db.Column(db.Float)
    peso = db.Column(db.Float)
    promo_descuento = db.Column(db.Float)
    promo_nombre = db.Column(db.String(120))
    promo_precio_final = db.Column(db.Float)
    gestionado = db.Column(db.String(10))
    fecha_gestionado = db.Column(db.DateTime)
    observaciones = db.Column(db.Text)
    order = db.Column(db.Integer, db.ForeignKey('order_header.id'))

    def __repr__(self):
        return '<Order_Detail {} {} {}>'.format(self.order_line_number, self.line_number, self.prod_id, self.name)


class Transaction_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sub_status = db.Column(db.String(15))
    status_client = db.Column(db.String(25))
    prod = db.Column(db.String(200))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(64))
    order_id = db.Column(db.Integer, db.ForeignKey('order_header.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class  categories_filter(db.Model):
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'), primary_key=True)
    category_id = db.Column(db.Integer, primary_key=True)
    category_desc = db.Column(db.String(100))

    def __repr__(self):
        return '<Categoria {} {} >'.format(self.category_id, self.category_desc)


class  CONF_motivos(db.Model):
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'), primary_key=True)
    id_motivo = db.Column(db.Integer, primary_key=True)
    motivo = db.Column(db.String(35))
    tipo_motivo = db.Column(db.String(35))

    def __repr__(self):
        return '<Motivo {} {} >'.format(self.store, self.motivo, self.tipo_motivo)


class  CONF_boris(db.Model):
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'), primary_key=True)
    ventana_cambios = db.Column(db.Integer)
    ventana_devolucion = db.Column(db.Integer)
    cambio_otra_cosa = db.Column(db.Boolean)
    cambio_cupon = db.Column(db.Boolean)
    observaciones = db.Column(db.Boolean)
    cambio_opcion = db.Column(db.String(200))
    cambio_opcion_cupon = db.Column(db.String(150))
    cambio_opcion_otra_cosa = db.Column(db.String(150))
    portal_empresa = db.Column(db.String(150))
    portal_titulo = db.Column(db.String(250))
    portal_texto = db.Column(db.String(250))
    

    def __repr__(self):
        return '<configuracion {} {} >'.format(self.store, self.ventana_cambios, self.ventana_devolucion)


class metodos_envios(db.Model):
    metodo_envio_id = db.Column(db.String(20), primary_key=True)
    metodo_envio_descripcion = db.Column(db.String(200))
    carrier = db.Column(db.Boolean) # Necesita un correo?
    sucursales = db.Column(db.Boolean) # Necesita elegir una sucursal ?
    direccion_obligatoria = db.Column(db.Boolean) # Exige poner al usuario una direccion?
    ### ver si es necesario tambien agregar opcion roundtrip
    icon = db.Column(db.String(50))

    def __repr__(self):
        return '<Metodo Envio {} {} >'.format(self.metodo_envio_id, self.metodo_envio_descripcion)


class correos(db.Model):
    correo_id = db.Column(db.String(15), primary_key=True)
    correo_descripcion = db.Column(db.String(150))
    correo_mail = db.Column(db.String(120))
def __repr__(self):
        return '<Correo {} {} >'.format(self.correo_id, self.correo_descripcion)


class CONF_correo(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'))
    correo_id = db.Column(db.String(15), db.ForeignKey('correos.correo_id'))
    cliente_apikey = db.Column(db.String(100))
    cliente_id = db.Column(db.String(50))
    user = db.Column(db.String(50))
    passw = db.Column(db.String(50))
    habilitado = db.Column(db.Boolean)

    def __repr__(self):
        return '<Correo {} {} >'.format(self.store, self.correo_id)


class CONF_metodos_envios(db.Model):
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'), primary_key=True)
    metodo_envio_id = db.Column(db.String(20), db.ForeignKey('metodos_envios.metodo_envio_id'), primary_key=True)
    habilitado = db.Column(db.Boolean)
    titulo_boton = db.Column(db.String(150))
    descripcion_boton = db.Column(db.String(350))
    correo_id = db.Column(db.String(10))
    correo_descripcion = db.Column(db.String(150))
    correo_servicio = db.Column(db.String(50))
    correo_sucursal = db.Column(db.String(50))
    costo_envio = db.Column(db.String(15))
    instrucciones_entrega = db.Column(db.Text)
    #### agregado para saber si cotizar con Retiro + Entrega
    roundtrip = db.Column(db.Boolean)
    ### quitar
    icon = db.Column(db.String(50))
    # origen_valido = provincia (ver si es tabla aparte)
    # accion = cambio/devolucion/ambas
    
    def __repr__(self):
        return '<Envio {} {} >'.format(self.store, self.metodo_envio_id, self.habilitado)

####### Esta tabla sirve solo para migrar del modelo anterior al nuevo
####### durante la actualziacion para integrar con correos, despues sacar
class  CONF_envios(db.Model):
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'), primary_key=True)
    metodo_envio = db.Column(db.String(200), primary_key=True)
    habilitado = db.Column(db.Boolean)
    titulo_boton = db.Column(db.String(150))
    descripcion_boton = db.Column(db.String(350))

    def __repr__(self):
        return '<Envio {} {} >'.format(self.store, self.metodo_envio, self.habilitado)


class Codigos_postales(db.Model):
    cp = db.Column(db.String(4), primary_key=True)
    partido	= db.Column(db.String(40))
    localidad = db.Column(db.String(40))
    barrio = db.Column(db.String(40))
    cordon = db.Column(db.String(40))
    provincia = db.Column(db.String(40))

    def __repr__(self):
        return '<Codigo {} {}>'.format(self.cp, self.provincia)

class  Sucursales(db.Model):
    sucursal_id = db.Column(db.String(200), primary_key=True)
    store = db.Column(db.String(64), db.ForeignKey('company.store_id'))
    metodo_envio_id = db.Column(db.String(20), db.ForeignKey('metodos_envios.metodo_envio_id'))
    sucursal_name = db.Column(db.String(350))
    sucursal_direccion = db.Column(db.String(350))
    sucursal_localidad = db.Column(db.String(250))
    sucursal_ciudad = db.Column(db.String(64))
    sucursal_provincia = db.Column(db.String(64))
    sucursal_pais = db.Column(db.String(64))
    sucursal_observaciones = db.Column(db.String(350))

    def __repr__(self):
        return '<Sucursal {} {} {} {} >'.format(self.sucursal_id, self.sucursal_name, self.store, self.metodo_envio_id)

