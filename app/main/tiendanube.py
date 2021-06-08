import requests
import json
import os
import shutil
from app import db
from app.models import User, Company, Customer, Order_header, Order_detail, Transaction_log
from flask_login import current_user
from flask import flash, current_app


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
        flash('Hubo un problema en la devolución No se pudo devolver el stock. Error {}'.format(order.status_code))
        return 'Failed'
    return 'Success'


def generar_envio_tiendanube(orden, linea, unCliente, unaEmpresa):
    url = "https://api.tiendanube.com/v1/"+str(current_user.store)+"/orders/"
    payload={}
    headers = {
        'Content-Type': 'application/json',
        'Authentication': unaEmpresa.platform_token_type+' '+unaEmpresa.platform_access_token
    }
        
    orden_tmp = { 
        "status": "open",
        "gateway": "offline",
        "payment_status": "paid",
        "products": [
            {
                "variant_id": linea.accion_cambiar_por,
                "quantity": linea.accion_cantidad,
                "price": 0
            }
        ],
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
        "shipping_pickup_type": "ship",
        "shipping": "not-provided",
        "shipping_option": "No informado",
        "send_confirmation_email" : False,
        "send_fulfillment_email" : False
        }

    order = requests.request("POST", url, headers=headers, data=json.dumps(orden_tmp))
    if order.status_code != 201:
        flash('Hubo un problema en la generación de la Orden. Error {}'.format(order.status_code))  
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
            
        else: 
            empresa = traer_datos_tiendanube(store, respuesta['token_type'],respuesta['access_token'] )
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
                correo_usado = 'Ninguno',
                correo_test = True
            )
            db.session.add(unaEmpresa)
            inicializa_tiendanube(unaEmpresa)
            
        db.session.commit()
        return unaEmpresa
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


def inicializa_tiendanube(empresa) :
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
    script_2= {
    "src": "https://frontprod.borisreturns.com/static/boris_politica.js",
    "event" : "onload",
    "where" : "store"
    }
    script_3= {
    "src": "https://frontprod.borisreturns.com/static/boris.js",
    "event" : "onload",
    "where" : "store"
    }

    response_1 = requests.request("POST", url, headers=headers, data=json.dumps(script_1))
    response_2 = requests.request("POST", url, headers=headers, data=json.dumps(script_2))
    response_3 = requests.request("POST", url, headers=headers, data=json.dumps(script_3))

    ### Crea usuario para Backoffice
    unUsuario = User(
        username=empresa.store_name[0:8], 
        email=empresa.admin_email, 
        store=empresa.store_id
        )
    unUsuario.set_password(empresa.store_name[0:8])
    db.session.add(unUsuario)
    db.session.commit()

    ### Crea carpeta para mails
    #if not os.path.exists('app/templates/email/'+str(empresa.store_id)):
    #    os.mkdir('app/templates/email/'+str(empresa.store_id))
    #    source_dir = 'app/templates/email_models'
    #    target_dir = 'app/templates/email/'+str(empresa.store_id)
    
    #    file_names = os.listdir(source_dir)
    
    #    for file_name in file_names:
    #        shutil.move(os.path.join(source_dir, file_name), target_dir)
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