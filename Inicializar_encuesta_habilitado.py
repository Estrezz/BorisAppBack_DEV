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

        x.encuesta = False
        x.habilitado = True

        x.orden_iniciada_asunto = 'Tu orden ha sido iniciada'
        x.orden_confirmada_asunto = 'Tu orden ha sido confirmada'
        x.orden_rechazada_asunto = 'Tu orden ha sido rechazada'
        x.orden_aprobada_asunto = 'Tu orden ha sido aprobada'
        x.cupon_generado_asunto = 'Hemos generado tu cupón'
        x.orden_finalizada_asunto = 'El procesamiento de tu orden ha finalizado'

        db.session.commit()


        print ('Finalizado '+str(x.store_id)+' '+x.store_name)

                
        


  




