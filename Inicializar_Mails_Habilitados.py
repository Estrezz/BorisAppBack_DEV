from app import db, create_app
from app.models import Company, CONF_boris
from flask import current_app
from app.main.interfaces import actualiza_empresa_JSON


app=create_app()
with app.app_context():


    companies = Company.query.all()
   
    for x in companies:
        if x.store_id == '1':
            continue
        print ('Comenzando '+str(x.store_id)+' '+x.store_name)

        x.orden_solicitada_habilitado = True
        x.orden_confirmada_habilitado = True
        x.orden_rechazada_habilitado = True
        x.orden_aprobada_habilitado = True
        x.cupon_generado_habilitado = True
        x.orden_finalizada_habilitado = True

        db.session.commit()

        print ('Finalizado '+str(x.store_id)+' '+x.store_name)

                


  




