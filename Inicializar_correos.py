from sqlalchemy import false
from app import db, create_app
from app.models import Company, CONF_envios, correos, metodos_envios,CONF_metodos_envios 
import requests
from flask import current_app
import json


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

    correoNone = correos(
                       correo_id = 'NONE',
                       correo_descripcion = 'None'
                   )    
    db.session.add(correoNone)


    ################# ALTA METODOS ENVIO ###################################################
    print ('Dando de alta Metodos de Envio')

    metodoManual = metodos_envios(
                       metodo_envio_id = 'Manual',
                       metodo_envio_descripcion = 'El cliente se ocupa de llevar los productos',
                       carrier = False,
                       direccion_obligatoria = False,
                       icon = 'bi bi-handbag'
                   ) 
    db.session.add(metodoManual)

    metodoCoordinar = metodos_envios(
                       metodo_envio_id = 'Coordinar',
                       metodo_envio_descripcion = 'Metodo preferido pro el Merchant',
                       carrier = False,
                       direccion_obligatoria = True,
                       icon = 'bi bi-headphones'
                   ) 
    db.session.add(metodoCoordinar)

    metodoDomicilio = metodos_envios(
                       metodo_envio_id = 'Domicilio',
                       metodo_envio_descripcion = 'Retiro por el domicilio del cliente',
                       carrier = True,
                       direccion_obligatoria = True,
                       icon = 'bi bi-house-fill'
                   ) 
    db.session.add(metodoDomicilio)

    db.session.commit()

    ################# CONFIGURACION DE METODOS EN ENVIO EN COMPANIES #####################################################
    companies = Company.query.all()
    
    print('Configurando tiendas')

    url="https://devfront.borisreturns.com/empresa_json?clave="+'envio'+"&key="+'otros'
    headers = {
        'Content-Type': 'application/json'
    }

    for x in companies:
        if x.store_id == '1':
            continue

        print ('Comenzando '+str(x.store_id)+' '+x.store_name)
        envios = CONF_envios.query.filter_by(store=x.store_id).all()
        
        for e in envios:
            if e.metodo_envio == 'manual':
                manual = CONF_metodos_envios( 
                        store = x.store_id,
                        metodo_envio_id = 'Manual',
                        habilitado = e.habilitado,
                        titulo_boton = e.titulo_boton,
                        descripcion_boton = e.descripcion_boton,
                        correo_id = "",
                        correo_descripcion = "",
                        correo_servicio = "",
                        correo_sucursal = "",
                        costo_envio = 'Merchant',
                        instrucciones_entrega = x.envio_manual_note
                )    
            
                db.session.add(manual)
                print('se dio de alta manual')


            if e.metodo_envio == 'coordinar':
                coordinar = CONF_metodos_envios( 
                        store = x.store_id,
                        metodo_envio_id = 'Coordinar',
                        habilitado = e.habilitado,
                        titulo_boton = e.titulo_boton,
                        descripcion_boton = e.descripcion_boton,
                        correo_id = "",
                        correo_descripcion = "",
                        correo_servicio = "",
                        correo_sucursal = "",
                        costo_envio = 'Merchant',
                        instrucciones_entrega = x.envio_coordinar_note
                )    
            
                db.session.add(coordinar)
                print('se dio de alta coordinar')

            db.session.commit()

       
        ########### Actualizar JSON ######################
        print('actualizando JSON')

        metodos_tmp = CONF_metodos_envios.query.filter_by(store=x.store_id).all() 
        metodos=[]
        for m in metodos_tmp:
            metodo_master = metodos_envios.query.get(m.metodo_envio_id)
            unMetodo_tmp = {"metodo_envio_id" : m.metodo_envio_id,
                            "icon": metodo_master.icon,
                            "boton_titulo": m.titulo_boton,
                            "boton_descripcion": m.descripcion_boton,
                            "direccion_obligatoria": metodo_master.direccion_obligatoria,
                            "carrier":metodo_master.carrier,
                            "correo_id": m.correo_id,
                            "costo_envio": m.costo_envio}
            metodos.append(unMetodo_tmp)
  
        data = {
                "store_id" : x.store_id,
                'envio' : metodos,
        }
                
        solicitud = requests.request("POST", url, headers=headers, data=json.dumps(data))               
                    
        print ('Finalizado '+str(solicitud.status_code)+str(x.store_id)+' '+x.store_name)





        


  




