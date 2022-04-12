from app import db, create_app
from app.models import CONF_motivos, Company
import csv

app=create_app()

with app.app_context():
    companies = Company.query.all()
    motivos = CONF_motivos.query.all()
    
    # ########################################################### 
    # Genera datos de tiendas
    # ###########################################################
    with open('logs/app/datos_tiendas.csv', 'w+', newline='', encoding='utf-8') as file_tiendas:
        writer = csv.writer(file_tiendas)
        header = ['Plataforma', 'Tienda_Id', 'Tienda_Nombre', 'Fecha de Inicio', 'Demo', 'Rubro']
        writer.writerow(header)

        for c in companies:
            row = [c.platform, c.store_id, c.store_name, c.start_date, c.demo_store, c.rubro_tienda]
            writer.writerow(row)

    file_tiendas.close()

    ################## Genera Base de Motivos ####################################################
    #with open('logs/app/datos_motivos.csv', 'w+', newline='') as file_motivos:
    #    writer = csv.writer(file_motivos)
    #    header = ['motivo', 'tipo_motivo']
    #
    #    writer.writerow(header)
    #
    #    for m in motivos:
    #        row = [m.motivo, m.tipo_motivo]
    #        writer.writerow(row)

    #file_motivos.close()

