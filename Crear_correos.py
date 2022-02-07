from sqlalchemy import false
from app import db, create_app
from app.models import correos, metodos_envios
from flask import current_app



app=create_app()
with app.app_context():
      
    ##### Datos Maestros #########

    ################# ALTA CORREOS #####################################################
    print ('Dando de alta correos')
    correoFastmail = correos(
                       correo_id = 'FAST',
                       correo_descripcion = 'Fastmail',
                       correo_mail ='ssuarez@fastmail.com.ar'
                   ) 
    db.session.add(correoFastmail)   


    ################# ALTA METODOS ENVIO ###################################################
    print ('Dando de alta Metodos de Envio')
    
    metodoDomicilio = metodos_envios(
                       metodo_envio_id = 'Domicilio',
                       metodo_envio_descripcion = 'Retiro por el domicilio del cliente',
                       carrier = True,
                       direccion_obligatoria = True,
                       icon = 'bi bi-house-fill'
                   ) 
    db.session.add(metodoDomicilio)

    db.session.commit()

    




        


  




