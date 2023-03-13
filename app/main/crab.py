import requests
import json

from flask import flash, render_template
from app.email import send_email
from flask_login import current_user
from app.models import CONF_correo, Codigos_postales, Company, correos


###################################################
# Cotiza envio en CRAB
###################################################
def cotiza_envio_crab(data, datos_correo, correo_servicio):
    ###########################################################################
    #### Si tienen salientes es un cambio si No devolucion
    ##########################################################################

    id_servicio = codigo_servicio_crab(data['correo']['salientes'], correo_servicio.roundtrip, data['from']['postalCode'])
    # print ('ID SERVICIO :'+str(id_servicio))
    if id_servicio == "Sin Cobertura":
         return 'Failed'
    
    url = "https://crab.epresis.com/api/v2/cotizador.json"
        
    headers = {
     'Content-Type': 'application/json'
    }

    solicitud_tmp = {
        "api_token": datos_correo.cliente_apikey,
        "codigo_servicio": id_servicio, # "110 - Devoluciones / 118 - Cambios" codigo de servicio de CRAB para logistica Inversa
        "cp_origen": data['from']['postalCode'],
        "cp_destino": data['to']['postalCode'],
        #"destino": "AMBA",
        "is_urgente": False,
        #"valor_declarado": 100.25
    }

    items_envio = []
    precio_total_envio = 0
    
    for i in data['items']:
        precio_total_envio += i['precio']
        items_envio.append (   
        {
            "bultos": i['cantidad'],
            "peso": i['peso'],
            "descripcion": i['descripcion'],
            "dimensiones": {
                "alto": i['alto'],
                "largo": i['largo'],
                "profundidad": i['profundidad']
            }   
        }
        )
    
    solicitud_tmp['productos'] = items_envio
    solicitud_tmp["valor_declarado"] = precio_total_envio

    payload = json.dumps(solicitud_tmp)
    
    solicitud = requests.request("POST", url, headers=headers, data=payload)
    if solicitud.status_code != 200:
        return 'Failed'
    else:
        solicitud = solicitud.json()
        return solicitud['importe_total_flete']



###################################################
# Crea un nuevo envio en CRAB
###################################################
def crea_envio_crab(correo, metodo_envio, orden, customer, orden_linea):

    correo_servicio = codigo_servicio_crab(orden.salientes, orden.courier_coordinar_roundtrip, orden.customer_zipcode)
    if correo_servicio == "Sin Cobertura":
         return 'Failed'

    url = "https://crab.epresis.com/api/v2/guias.json"

    headers = {
     'Content-Type': 'application/json'
    }

    if orden.courier_coordinar_roundtrip == True and orden.salientes == 'Si':
        observaciones = "Retiro + Entrega"
    #    correo_servicio = "118"
    else: 
        observaciones = "Retiro"
    #    correo_servicio = "110"

    solicitud_tmp = {
        "api_token": correo.cliente_apikey, # viene de envios
        "codigo_sucursal": metodo_envio.correo_sucursal, # viene de CONF_metodo_envio
        "codigo_servicio": correo_servicio, # "LI" viene de CONF_metodo_envio
        "remito": orden.order_number,
        "isInversa": True,
        "observaciones": observaciones,
        "tipo_operacion": "ENTREGA PAQUETERIA",
        "canal": "BORIS",
        "internacional" : False,
	    "is_urgente": False,

        "comprador": {
            "destinatario": customer.name,
            "horario": "", # ver nota del cliente
            "calle": orden.customer_address,
            "altura": orden.customer_number,
            "piso": orden.customer_floor,
            "localidad": orden.customer_locality,
            "provincia": orden.customer_province,
            "cp":orden.customer_zipcode,
            "email": customer.email,
            "celular": customer.phone,
            "cuit": customer.identification,
            "contenido": ""
        },
       
    }

    items_envio = []
    precio_total_envio = 0
    
    for i in orden_linea:
        precio_total_envio += i.precio
        items_envio.append (   
        {
            "bultos": i.accion_cantidad,
            "peso": i.peso,
            "descripcion": i.name,
            "dimensiones": {
                "alto": i.alto,
                "largo": i.largo,
                "profundidad": i.profundidad
            }   
        }
        )
    
    solicitud_tmp['productos'] = items_envio
    solicitud_tmp["valor_declarado"] = precio_total_envio

    payload = json.dumps(solicitud_tmp)
       
    solicitud = requests.request("POST", url, headers=headers, data=payload)
   
    if solicitud.status_code != 200:
        flash('Hubo un error al generar la guia. Codigo {} - {}'.format(solicitud.status_code, solicitud.content))
        return "Failed"
    else:
        solicitud = solicitud.json()
        enviar_etiqueta_crab(correo, solicitud, customer, orden, metodo_envio, observaciones)
        return solicitud



def enviar_etiqueta_crab(correo, solicitud, customer, orden, metodo_envio, observaciones):
    ####################################################################
    # las etiquetas se envia:
    # a FASTMAIL + CLIENTE si solo es RETIRO
    # al MERCHANT si es Retiro + Entrega
    ####################################################################
    company = Company.query.filter_by(store_id=current_user.store).first()

    if observaciones == "Retiro + Entrega":
        mailto = [company.admin_email]
    
    if observaciones == "Retiro":
        correo_descripcion = correos.query.get('CRAB').correo_mail
        #mailto = 'ssuarez@fastmail.com.ar'
        mailto = [correo_descripcion,customer.email]
    
    url = "https://crab.epresis.com/api/v2/print_etiquetas.json"

    headers = {
     'Content-Type': 'application/json'
    }

    data = {
        "api_token": correo.cliente_apikey,
        "ids": solicitud['guia']
    }
    
    payload = json.dumps(data)
    label_tmp = requests.request("POST", url, headers=headers, data=payload)
    if label_tmp.status_code !=200:
        flash('no se pudo generar la etiqueta')
        flash ("codigo: {} - Error: {}".format(label_tmp.status_code, label_tmp.content))
        return
    else:
        label = label_tmp.content
       
    
    flash('Se generó la orden {} . Se envia la etiqueta por correo a {}'.format(solicitud['guia'], mailto))
    
    send_email('se ha generado una etiqueta para la solicitud '+str(orden.order_number), 
        sender=(company.communication_email_name, company.communication_email),
        recipients=mailto, 
        reply_to = company.admin_email,
        text_body=render_template('email/etiqueta_enviada.txt',
                                        company=company, customer=customer, order=orden, envio=orden.courier_method, label=label),
                                        html_body=render_template('email/etiqueta_enviada.html',
                                        company=company, customer=customer, order=orden, envio=orden.courier_method, label=label, instrucciones=metodo_envio.instrucciones_entrega), 
                                        attachments=[('etiqueta.pdf', 'application/pdf',
                                            label)], 
                                        sync=False)


def ver_etiqueta_crab(guia):
    correo_tmp = 'CRAB'+str(current_user.store)
    correo = CONF_correo.query.get(correo_tmp)
    
    url = "https://crab.epresis.com/api/v2/print_etiquetas.json"

    headers = {
     'Content-Type': 'application/json'
    }

    data = {
        "api_token": correo.cliente_apikey,
        "ids": guia
    }
    
    payload = json.dumps(data)
    label_tmp = requests.request("POST", url, headers=headers, data=payload)
   
    return label_tmp

def codigo_servicio_crab(salientes, roundtrip, postalcode):
    #### CAMBIO ##### revisar para el interior hay que generar 2 ordenes
    cordon_tmp = Codigos_postales.query.get(postalcode)
    if not cordon_tmp:
        return "Sin Cobertura"
   
    cordon = cordon_tmp.cordon
    
    if salientes == 'Si' and roundtrip == True: 
        
        if cordon == "AMBA":
            return 118

        #if CORDON 3: a
        #119

        #if INTERIOR 1
        #120

        #If INTERIOR 2
        #121

        #if PATAGONIA 1
        #122

        #if PATAGONIA 2
        #123

        #if TIERRA DEL FUEGO:
        #124

        return "A cotizar"
        
    if salientes == 'No' or roundtrip == False:
       
        if cordon == "AMBA":
            return 110

        # if CORDON 3	
        #     111
        #if INTERIOR 1	
        # 112
        #if INTERIOR 2	
        # 114
        #if PATAGONIA 1	
        # 115
        #if PATAGONIA 2	
        # 116
        #if TIERRA DEL FUEGO	
        # 117

        return "A cotizar"

