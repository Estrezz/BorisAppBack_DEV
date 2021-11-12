from app import db, create_app
import requests
from app.models import Company
import sys
import csv

app=create_app()
with app.app_context():
    fecha=sys.argv[1]
    companies = Company.query.all()
    with open('logs/app/datos_ordenes.csv', 'w+', newline='') as f:
        writer = csv.writer(f)
        header = ['Tienda', 'Nro_orden', 'Fecha_orden', 'Subtotal', 'Descuento', 'Shipping', 'Cliente', 'Provincia', 'Localidad', 'Codigo_Postal']
        writer.writerow(header)
        for x in companies:
            maspaginas = 1
            contador = 1   
            if x.store_id == '1':
                continue
            
            print ('Comenzando '+str(x.store_id)+' '+x.store_name) 

            while maspaginas != 0:   
                url = "https://api.tiendanube.com/v1/"+str(x.store_id)+"/orders?created_at_min="+str(fecha)+"&page="+str(contador)
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
                        row = [
                            x.store_id, r['number'], r['created_at'], r['subtotal'], r['discount'], 
                            r['shipping'], r['customer']['id'], r['shipping_address']['province'], 
                            r['shipping_address']['locality'], r['shipping_address']['zipcode'] ]
                        writer.writerow(row)
                    print(x.store_id, ('Page')+str(contador))
                    contador += 1
    f.close()
                    
