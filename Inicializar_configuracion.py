from app import db, create_app
from app.models import Company, CONF_boris, CONF_envios, CONF_motivos
from app.main.interfaces import inicializa_motivos, inicializa_parametros, inicializa_envios
from flask import current_app


app=create_app()
with app.app_context():


    companies = Company.query.all()
   
    for x in companies:
        print(x, x.store_id)
        if x.store_id == '1631829':
            print('Configuracion especial:',x)
            if CONF_boris.query.filter_by(store=x.store_id).first():
                continue
            else:
                inicializa_motivos(x)
                inicializa_parametros(x)
                inicializa_envios(x)

        


  




