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
    productos = []
    productos_tmp = []

    # ########################################################### 
    # Genera datos de tiendas
    # ###########################################################
    with open('logs/app/datos_tiendas.csv', 'w+', newline='') as file_tiendas:
        writer = csv.writer(file_tiendas)
        header = ['Plataforma', 'Tienda_Id', 'Tienda_Nombre', 'Fecha de Inicio', 'Demo', 'Rubro']
        writer.writerow(header)

        for c in companies:
            row = [c.platform, c.store_id, c.store_name, c.start_date, c.demo_store, c.rubro_tienda]
            writer.writerow(row)

    file_tiendas.close()


    # ###########################################################
    # Genera datos de Ventas 
    # ###########################################################
    with open('logs/app/datos_ordenes.csv', 'w+', newline='') as f:
        writer = csv.writer(f)
        header = ['Tienda', 'Nro_orden', 'Fecha_orden', 'Status','Producto','Cantidad', 'Subtotal', 'Descuento', 'Shipping', 'Cliente', 'Provincia', 'Localidad', 'Codigo_Postal']
        writer.writerow(header)


        for x in companies:
            maspaginas = 1
            contador = 1  

            #############################################################3
            # Filtra Tiendas que tengan PLAN C o PLAN_D
            # ###########################################################
            if (x.plan_boris != 'Plan_C') and (x.plan_boris != 'Plan_D'):
                continue
            
            print ('Comenzando '+str(x.store_id)+' '+x.store_name) 

            while maspaginas != 0:   
                url = "https://api.tiendanube.com/v1/"+str(x.store_id)+"/orders?created_at_min="+str(fecha_desde)+"&created_at_max="+str(fecha_hasta)+"&page="+str(contador)
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

                        for p in r['products']:
                            row = [
                                x.store_id, r['number'], r['created_at'],r['status'], p['product_id'], p['quantity'], r['subtotal'], r['discount'], 
                                r['shipping'], cliente, r['shipping_address']['province'], 
                                r['shipping_address']['locality'], r['shipping_address']['zipcode'] ]
                            writer.writerow(row)

                             #############################################################3
                             # Filtra Tiendas que tengan PLAN_D
                             # ###########################################################
                            if x.plan_boris != 'Plan_D':
                                continue
                            else:
                                if p['product_id'] not in productos_tmp:
                                    url = "https://api.tiendanube.com/v1/"+str(x.store_id)+"/products/"+str(p['product_id'])
                                    payload={}
                                    headers = {
                                        'Content-Type': 'application/json',
                                        'Authentication': x.platform_token_type+' '+x.platform_access_token
                                    }
                                    response_prodcuto = requests.request("GET", url, headers=headers, data=payload).json()
                                
                                    if 'brand' in response_prodcuto.keys(): 
                                        productos.append([x.store_id, p['product_id'], response_prodcuto['brand'].upper()])
                                    else:
                                        productos.append([x.store_id, p['product_id'], 'Sin Marca'])

                                    productos_tmp.append(p['product_id'])

                    print(x.store_id, ('Page')+str(contador))
                    contador += 1
    f.close()


    with open('logs/app/datos_productos.csv', 'w+', newline='') as file_producto:
        writer = csv.writer(file_producto)
        header = ['Tienda', 'Producto', 'Marca']
        writer.writerow(header)
        for p in productos:
            row = [p[0],p[1],p[2]]
            writer.writerow(row)
    file_producto.close()
            

