#import requests
import json
from app import db
from app.models import User, Company, Customer, Order, Product
from flask import session, flash, current_app
import os

def cargar_pedidos():
    Pedidos = []
    #flash('os :{}'.format(os.environ.get('FILES_PEDIDOS_URL')))
    #flash('app {}'.format(current_app.config['FILES_PEDIDOS_URL']))
    url = "../Boris_common/logs/"
    for file in os.listdir(url):
        full_filename = "%s/%s" % (url, file)
        flash('file {}'.format(full_filename))
        with open(full_filename,'r') as fi:
            dict = json.load(fi)
            crear_pedido(dict)
            #Pedidos.append(dict)
    
    return Pedidos


def crear_pedido(pedido):
    #unaEmpresa =  Company.query.filter(Company.store_id == pedido['store_id']).first()
    unaEmpresa =  Company.query.get(pedido['company']['id'])

    unCliente = Customer(
    id = pedido['cliente']['id'],
    name = pedido['cliente']['name'],
    email = pedido['cliente']['email'],
    phone = pedido['cliente']['phone'],
    address = pedido['cliente']['address']['street'],
    number = pedido['cliente']['address']['number'],
    floor = pedido['cliente']['address']['floor'],
    zipcode = pedido['cliente']['address']['zipcode'],
    locality = pedido['cliente']['address']['locality'],
    city = pedido['cliente']['address']['city'],
    province = pedido['cliente']['address']['province'],
    country = pedido['cliente']['address']['country'],
    )

    unaOrden = Order(
    id = pedido['orden'],
    payment_method = pedido['orden_medio_de_pago'],
    payment_card = pedido['orden_tarjeta_de_pago'],
    courier = pedido['correo']['correo_id'],
    status = 'Shipping',
    sub_status = pedido['correo']['correo_status'],
    buyer = unCliente,
    pertenece = unaEmpresa
    )   

    #for x in range(len(pedido['producto'])): 
    for x in pedido['producto']: 
        unProducto = Product(
            id =  x['id'],
            name = x['name'],
            accion = x['accion'],
            accion_cantidad = x['accion_cantidad'],
            accion_cambiar_por = x['accion_cambiar_por'],
            monto_a_devolver = x['monto_a_devolver'],
            motivo =  x['motivo'],
            articulos = unaOrden
            )
   