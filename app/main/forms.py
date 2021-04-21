from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    store = StringField('Store_id', validators=[DataRequired()])

    #store_name = StringField('Nombre de la tienda')
    #admin_email = StringField('Email de Administración')
    #param_logo = StringField('Ruta para el Logo')
    #param_fondo = StringField('Ruta para el fondo')
    #param_config = StringField('Ruta para el archivo de configuración')
    #contact_name = StringField('Nombre del contacto')
    #contact_phone = StringField('Telefono del contacto')
    #contact_email = StringField('Email del contacto')
    #correo_usado = StringField('Empresa de correo utilizada')
    #correo_apikey = StringField('API KEY de la empresa de correo')
    #correo_id = StringField('ID de cliente para la empresa de correo')
    #shipping_address = StringField('Calle')
    #shipping_number =StringField('numero')
    #shipping_floor = StringField('Piso y depto')
    #shipping_zipcode = StringField('Codigo Postal')
    #shipping_city = StringField('Ciudad')
    #shipping_province = StringField('Provincia')
    #shipping_country = StringField('Pais')
    #shipping_info = StringField('Info para envíos')

    submit = SubmitField('Confirmar')

class EditProfileCompanyForm(FlaskForm):
    store_name = StringField('Nombre de la tienda')
    platform = StringField('Plataforma utilizada')
    platform_token_type = StringField('Token type', render_kw={'readonly': True})
    platform_access_token = StringField('Access Token', render_kw={'readonly': True})
    store_main_language = StringField('Idioma Principal', render_kw={'readonly': True})
    store_main_currency = StringField('Moneda Principal', render_kw={'readonly': True})
    store_country = StringField('Pais de la Tienda', render_kw={'readonly': True})
    store_name_bis = StringField('Nombre de la tienda - con lenguage automático', render_kw={'readonly': True})
    store_url = StringField('Url con protocolo', render_kw={'readonly': True})
    store_plan = StringField('Plan', render_kw={'readonly': True})
    store_phone = StringField('Telefono', render_kw={'readonly': True})
    store_address= StringField('Dirección', render_kw={'readonly': True})

    contact_name = StringField('Nombre del contacto')
    contact_phone = StringField('Telefono del contacto')
    contact_email = StringField('Email del contacto')
    admin_email = StringField('Email de Administración')
    communication_email = StringField('Email para las comuniaciones')
    
    correo_usado = StringField('Empresa de correo utilizada')
    correo_apikey = StringField('API KEY de la empresa de correo')
    correo_id = StringField('ID de cliente para la empresa de correo')
    correo_test = BooleanField('Va a utilizar el entorno de Test para los correos:')
    correo_apikey_test = StringField('API KEY de la empresa de correo - Entorno TEST')
    correo_id_test = StringField('ID de cliente para la empresa de correo - Entorno TEST')
    
    shipping_address = StringField('Calle')
    shipping_number =StringField('numero')
    shipping_floor = StringField('Piso y depto')
    shipping_zipcode = StringField('Codigo Postal')
    shipping_city = StringField('Ciudad')
    shipping_province = StringField('Provincia')
    shipping_country = StringField('Pais')
    shipping_info = StringField('Info para envíos')

    param_logo = StringField('Ruta para el Logo')
    param_fondo = StringField('Ruta para el fondo')
    param_config = StringField('Ruta para el archivo de configuración')

    submit = SubmitField('Confirmar')

#class EmptyForm(FlaskForm):
#    submit = SubmitField('Submit')