from app import db, create_app
import requests
from app.models import Company
from datetime import date
import sys
import csv

app=create_app()
with app.app_context():
    if len(sys.argv) < 2:
        print('Debe indicar la fecha desde y, si se desea, la fecha hasta Ej: generar_datos.py 2021-10-01 2021-10-29')
        sys.exit()
    else:
        fecha_desde=sys.argv[1]
    if len(sys.argv) > 2:
        fecha_hasta=sys.argv[2]
    else:
        fecha_hasta = date.today()
    
    companies = Company.query.all()
    with open('logs/app/datos_ordenes.csv', 'w+', newline='') as f:
        writer = csv.writer(f)
        header = ['Tienda', 'Nro_orden', 'Fecha_orden', 'status','Subtotal', 'Descuento', 'Shipping', 'Cliente', 'Provincia', 'Localidad', 'Codigo_Postal']
        writer.writerow(header)
        for x in companies:
            maspaginas = 1
            contador = 1   
            if x.store_id == '1':
                continue
            
            print ('Comenzando '+str(x.store_id)+' '+x.store_name) 

            while maspaginas != 0:   
                url = "https://api.tiendanube.com/v1/"+str(x.store_id)+"/orders?created_at_min="+str(fecha_desde)+"&created_at_max="+str(fecha_hasta)+"&page="+str(contador)
                #url = "https://api.tiendanube.com/v1/"+str(x.store_id)+"/orders?created_at_min="+str('2021-10-01')+"&fields=id,number,created_at&page="+str(contador)
                payload={}
                headers = {
                    'Content-Type': 'application/json',
                    'Authentication': x.platform_token_type+' '+x.platform_access_token
                }
                response_tmp = requests.request("GET", url, headers=headers, data=payload)

                if response_tmp.status_code != 200:
                    maspaginas = 0
                else:
                    response = response_tmp.json()
                    for r in response:
                        if r['customer']:
                            cliente = r['customer']['id']
                        else: 
                            cliente = '000'

                        row = [
                            x.store_id, r['number'], r['created_at'],r['status'], r['subtotal'], r['discount'], 
                            r['shipping'], cliente, r['shipping_address']['province'], 
                            r['shipping_address']['locality'], r['shipping_address']['zipcode'] ]
                        writer.writerow(row)
                    print(x.store_id, ('Page')+str(contador))
                    contador += 1
    f.close()

