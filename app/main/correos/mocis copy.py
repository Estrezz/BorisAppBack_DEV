import requests
import json
import base64

from flask import flash, render_template, Response
from app.email import send_email
from flask_login import current_user
from app.models import CONF_correo, Codigos_postales, Company, correos


#### Cotiza un Envio 
def cotiza_envio_mocis(data, datos_correo):
    token = get_token_mocis(datos_correo.cliente_apikey, datos_correo.cliente_apisecret)
    url = "https://mocis.akeron.net/api/v1/shipping/price"
        
    headers = {
     'Authorization': 'Bearer ' + token
    }

    solicitud_tmp = { "postal_code": data['from']['postalCode'] }

    payload = json.dumps(solicitud_tmp)
    
    solicitud = requests.request("POST", url, headers=headers, data=payload)
    if solicitud.status_code != 200:
        return 'Failed'
    else:
        solicitud = solicitud.json()
        return solicitud['result'][0]['price'] ### Devuelve precio sin iva ['price_iva'] para obtener precio con IVA



###################################################
# Crea un nuevo envio en MOCIS
###################################################
def crea_envio_mocis(correo, metodo_envio, orden, customer, orden_linea):
    token = get_token_mocis(correo.cliente_apikey, correo.cliente_apisecret)
    envio_nro = ""

    #coordinadas = get_geolocation_mocis(orden.customer_zipcode, direccion, orden.customer_locality, token)
    #provincia = get_provincia_mocis(orden.customer_province)
   
    #####################################################################################
    # Si se trata de un CAMBIO 
    # Se genera el ENVIO Y luego la Inversa utilizando el codigo de envio obtenido
    #####################################################################################
    if orden.courier_coordinar_roundtrip == True and orden.salientes == 'Si':
        url = "https://mocis.akeron.net/api/v1/shipping/new"

        headers = {
         'Authorization': 'Bearer ' + token,
         'Content-Type': 'application/json'
        }

       
        # Caclual peso total del paquete
        kg = 0
        for i in orden_linea:
            if i.peso > 0:
                kg += i.peso

        envio_tmp = {
            "receives": customer.name,
            "address":  orden.customer_address +' '+ orden.customer_number +' '+ orden.customer_floor,
            "location": orden.customer_locality,
            "reference": "", # Ver nota del cliente
            "postal_code": orden.customer_zipcode,
            "kgs": kg,
            "Bultos": "1",
            "telephone": customer.phone,
            "email": customer.email        
        }

        payload = json.dumps(envio_tmp) 
        envio_nro_tmp = requests.request("POST", url, headers=headers, data=payload).json()
        
        if envio_nro_tmp['status'] == False:
            flash(f'Hubo un error al generar la guía. Código {envio_nro_tmp["msg"]}')
            return "Failed"
        envio_nro = envio_nro_tmp['result'][0]
        type_inversa = "2" #Setea el tipo de inversa en CAMBIO
     
    else: 
        #################### Si se trata de un DEVOLUCION #######################
        type_inversa = "1" # Setea el tipo de Inversa en SOLO INVERSA

    # Genera logistica inversa
    guia_envio = crea_inversa_mocis(correo, metodo_envio, orden, customer, orden_linea, token, type_inversa, envio_nro)
    
    return guia_envio, envio_nro


#################################################################################3
# Crea un nuevo envio de LOGISTICA INVERSA en MOCIS
###################################################################################
def crea_inversa_mocis(correo, metodo_envio, orden, customer, orden_linea, token,  type_inversa, envio_nro):

    cambio_shipping_code = envio_nro if type_inversa == "2" else ""

    url_inversa = "https://mocis.akeron.net/api/v1/shipping_inversa/new"

    headers = {
     'Authorization': 'Bearer ' + token,
     'Content-Type': 'application/json',
    }

    retiro_tmp = {
        # Uso los datos del comprador para el origen
        "origen":{
            "provincia": "",
            "postal_code": orden.customer_zipcode,
            "address": orden.customer_address +' '+ orden.customer_number +' '+ orden.customer_floor,
            "location": orden.customer_locality,
            "reference": "", # Ver nota del cliente
            "sender": customer.name,
            "telephone": customer.phone,
            "email":customer.email      
        },
        "destino":{
            "provincia": "",
            "postal_code": "C1439",
            "address": "Calle falsa 123",
            "location": "Caballito",
            "reference": "Departamento 2D",
            "receives": "Juan",
            "telephone": "123123123",
            "email":"test@test.com"
        },
        "type_inversa": type_inversa, # revisar
        "bultos":"1", # revisar
        "kgs":"1", # revisar
        "cambio_shipping_code": cambio_shipping_code, 
        "devolucion_shipping_code": "" 
    }

    payload = json.dumps(retiro_tmp)
    guia_envio_tmp = requests.request("POST", url_inversa, headers=headers, data=payload)
   
    if guia_envio_tmp.status_code != 200:
        flash('Hubo un error al generar la guia. Codigo {} - {}'.format(guia_envio_tmp.status_code, guia_envio_tmp.content))
        return "Failed"
    else:
        guia_envio = guia_envio_tmp.json()

        if guia_envio['status'] == False:
            flash(f'Hubo un error al generar la guía. Código {guia_envio["msg"]}')
            return "Failed"
        else:
            precio = obtener_precio_envio_mocis(guia_envio['result'][0], token)
            #enviar_etiqueta_mocis(correo, solicitud, customer, orden, metodo_envio, observaciones)
            guia = {
                "guia": guia_envio['result'][0],
                "importe": precio
            }
            return guia
        

def obtener_precio_envio_mocis(guia, token):
    url = "https://mocis.akeron.net/api/v1/shipping/state/"+guia

    headers = {
     'Authorization': 'Bearer ' + token
    }
    payload = {}
    orden_tmp = requests.request("GET", url, headers=headers, data=payload)
    orden = orden_tmp.json()
   
    return orden['result'][0]['price']


def enviar_etiqueta_mocis(correo, solicitud, customer, orden, metodo_envio, observaciones):
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


def ver_etiqueta_mocis(guia):
    
    correo_tmp = 'MOCIS'+str(current_user.store)
    correo = CONF_correo.query.get(correo_tmp)
    token = get_token_mocis(correo.cliente_apikey, correo.cliente_apisecret)
    
    url = f"https://mocis.akeron.net/api/v1/shipping/print/label/{guia}"

    headers = {'Authorization': 'Bearer ' + token }
    payload = {}
    
    label_tmp = requests.request("GET", url, headers=headers, data=payload).json()
    guia = label_tmp["result"][0]["pdf"]
    pdf_path = f"https://mocis.akeron.net/api{guia}"
    pdf_response = requests.get(pdf_path)
    
    response = Response(pdf_response.content, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline'
    return response

    

########## Obtiene Token de Autorización 
def  get_token_mocis(apikey, apisecret):
    url = "https://mocis.akeron.net/api/v1/auth/token"

    headers = {}

    data = {
        'client_api': apikey,
        'client_secret': apisecret
    }
    
    result = requests.request("POST", url, headers=headers, data=data)
    
    token_tmp = result.json()
    token = token_tmp['result'][0]['api_token']
   
    return token


########## Obtiene Token de Autorización 
def  get_geolocation_mocis(postal_code, address, location, token):
    url = "https://mocis.akeron.net/api/v1/shipping/geolocation"

    headers = {
     'Authorization': 'Bearer ' + token
    }

    data = {
        'postal_code': postal_code,
        'address': address,
        'location': location
    }
    
    result = requests.request("POST", url, headers=headers, data=data).json()
    
    location = {
        'lat':result['result'][0]['lat'],
        'lng':result['result'][0]['lng'],
        'address':result['result'][0]['address']
    }
    return location
    

