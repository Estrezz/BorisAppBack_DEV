import requests
import json
## import os
## import shutil
import re
from datetime import datetime
from app import db
## from app.models import User, Company, Customer, Order_header, Order_detail, Transaction_log
from app.models import User, Company
from flask_login import current_user
from flask import flash, current_app

def buscar_datos_variantes_tiendanube(prod_id, variant, empresa):
    url = "https://api.tiendanube.com/v1/"+str(current_user.store)+"/products/"+str(prod_id)+"/variants/"+str(variant)
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': empresa.platform_token_type+' '+empresa.platform_access_token
    }
    variante = requests.request("GET", url, headers=headers, data=payload).json()
    return variante



def buscar_producto_tiendanube(prod_id, empresa):
    url = "https://api.tiendanube.com/v1/"+str(current_user.store)+"/products/"+str(prod_id)
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': empresa.platform_token_type+' '+empresa.platform_access_token
    }
    producto = requests.request("GET", url, headers=headers, data=payload).json()
    return producto


def devolver_stock_tiendanube(empresa, prod_id, variant, cantidad):
    url = "https://api.tiendanube.com/v1/"+str(current_user.store)+"/products/"+str(prod_id)+"/variants/"+str(variant)
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': empresa.platform_token_type+' '+empresa.platform_access_token
    }
    # Trae stock actual
    order = requests.request("GET", url, headers=headers, data=payload).json()

    ### Si la variante no existe
    if 'stock' not in order:
        return 'Failed_Variante'
        
    #flash('order{} - prod_id {} - variant {}'.format(order, prod_id, variant))
    if isinstance(order['stock'], type(None)) == True:
        flash('No se está gestionando información de Stock.')
        return 'Success'
    stock_tmp = int(order['stock']) + int(cantidad)
    stock = {
        "stock": stock_tmp
    }
    # Aumenta el stock de la tienda en la cantidad devuelta
    order = requests.request("PUT", url, headers=headers, data=json.dumps(stock))

    if order.status_code != 200:
        flash('Hubo un problema en la devolución No se pudo devolver el stock. Error {} - {}'.format(order.status_code, order.content))
        flash('{} - {}'.format(url, json.dumps(stock)))
        return 'Failed'
    if int(cantidad) > 0:
        flash("Se devolvió satisfactoriamente el stock a la variante {}".format(str(variant))) #### stock FALLA
    return 'Success'


def generar_envio_tiendanube(orden, lineas, unCliente, unaEmpresa):
    url = "https://api.tiendanube.com/v1/"+str(current_user.store)+"/orders/"
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': unaEmpresa.platform_token_type+' '+unaEmpresa.platform_access_token
    }

    if (orden.customer_address == ''  or orden.customer_number == ''):
        orden.customer_address = 'null'
        orden.customer_number = 'null'
        tipoenvio = 'pickup'
    else:
        tipoenvio = 'ship'

    orden_tmp = { 
        "status": "open",
        #"gateway": "not-provided",
        "payment_status": "pending",
        # Se crea la orden en 0
        # 'total':orden.nuevo_envio_total,
        'total':0,
        "products": [],
        "inventory_behaviour" : "claim",
        "customer": {
            "email": unCliente.email,
            "name": unCliente.name,
            "phone": unCliente.phone
        },
        "note": 'Cambio realizado mediante Boris',
        "shipping_address": {
            "first_name": unCliente.name,
            "address": orden.customer_address,
            "number": orden.customer_number,
            "floor": orden.customer_floor,
            "locality": orden.customer_locality,
            "city": orden.customer_city,
            "province": orden.customer_province,
            "zipcode": orden.customer_zipcode,
            "country": orden.customer_country,
            "phone": unCliente.phone
        },
        "shipping_pickup_type": tipoenvio,
        "shipping": "not-provided",
        "shipping_option": "No informado",
        # Se crea la orden en 0
        # "shipping_cost_customer": orden.nuevo_envio_costo,
        "shipping_cost_customer": 0,
        "send_confirmation_email" : False,
        "send_fulfillment_email" : False
        }
    
    productos_tmp = []
    for i in lineas:
        productos_tmp.append ({
        "variant_id":i.accion_cambiar_por,
        "quantity": i.accion_cantidad,
        # Se crea la orden en 0
        # "price": i.accion_cambiar_por_diferencia
        "price": 0
        })
    orden_tmp['products'] = productos_tmp

    order = requests.request("POST", url, headers=headers, data=json.dumps(orden_tmp))
    if order.status_code != 201:
        flash('Hubo un problema en la generación de la Orden. Error {}'.format(order.status_code))  
        flash(json.dumps(orden_tmp))

        if order.status_code == 422:
            flash('Código {} - {}'.format(order.status_code, order.content))
        return 'Failed'
    return 'Success'


def autorizar_tiendanube(codigo):
    url = "https://www.tiendanube.com/apps/authorize/token"
    data = {
        'client_id': current_app.config['CLIENT_ID_TN'] ,
        'client_secret': current_app.config['CLIENT_SECRET_TN'],
        'grant_type': 'authorization_code',
        'code': codigo
    }
    response = requests.request("POST", url, data=data)
    respuesta = response.json()
    
    if 'scope' in respuesta:
        if 'store_id' in respuesta:
            store = respuesta['store_id']
        if 'user_id' in respuesta:
            store = respuesta['user_id']
        
        if Company.query.filter_by(store_id=store).first():
            unaEmpresa = Company.query.filter_by(store_id=store).first()
            unaEmpresa.platform_token_type = respuesta['token_type']
            unaEmpresa.platform_access_token = respuesta['access_token']
            unaEmpresa.start_date = datetime.utcnow(),
            inicializa_tiendanube(unaEmpresa, 'existente')
            
        else: 
            empresa = traer_datos_tiendanube(store, respuesta['token_type'],respuesta['access_token'] )
            if empresa['type']:
                tipo_empresa = empresa['type']
            else: 
                tipo_empresa = 'desconocido'

            #### carga los datos de la Empresa ######################################
            unaEmpresa = Company(
                store_id = store,
                platform = 'tiendanube',
                platform_token_type =  respuesta['token_type'],
                platform_access_token = respuesta['access_token'],
                store_name = empresa['name'][empresa['main_language']],
                store_url = empresa['url_with_protocol'],
                store_plan = empresa['plan_name'],
                store_phone = empresa['phone'],
                store_address= empresa['business_address'], 
                admin_email = empresa['email'],
                contact_email = empresa['contact_email'],
                param_logo = empresa['logo'],
                store_main_language = empresa['main_language'],
                store_main_currency = empresa['main_currency'],
                store_country = empresa['country'],
                stock_vuelve_config = True,
                shipping_country = 'ARG',
                communication_email = 'info@borisreturns.com',
                communication_email_name = 'Cambios Boris',
                correo_usado = 'Ninguno',
                correo_cost = 'customer',
                start_date = datetime.utcnow(),
                demo_store = 0,
                plan_boris = 'Plan_C',
                rubro_tienda = tipo_empresa,
                correo_test = True,
                encuesta = False,
                habilitado = True,
                orden_solicitada_asunto = 'Tu orden ha sido iniciada',
                orden_confirmada_asunto = 'Tu orden ha sido confirmada',
                orden_rechazada_asunto = 'Tu orden ha sido rechazada',
                orden_aprobada_asunto = 'Tu orden ha sido aprobada',
                cupon_generado_asunto = 'Hemos generado tu cupón',
                orden_finalizada_asunto = 'El procesamiento de tu orden ha finalizado',
                orden_solicitada_habilitado = True,
                orden_confirmada_habilitado = True,
                orden_rechazada_habilitado = True,
                orden_aprobada_habilitado = True,
                cupon_generado_habilitado = True,
                orden_finalizada_habilitado = True,
            )
            db.session.add(unaEmpresa)
            inicializa_tiendanube(unaEmpresa, 'nueva')

        db.session.commit()
        return unaEmpresa
    else:
        flash("Error al autorizar la Tienda {}. Ponete en contacto con nosotros".format(respuesta))
    return 'Failed'


def traer_datos_tiendanube(store, token_type, access_token):
    url = "https://api.tiendanube.com/v1/"+str(store)+"/store"
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': str(token_type)+' '+str(access_token)
    }
    empresa = requests.request("GET", url, headers=headers, data=payload).json()
    return empresa

###################################################################################################3
# Iniciliaza una tienda cargando los scripts
# Si es una nueva tienda (tipo = 'nueva'  - crea el usuario en el Backoffica
###################################################################################################3
def inicializa_tiendanube(empresa, tipo) :
    ### Carga scripts en la tienda
    url = "https://api.tiendanube.com/v1/"+str(empresa.store_id)+"/scripts"
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': str(empresa.platform_token_type)+' '+str(empresa.platform_access_token)
    }
    script_1= {
    "src": "https://frontprod.borisreturns.com/static/boris_order.js",
    "event" : "onload",
    "where" : "store"
    }

    script_4= {
    "src": "https://frontprod.borisreturns.com/static/general.js",
    "event" : "onload",
    "where" : "store"
    }

    #### Valida si ya existen scripts antes de crearlos ####
    response = requests.request("GET", url, headers=headers).json()
    if len(response) < 1:
        response_1 = requests.request("POST", url, headers=headers, data=json.dumps(script_1))
        response_4 = requests.request("POST", url, headers=headers, data=json.dumps(script_4))
    #############################3

    ### Crea usuario para Backoffice
    if tipo == 'nueva':
        nombre = re.sub('[\s+]', '', empresa.store_name[0:8].strip())
        ### valida si ya existe el nombre del usuario
        user = User.query.filter_by(username=nombre).first()
        if user is not None:
            nombre = nombre+'_2'
        user = User.query.filter_by(username=nombre).first()
        if user is not None:
            nombre = nombre+'_3'
        unUsuario = User(
            username=nombre, 
            email=empresa.admin_email, 
            store=empresa.store_id
            )
        unUsuario.set_password(nombre)
        db.session.add(unUsuario)
        db.session.commit()
    return 'Success'


def genera_credito_tiendanube(empresa, monto, codigo):
    url = "https://api.tiendanube.com/v1/"+str(empresa.store_id)+"/coupons"
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': empresa.platform_token_type+' '+empresa.platform_access_token
    }
    cupon_tmp = { 
        "code": codigo,
        "type": "absolute",
        "value": monto,
        "max_uses": 1
    }
    cupon = requests.request("POST", url, headers=headers, data=json.dumps(cupon_tmp))
    if cupon.status_code != 201:
        flash('Hubo un problema en la generación del cupón. Error {}'.format(cupon.status_code))  
        return 'Failed'
    return codigo


## Devuelve todas las categorias existentes apra una tienda
def buscar_codigo_categoria_tiendanube(empresa):
    url = "https://api.tiendanube.com/v1/"+str(empresa.store_id)+"/categories?fields=id,name"
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': empresa.platform_token_type+' '+empresa.platform_access_token
    }
    categorias_tmp = requests.request("GET", url, headers=headers, data=payload).json()
    categorias = {}
    for x  in categorias_tmp:
        categorias[x['id']]=(x['name']['es'])
    return categorias



               