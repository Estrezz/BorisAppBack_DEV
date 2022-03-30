from app import db, create_app
from app.models import Company, Customer, Order_header, Order_detail
from sqlalchemy import create_engine
from flask import current_app
#import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd
import csv

app=create_app()
with app.app_context():

    # to dreate df from database
    #cnx = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI']).connect()
    #df = pd.read_sql_table('company', cnx)
    #print(df)

    companies = Company.query.all()
    with open('logs/app/datos.csv', 'w+', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['Plataforma', 'Tienda_Id', 'Tienda_Nombre', 'Fecha de Inicio', 'Demo', 'Rubro',  'Solicitud_Nro', 'Solicitud_Id', 'Solicitud_Fecha_Creacion', 'Solicitud_Fecha_Cierre','Estado','Sub_Estado','Estado_Descripcion','Codigo_Postal','Ciudad','Provincia','Correo_coordinar','Roundtrip','Metodo_Envio', 'Metodo_Pago','Tarjeta','Accion','Motivo','Cambiar_por', 'Cambiar_cantidad','Cambiar_por_descripcion','Linea_Estado','Linea_Fecha_estado','Monto_a_devolver','Monto_devuelto','Produto_id', 'Producto_descripcion', 'Cliente_Documento','Cliente_Mail','Cliente' ]
        writer.writerow(header)
        for x in companies:
            orden = Order_header.query.filter_by(store = x.store_id).all()
            for i in orden:
                linea = Order_detail.query.filter_by(order=i.id).all()
                cliente = Customer.query.get(i.customer_id)
                for l in linea:
                    row = [
                        ### Company
                        x.platform, x.store_id, x.store_name, x.start_date, x.demo_store, x.rubro_tienda,
                        ### order
                        i.order_number, i.id, i.date_creation, i.date_closed, i.status, i.sub_status,
                        i.status_resumen, i.customer_zipcode, i.customer_city, i.customer_province, 
                        i.metodo_envio_correo, i.courier_coordinar_roundtrip, i.courier_method,
                        i.payment_method, i.payment_card,
                        ### detail
                        l.accion, l.motivo, l.accion_cambiar_por, l. accion_cantidad, l.accion_cambiar_por_desc, l.gestionado,
                        l.fecha_gestionado, l.monto_a_devolver, l.monto_devuelto,
                        l.prod_id, l.name,
                        #### falta info de los productos producto y desc de cambiar por
                        #### CLiente
                        cliente.identification, cliente.email, cliente.name  ]
            
                    # write a row to the csv file
                    writer.writerow(row)

                # close the file
    f.close()

