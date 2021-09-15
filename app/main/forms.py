from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    store = StringField('Store_id', validators=[DataRequired()])
    submit = SubmitField('Confirmar')

class EditProfileCompanyForm(FlaskForm):
    store_name = StringField('Nombre de la tienda')
    store_country = StringField('Pais de la Tienda', render_kw={'readonly': True})
    store_url = StringField('Url con protocolo', render_kw={'readonly': True})
    store_phone = StringField('Telefono')
    store_address= StringField('Dirección')
    contact_name = StringField('Nombre del contacto')
    contact_phone = StringField('Telefono del contacto')
    contact_email = StringField('Email del contacto', validators=[Email()])
    admin_email = StringField('Email de Administración', validators=[Email()])
    submit = SubmitField('Confirmar')

class EditParamsCompanyForm(FlaskForm):
    platform = StringField('Plataforma utilizada')
    #platform_token_type = StringField('Token type', render_kw={'readonly': True})
    #platform_access_token = StringField('Access Token', render_kw={'readonly': True})
    store_main_language = StringField('Idioma Principal', render_kw={'readonly': True})
    store_main_currency = StringField('Moneda Principal', render_kw={'readonly': True})
    stock_vuelve_config = BooleanField('Al devolver el stock se ingresa físicamente:')
    param_logo = StringField('Ruta para el Logo')
    param_fondo = StringField('Ruta para el fondo')
    param_config = StringField('Ruta para el archivo de configuración', render_kw={'readonly': True})
    submit = SubmitField('Confirmar')

class EditCorreoCompanyForm(FlaskForm):
    correo_usado = StringField('Empresa de correo utilizada')
    correo_apikey = StringField('API KEY de la empresa de correo')
    correo_id = StringField('ID de cliente para la empresa de correo')
    correo_test = BooleanField('Va a utilizar el entorno de Test para los correos')
    correo_apikey_test = StringField('API KEY de la empresa de correo - Entorno TEST')
    correo_id_test = StringField('ID de cliente para la empresa de correo - Entorno TEST')

    shipping_address = StringField('Calle')
    shipping_number =StringField('numero')
    shipping_floor = StringField('Piso y depto')
    shipping_zipcode = StringField('Codigo Postal')
    shipping_city = StringField('Ciudad')
    shipping_province = StringField('Provincia')
    shipping_country = StringField('Pais', render_kw={'readonly': True})
    shipping_info = StringField('Info para envíos')
    submit = SubmitField('Confirmar')

class EditMailsCompanyForm(FlaskForm):
    communication_email = StringField('Email para las comuniaciones', validators=[Email()])
    aprobado_note = StringField('Nota para el MAIL de Aprobacion', validators=[Length(max=350)])
    rechazado_note = StringField('Nota para el MAIL de Rechazo al recibir', validators=[Length(max=350)])
    envio_manual_note = StringField('Nota para el MAIL de confirmacion - Retiro Manual', validators=[Length(max=350)])
    envio_coordinar_note = StringField('Nota para el MAIL de confirmacion -Retiro a Coordinar', validators=[Length(max=350)])
    envio_correo_note = StringField('Nota para el MAIL de confirmacion - Retiro x Correo', validators=[Length(max=350)])
    cupon_generado_note = StringField('Nota para el MAIL de generación de cupón', validators=[Length(max=350)])
    finalizado_note = StringField('Nota para el MAIL de finalización', validators=[Length(max=350)])
    submit = SubmitField('Confirmar')

class EditMailsFrontCompanyForm(FlaskForm):
    confirma_manual_note = StringField('Nota para el MAIL de inicio de Solicitud - Retiro Manual', validators=[Length(max=350)])
    confirma_coordinar_note = StringField('Nota para el MAIL de inicio de Solicitud -Retiro a Coordinar', validators=[Length(max=350)])
    confirma_moova_note = StringField('Nota para el MAIL de inicio de Solicitud - Retiro x Moova', validators=[Length(max=350)])
    submit = SubmitField('Confirmar')
