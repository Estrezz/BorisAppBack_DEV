import requests
import json
from flask import session, flash, current_app,render_template
from app.email import send_email
from flask_login import current_user

def toready_moova(orden,company,customer):
    if company.correo_test == False:
        url = "https://api-prod.moova.io/b2b/shippings/"+str(orden.courier_order_id)+"/READY"
        url_label = "https://api-prod.moova.io/b2b/shippings/"+str(orden.courier_order_id)+"/label"
        headers = {
            'Authorization': company.correo_apikey,
            'Content-Type': 'application/json',
        }
        params = {'appId': company.correo_id}
        api_usada ='PROD'
    else :
        url = "https://api-dev.moova.io/b2b/shippings/"+str(orden.courier_order_id)+"/READY"
        url_label = "https://api-dev.moova.io/b2b/shippings/"+str(orden.courier_order_id)+"/label"
        headers = {
            'Authorization': company.correo_apikey_test,
            'Content-Type': 'application/json',
        }
        params = {'appId': company.correo_id_test}
        api_usada = 'DEV'

    solicitud = requests.request("POST", url, headers=headers, params=params)
    if solicitud.status_code != 201:
        if solicitud.status_code == 409:
            flash('Revise y corrija la dirección en la página del correo. Error {}'.format(solicitud.status_code))
            return 'Fail'
        flash('Hubo un problema con la generación del evío. Error {}'.format(solicitud.status_code))
        flash('url {} params{}'.format(url, params))
        return "Fail"
    else:
        if api_usada == 'DEV':
            flash('La orden se actualizó en Moova exitosamente - DEV')
        if api_usada == 'PROD':
            flash('La orden se actualizó en Moova exitosamente')
        label_tmp = requests.request("GET", url_label, headers=headers, params=params)
        label = label_tmp.json()['label']
            
        send_email('Tu orden ha sido confirmada', 
            #sender=current_app.config['ADMINS'][0], 
            sender=company.communication_email,
            recipients=[customer.email], 
            text_body=render_template('email/pedido_confirmado.txt',
                                        company=company, customer=customer, order=orden, envio=orden.courier_method, label=label),
                                        html_body=render_template('email/pedido_confirmado.html',
                                        company=company, customer=customer, order=orden, envio=orden.courier_method, label=label), 
                                        attachments=None, 
                                        sync=False)
        return "Success"