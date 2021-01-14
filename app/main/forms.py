from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    platform = StringField('Plataforma', validators=[DataRequired()])
    company_id = StringField('Store_id', validators=[DataRequired()])

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

#class EmptyForm(FlaskForm):
#    submit = SubmitField('Submit')