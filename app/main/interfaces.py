import requests
import json
import string
import random
from app import db
from app.models import User, Company, Customer, Order_header, Order_detail, Transaction_log, categories_filter
from app.main.moova import toready_moova
from app.main.tiendanube import buscar_producto_tiendanube,  genera_credito_tiendanube
from app.email import send_email
from flask import session, flash, current_app,render_template
from flask_login import current_user
from datetime import datetime
import os

def cargar_pedidos():
    Pedidos = []
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
        # flash('monto {} tipo {}'.format(x['monto_a_devolver'], type(x['monto_a_devolver'])))
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
        # flash('Producto {} - monto: {}'.format(unProducto, unProducto.monto_a_devolver))
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


def buscar_producto(prod_id, empresa):
    if empresa.platform == 'tiendanube':
        producto = buscar_producto_tiendanube(prod_id, empresa)
    else:
        return 'no existe'
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
        manda_envio = toready_moova(orden,company,customer) 
        return manda_envio
    else:
        ## envio mail con instrucciones para envío manual
        orden_tmp = Order_header.query.get(orden.id)
        orden_tmp.status = 'Shipping'
        orden_tmp.sub_status = traducir_estado('READY')[0]
        orden_tmp.status_resumen = traducir_estado('READY')[1]
        orden_tmp.last_update_date = str(datetime.utcnow)
        db.session.commit()
        send_email('Tu orden ha sido confirmada', 
                #sender=current_app.config['ADMINS'][0], 
                sender=company.communication_email,
                recipients=[customer.email], 
                text_body=render_template('email/pedido_confirmado.txt',
                                         company=company, customer=customer, order=orden, envio=orden.courier_method),
                html_body=render_template('email/pedido_confirmado.html',
                                         company=company, customer=customer, order=orden, envio=orden.courier_method), 
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
    customer = Customer.query.get(orden.customer_id)
    company = Company.query.get(orden.store)

    unaTransaccion = Transaction_log(
            sub_status = traducir_estado('APROBADO')[0],
            status_client = traducir_estado('APROBADO')[2],
            order_id = orden.id,
            user_id = current_user.id,
            username = current_user.username
        )
    db.session.add(unaTransaccion)
    db.session.commit()
    send_email('Tu orden ha sido aprobada', 
                #sender=current_app.config['ADMINS'][0], 
                sender=company.communication_email,
                recipients=[customer.email], 
                text_body=render_template('email/pedido_aprobado.txt',
                                         company=company, customer=customer, order=orden, envio=orden.courier_method),
                html_body=render_template('email/pedido_aprobado.html',
                                         company=company, customer=customer, order=orden, envio=orden.courier_method), 
                attachments=None, 
                sync=False)


def toReject(orden_id):
    orden = Order_header.query.get(orden_id)    
    orden.status = 'En Proceso'
    orden.sub_status = traducir_estado('RECHAZADO')[0]
    orden.status_resumen = traducir_estado('RECHAZADO')[1]
    orden.last_update_date = str(datetime.utcnow)
    customer = Customer.query.get(orden.customer_id)
    company = Company.query.get(orden.store)

    unaTransaccion = Transaction_log(
            sub_status = traducir_estado('RECHAZADO')[0],
            status_client = traducir_estado('RECHAZADO')[2],
            order_id = orden.id,
            user_id = current_user.id,
            username = current_user.username
        )
    db.session.add(unaTransaccion)
    db.session.commit()
    send_email('Tu orden ha sido rechazada', 
                sender=company.communication_email,
                recipients=[customer.email], 
                text_body=render_template('email/pedido_rechazado.txt',
                                         company=company, customer=customer, order=orden, envio=orden.courier_method),
                html_body=render_template('email/pedido_rechazado.html',
                                         company=company, customer=customer, order=orden, envio=orden.courier_method), 
                attachments=None, 
                sync=False)


def genera_credito(empresa, monto, cliente, orden, linea):
    importe = float(monto)
    codigo_tmp = genera_codigo(8)
    codigo = str(orden.order_number)+codigo_tmp+str(orden.id)
    if empresa.platform == 'tiendanube':
        cupon = genera_credito_tiendanube(empresa, importe, codigo)
        if cupon != 'Failed':
            send_email('Hemos generado tu Cupón', 
                    sender=empresa.communication_email,
                    recipients=[cliente.email], 
                    text_body=render_template('email/cupon_generado.txt',
                                            company=empresa, customer=cliente, order=orden, cupon=cupon, monto=importe),
                    html_body=render_template('email/cupon_generado.html',
                                            company=empresa, customer=cliente, order=orden, cupon=cupon, monto=importe), 
                    attachments=None, 
                    sync=False)
            send_email('BORIS ha generado un Cupon', 
                    sender=empresa.communication_email,
                    recipients=[empresa.admin_email], 
                    text_body=render_template('email/cupon_empresa.txt',
                                            customer=cliente, order=orden, cupon=cupon, monto=importe, linea=linea),
                    html_body=render_template('email/cupon_empresa.html',
                                            customer=cliente, order=orden, cupon=cupon, monto=importe, linea=linea), 
                    attachments=None, 
                    sync=False)
        return cupon
    else:
        return "Failed"
    

def genera_codigo(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


############# Envia datos de la empresa al FRONT para dar de alta o actualizar #################
def actualiza_empresa(empresa):
    if current_app.config['SERVER_ROLE'] == 'DEV':
        url="https://front.borisreturns.com/empresa/chequear"
    if current_app.config['SERVER_ROLE'] == 'PROD':
        url="https://frontprod.borisreturns.com/empresa/chequear"
    
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "store_id" : empresa.store_id,
        "platform" : empresa.platform,
        "platform_token_type" :  empresa.platform_token_type,
        "platform_access_token" : empresa.platform_access_token,
        "store_name" : empresa.store_name ,
        "store_url" : empresa.store_url,    
        "store_phone" : empresa.store_phone,
        "store_address": empresa.store_address, 
        "admin_email" : empresa.admin_email,
        "contact_email" : empresa.contact_email,
        "communication_email" : empresa.communication_email, 
        "param_logo" : empresa.param_logo,
        "param_fondo" : empresa.param_fondo,
        "store_main_language" : empresa.store_main_language,
        "store_main_currency" : empresa.store_main_currency,
        "store_country" : empresa.store_country,
        "correo_usado" : empresa.correo_usado, 
        "correo_test" : empresa.correo_test, 
        "correo_apikey" : empresa.correo_apikey,
        "correo_id" : empresa.correo_id,
        "correo_id_test" : empresa.correo_id_test,
        "correo_apikey_test" : empresa.correo_apikey_test,
        "contact_email" : empresa.contact_email,
        "contact_name" : empresa.contact_name,
        "contact_email" : empresa.contact_email,
        "contact_phone" : empresa.contact_phone,
        "shipping_address" : empresa.shipping_address,
        "shipping_number" : empresa.shipping_number,
        "shipping_floor" : empresa.shipping_floor,
        "shipping_zipcode" : empresa.shipping_zipcode,
        "shipping_city" : empresa.shipping_city,
        "shipping_province" : empresa.shipping_province,
        "shipping_country" : empresa.shipping_country,
        "shipping_info" : empresa.shipping_info 
    }
    solicitud = requests.request("POST", url, headers=headers, data=json.dumps(data))
    if solicitud.status_code != 200:
        return 'Failed'
    else: 
        return 'Success'


############# Envia datos de las categorias filtradas al FRONT para dar de alta o actualizar #################
def actualiza_empresa_categorias(empresa):

    categorias_tmp = categories_filter.query.filter_by(store=empresa.store_id).all()
    categorias = []
    for i in categorias_tmp:
        categorias.append(i.category_id)
    
    if current_app.config['SERVER_ROLE'] == 'DEV':
        url="https://front.borisreturns.com/empresa_categorias"
    if current_app.config['SERVER_ROLE'] == 'PROD':
        url="https://frontprod.borisreturns.com/empresa_categorias"
    
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "store_id" : empresa.store_id,
        "categorias" : categorias,
    }
    solicitud = requests.request("POST", url, headers=headers, data=json.dumps(data))
    if solicitud.status_code != 200:
        return 'Failed'
    else: 
        return 'Success'
    

