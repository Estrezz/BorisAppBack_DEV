import requests
import json
from app import db
from app.models import User, Company, Customer, Order_header, Order_detail, Transaction_log
from app.email import send_email
from flask import session, flash, current_app,render_template
from flask_login import current_user
from datetime import datetime
import os


def cargar_pedidos():
    Pedidos = []
    #flash('os :{}'.format(os.environ.get('FILES_PEDIDOS_URL')))
    flash('app {}'.format(current_app.config['FILES_PEDIDOS_URL']))
    #url = "../Boris_common/logs/"
    url = current_app.config['FILES_PEDIDOS_URL']
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
        identification = pedido['cliente']['identification'],
        email = pedido['cliente']['email'],
        phone = pedido['cliente']['phone'],
        platform=unaEmpresa.platform
        )

    unaOrden = Order_header(
        order_number = pedido['orden_nro'],
        order_id_anterior = pedido['orden'],
        gastos_cupon = pedido['orden_gastos_cupon'],
        gastos_gateway = pedido['orden_gastos_gateway'],
        gastos_shipping_owner = pedido['orden_gastos_shipping_owner'],
        gastos_shipping_customer = pedido['orden_gastos_shipping_customer'],
        gastos_promocion = pedido ['orden_gastos_promocion'],
        date_creation = datetime.strptime(pedido['orden_fecha'], '%Y-%m-%d %H:%M:%S.%f'),
        date_lastupdate = datetime.strptime(pedido['orden_fecha'], '%Y-%m-%d %H:%M:%S.%f'),
        payment_method = pedido['orden_medio_de_pago'],
        payment_card = pedido['orden_tarjeta_de_pago'],
        courier_method = pedido['correo']['correo_metodo_envio'],
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
            precio = float(x['precio']),
            promo_descuento = float(x['promo_descuento']),
            promo_nombre = x['promo_nombre'],
            promo_precio_final = float(x['promo_precio_final']),
            accion_cantidad = x['accion_cantidad'],
            accion_cambiar_por = x['accion_cambiar_por'],
            accion_cambiar_por_desc = x['accion_cambiar_por_desc'],
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
                if i.status == 'Cerrado':
                    cerradas += 1
    
    resumen = {'shipping':shipping, 'enproceso':enproceso,'cerradas':cerradas, 
        'solicitadas':solicitadas, 'entransito':entransito, 'recibidas': recibidas, 
            'aprobadas':aprobadas, 'rechazadas':rechazadas}
    return resumen

def buscar_producto(prod_id):
    url = "https://api.tiendanube.com/v1/1447373/products/"+str(prod_id)
    payload={}
    headers = {
        'User-Agent': 'Boris (erezzonico@borisreturns.com)',
        'Content-Type': 'application/json',
        'Authentication': 'bearer cb9d4e17f8f0c7d3c0b0df4e30bcb2b036399e16'
    }

    producto = requests.request("GET", url, headers=headers, data=payload).json()
    return producto



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
            "APROBADO":['Aprobado','Aprobado','Tu orden fue aprobada'],
            "RECHAZADO":['Rechazado', 'Rechazado', 'Tu orden fue rechazada'],
            "CERRADO":['Cerrado', 'Cerrado', 'Tu orden fue finalizada']
        }
    return switcher.get(estado,"Aprobado")



def toReady(orden, company):
    customer = Customer.query.get(orden.customer_id)
    if orden.courier_method == 'Moova':
        url = "https://api-dev.moova.io/b2b/shippings/"+str(orden.courier_order_id)+"/READY"
        url_label = "https://api-dev.moova.io/b2b/shippings/"+str(orden.courier_order_id)+"/label"
        headers = {
            'Authorization': company.correo_apikey,
            'Content-Type': 'application/json',
        }
        params = {'appId': company.correo_id}

        solicitud = requests.request("POST", url, headers=headers, params=params)
        if solicitud.status_code != 201:
            if solicitud.status_code == 409:
                flash('Revise y corrija la dirección en la página del correo. Error {}'.format(solicitud.status_code))
                return 'Fail'
            flash('Hubo un problema con la generación del evío. Error {}'.format(solicitud.status_code))
            flash('url {} params{}'.format(url, params))
            return "Fail"
        else:
            flash('La orden se actualizó en Moova exitosamente')
            label_tmp = requests.request("GET", url_label, headers=headers, params=params)
            label = label_tmp.json()['label']
            flash ('label {}'.format(label))
            send_email('Tu orden ha sido confirmada', 
                sender=current_app.config['ADMINS'][0], 
                recipients=[customer.email], 
                text_body=render_template('email/1447373/pedido_confirmado.txt',
                                         customer=customer, order=orden, envio=orden.courier_method, label=label),
                html_body=render_template('email/1447373/pedido_confirmado.html',
                                         customer=customer, order=orden, envio=orden.courier_method, label=label), 
                attachments=None, 
                sync=False)
            return "Success"
    else:
        ## envio mail con instrucciones para envío manual
        orden_tmp = Order_header.query.get(orden.id)
        orden_tmp.status = 'Shipping'
        orden_tmp.sub_status = traducir_estado('READY')[0]
        orden_tmp.status_resumen = traducir_estado('READY')[1]
        orden_tmp.last_update_date = str(datetime.utcnow)
        db.session.commit()
        end_email('Tu orden ha sido confirmada', 
                sender=current_app.config['ADMINS'][0], 
                recipients=[customer.email], 
                text_body=render_template('email/1447373/pedido_confirmado.txt',
                                         customer=customer, order=orden, envio=orden.courier_method),
                html_body=render_template('email/1447373/pedido_confirmado.html',
                                         customer=customer, order=orden, envio=orden.courier_method), 
                attachments=None, 
                sync=False)
        return "Success"

def toReceived(orden_id):
    orden = Order_header.query.get(orden_id)    
    orden.status = 'Shipping'
    orden.sub_status = traducir_estado('DELIVERED')[0]
    orden.status_resumen =traducir_estado('DELIVERED')[1]
    orden.last_update_date = str(datetime.utcnow)

    unaTransaccion = Transaction_log(
            sub_status = traducir_estado('DELIVERED')[0],
            status_client = traducir_estado('DELIVERED')[2],
            order_id = orden.id,
            user_id = current_user.id,
            username = current_user.username
        )
    db.session.add(unaTransaccion)
    db.session.commit()

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

                            

