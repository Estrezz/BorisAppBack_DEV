from app import db, create_app
from app.models import Company, Customer, Order_header, Order_detail
from flask import current_app
import csv
import datetime
import sys

app=create_app()
with app.app_context():
    
    if len(sys.argv) < 2:
        print('Debe indicar la fecha desde la cual desea obtener los datosEj: generar_encuestas.py 2021-10-01')
        sys.exit()
    else:
        fecha_desde=sys.argv[1]
    
    companies = Company.query.all()
    with open('logs/app/encuestas.csv', 'w+', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['Email', 'Name', 'Date', 'Brand']
        writer.writerow(header)
        for x in companies:
            if x.encuesta == True:
                #print(x.store_name+' No esta')
                continue

            ## orden = Order_header.query.filter_by(store = x.store_id).all()
            orden_filtrado = Order_header.query.filter_by(store = x.store_id).filter(Order_header.date_creation >= fecha_desde).all() 
            
            
            for i in orden_filtrado:
        
                cliente = Customer.query.get(i.customer_id)
                row = [cliente.email, cliente.name, i.date_creation.strftime('%d/%m/%Y'), x.store_name] 
                        
                # write a row to the csv file
                writer.writerow(row)

    # close the file
    f.close()

