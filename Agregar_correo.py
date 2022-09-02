from sqlalchemy import false
from app import db, create_app
from app.models import correos, metodos_envios
from flask import current_app



app=create_app()
with app.app_context():
      
    ##### Datos Maestros #########

    ################# ALTA CORREOS #####################################################
    print ('Dando de alta correos')
    correo = correos(
                       correo_id = 'CRAB',
                       correo_descripcion = 'CRAB',
                       correo_mail ='erezzoni@yandex.com'
                   ) 
    db.session.add(correo)   


    ################# ALTA METODOS ENVIO ###################################################
    #print ('Dando de alta Metodos de Envio')
    #
    #metodoDomicilio = metodos_envios(
    #                   metodo_envio_id = 'Etiqueta',
    #                   metodo_envio_descripcion = 'Etiqueta Prepaga',
    #                   carrier = True,
    #                   direccion_obligatoria = True,
    #                   icon = 'bi bi-postage-fill'
    #               ) 
    #db.session.add(metodoDomicilio)

    db.session.commit()

    




        


  




