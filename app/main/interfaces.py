import requests
import json
from app import db
from app.models import User, Company, Customer, Order_header, Order_detail, Transaction_log
from flask import session, flash, current_app
from flask_login import current_user
from datetime import datetime
import os


def cargar_pedidos():
    Pedidos = []
    #flash('os :{}'.format(os.environ.get('FILES_PEDIDOS_URL')))
    #flash('app {}'.format(current_app.config['FILES_PEDIDOS_URL']))
    url = "../Boris_common/logs/"
    for file in os.listdir(url):
        files = []
        full_filename = "%s/%s" % (url, file)
        with open(full_filename,'r') as fi:
            dict = json.load(fi)
            crear_pedido(dict)
            files.append(full_filename)
    return files


def crear_pedido(pedido):
    unaEmpresa = Company.query.get(pedido['company']['store_id'])
    
    if Customer.query.get(pedido['cliente']['id']):
        unCliente = Customer.query.get(pedido['cliente']['id'])
    else: 
        unCliente = Customer(
        id = pedido['cliente']['id'],
        name = pedido['cliente']['name'],
        email = pedido['cliente']['email'],
        phone = pedido['cliente']['phone'],
        platform=unaEmpresa.platform
        )

    unaOrden = Order_header(
        order_number = pedido['orden_nro'],
        order_id_anterior = pedido['orden'],
        creation_date = pedido['orden_fecha'],
        last_update_date = pedido['orden_fecha'],
        payment_method = pedido['orden_medio_de_pago'],
        payment_card = pedido['orden_tarjeta_de_pago'],
        courier_order_id = pedido['correo']['correo_id'],
        courier_precio = pedido['correo']['correo_precio_formateado'],
        status = 'Shipping',
        sub_status = traducir_estado(pedido['correo']['correo_status'])[0],
        status_resumen = traducir_estado(pedido['correo']['correo_status'])[1],
        customer_address = pedido['cliente']['address']['street'],
        customer_number = pedido['cliente']['address']['number'],
        customer_floor = pedido['cliente']['address']['floor'],
        customer_zipcode = pedido['cliente']['address']['zipcode'],
        customer_locality = pedido['cliente']['address']['locality'],
        customer_city = pedido['cliente']['address']['city'],
        customer_province = pedido['cliente']['address']['province'],
        customer_country = pedido['cliente']['address']['country'],
        buyer = unCliente,
        pertenece = unaEmpresa
    )   

    indice = 1
    for x in pedido['producto']: 
        flash('monto {} tipo {}'.format(x['monto_a_devolver'], type(x['monto_a_devolver'])))
        unProducto = Order_detail(
            order_line_number = str(pedido['orden']) + str(indice),
            line_number = indice,
            prod_id =  x['id'],
            name = x['name'],
            variant = x['variant'],
            accion = x['accion'],
            monto_a_devolver = x['monto_a_devolver'],
            accion_cantidad = x['accion_cantidad'],
            accion_cambiar_por = x['accion_cambiar_por'],
            motivo =  x['motivo'],
            gestionado = 'Iniciado',
            productos = unaOrden
            )
        flash('Producto {} - monto: {}'.format(unProducto, unProducto.monto_a_devolver))
        db.session.add(unProducto)
        indice += indice
    db.session.commit() 
    return unaOrden


def resumen_ordenes(store_id):
    shipping = 0
    enproceso = 0
    entransito = 0
    cerradas = 0
    solicitadas = 0
    recibidas = 0
    aprobadas = 0
    rechazadas = 0
    ordenes = Order_header.query.filter_by(store=store_id).all()
    for i in ordenes:
        if i.status == 'Shipping':
            shipping += 1
            if i.status_resumen == 'Solicitado':
                solicitadas += 1
            else:
                if i.status_resumen == 'En Transito':
                    entransito += 1
                else: 
                    if i.status_resumen == 'Recibido':
                        recibidas += 1
        else:
            if i.status == 'En Proceso':
                enproceso += 1
                if i.status_resumen == 'Aprobado':
                    aprobadas += 1
                else:
                    if i.status_resumen == 'Rechazado':
                        rechazadas += 1
            else:
                if i.status == 'Closed':
                    cerradas += 1
    
    resumen = {'shipping':shipping, 'enproceso':enproceso,'cerradas':cerradas, 
        'solicitadas':solicitadas, 'entransito':entransito, 'recibidas': recibidas, 
            'aprobadas':aprobadas, 'rechazadas':rechazadas}
    return resumen


def traducir_estado(estado):
    switcher={
            'DRAFT':['Solicitado','Solicitado','Inicio de la Gestion'],
            'READY':['Listo para retiro','En Transito', 'Solicitud aprobada'],
            'CONFIRMED':['Confirmado','En Transito', 'No'],
            'PICKEDUP':['Recogido','En Transito', 'Se recogió la orden'],
            'INTRANSIT':['En camino','En Transito','No'],
            'DELIVERED':['Recibido','Recibido', 'Llego a nuestro depósito'],
            "DEVUELTO":['Prenda devuleta a Stock', 'Devuelto', 'No'],
            "CAMBIADO":['Orden de cambio iniciada', 'Cambiado', 'Se generó el cambio'],
            "APROBADO":['Aprobado','Aprobado','Tu solicitud fue aprobada'],
            "RECHAZADO":['Rechazado', 'Rechazado', 'Tu solicitud fue rechazada'],
            "CERRADO":['Cerrrado', 'Cerrado', 'Tu orden fue finalizada']
        }
    return switcher.get(estado,"Aprobado")



def toReady(orden_courier_id, company):
  url = "https://api-dev.moova.io/b2b/shippings/"+str(orden_courier_id)+"/READY"

  headers = {
    'Authorization': company.correo_apikey,
    'Content-Type': 'application/json',
   }

  params = {'appId': company.correo_id}

  solicitud = requests.request("POST", url, headers=headers, params=params)
  if solicitud.status_code != 201:
    flash('Hubo un problema con la generación del evío. Error {}'.format(solicitud.status_code))
    flash('url {} params{}'.format(url, params))
    return "Fail"
  else:
    flash('La orden se actualizo exitosamente')
    return 'Success'



def toApproved(orden_id):
    orden = Order_header.query.get(orden_id)    
    orden.status = 'En Proceso'
    orden.sub_status = traducir_estado('APROBADO')[0]
    orden.status_resumen =traducir_estado('APROBADO')[1]
    orden.last_update_date = str(datetime.utcnow)

    unaTransaccion = Transaction_log(
            sub_status = traducir_estado('APROBADO')[0],
            status_client = traducir_estado('APROBADO')[2],
            order_id = orden.id,
            user_id = current_user.id,
            username = current_user.username
        )
    db.session.add(unaTransaccion)

    db.session.commit()


def toReject(orden_id):
    orden = Order_header.query.get(orden_id)    
    orden.status = 'En Proceso'
    orden.sub_status = traducir_estado('RECHAZADO')[0]
    orden.status_resumen = traducir_estado('RECHAZADO')[1]
    orden.last_update_date = str(datetime.utcnow)

    unaTransaccion = Transaction_log(
            sub_status = traducir_estado('RECHAZADO')[0],
            status_client = traducir_estado('RECHAZADO')[2],
            order_id = orden.id,
            user_id = current_user.id,
            username = current_user.username
        )
    db.session.add(unaTransaccion)
    db.session.commit()

                            

