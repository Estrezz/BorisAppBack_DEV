import requests
import json
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
    stock_tmp = int(order['stock']) + int(cantidad)
    stock = {
        "stock": stock_tmp
    }
    # Aumenta el stock de la tienda en la cantidad devuelta
    order = requests.request("PUT", url, headers=headers, data=json.dumps(stock))

    if order.status_code != 200:
        flash('Hubo un problema en la devolución No se pudo devolver el stock. Error {}'.format(solicitud.status_code))
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
    #flash('codigo de respuesta {}'.format(response.status_code))
    respuesta = response.json()
    #flash ('Respuesta {} {}'.format(respuesta, type(respuesta)))
    #flash('curl {}{} response {}'.format(url,data, respuesta))
    #flash('error {}'.format(respuesta['error']))
    if 'scope' in respuesta:
        if 'store_id' in respuesta:
            store = respuesta['store_id']
        if 'user_id' in respuesta:
            store = respuesta['user_id']
        
        #flash('Store {}'.format(store))
        empresa = traer_datos_tiendanube(store, respuesta['token_type'],respuesta['access_token'] )
        unaEmpresa = Company(
            store_id = store,
            platform = 'tiendaNube',
            platform_token_type =  respuesta['token_type'],
            platform_access_token = respuesta['access_token'],
            store_name = empresa['name']['es'],
            admin_email = empresa['email'],
            contact_email = empresa['contact_email'],
            param_logo = empresa['logo'],
            store_main_language = empresa['main_language'],
            store_country = empresa['country'],
            correo_usado = 'Ninguno',
            correo_test = True
        )
        db.session.add(unaEmpresa)
        db.session.commit()
        return empresa['name']['es']
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

    