from app import db, create_app
from app.models import Company, CONF_boris, CONF_envios, CONF_motivos
from app.main.interfaces import inicializa_motivos, inicializa_parametros, inicializa_envios
from flask import current_app
import json


app=create_app()
with app.app_context():


    companies = Company.query.all()
   
    for x in companies:
        if x.store_id == '1':
            continue
        print ('Comenzando '+str(x.store_id)+' '+x.store_name)

        if CONF_boris.query.filter_by(store=x.store_id).first():
            print ('Finalizado '+str(x.store_id)+' '+x.store_name+' - Ya tenia CONFIG')   
        else :
            if x.store_id == '138327':
                file = 'Abundancia.JSON'
            else:
                file = str(x.store_id)+'.json'
                
            with open('logs/tmp/'+file, 'r') as f:
                table = json.loads(f.read())

                ##### Otros #########
                x.correo_cost = table['shipping']
                db.session.commit()

                #### CONF_BORIS #####
                if 'cupon' in table.keys():
                    if table['cupon'] == 'Si':
                        cambio_cupon_tmp = 1
                    else: 
                        cambio_cupon_tmp = 0
                    cambio_opcion_cupon_tmp = table['textos']['elegir_opcion_cambio_cupon']
                else: 
                    cambio_cupon_tmp = 0
                    cambio_opcion_cupon_tmp = 'Seleccioná esta opción para obtener un cupón de crédito en nuestra tienda'

                if 'otracosa' in table.keys():
                    if table['otracosa'] == 'Si':
                        cambio_otracosa_tmp = 1
                    else: 
                        cambio_otracosa_tmp = 0
                    cambio_opcion_otracosa_tmp = table['textos']['elegir_opcion_otra_cosa']
                else: 
                    cambio_otracosa_tmp = 0
                    cambio_opcion_otracosa_tmp = 'Elegí en nuestra tienda el artículo que querés, ingresa el nombre y presion buscar'

                unParametro = CONF_boris(
                    store = x.store_id,
                    ventana_cambios = table['politica']['ventana_cambio'],
                    ventana_devolucion = table['politica']['ventana_devolucion'],
                    cambio_cupon = cambio_cupon_tmp,
                    cambio_otra_cosa = cambio_otracosa_tmp,
                    cambio_opcion = table['textos']['elegir_opcion_cambio'],
                    cambio_opcion_cupon = cambio_opcion_cupon_tmp,
                    cambio_opcion_otra_cosa = cambio_opcion_otracosa_tmp
                )
                db.session.add(unParametro)
                db.session.commit()

                #### Motivos ########
                counter = 0
                for m in table['motivos']:
                    if m == 'Es grande' or m == 'Es chico':
                        tipo_motivo_tmp = 'Talle'
                    else: 
                        if m == 'Mala calidad':
                            tipo_motivo_tmp = 'Calidad'
                        else: 
                            if m == 'No gusta color':
                                tipo_motivo_tmp = 'Color'
                            else: 
                                if m == 'No calza bien':
                                    tipo_motivo_tmp = 'Calce'
                                else:
                                    tipo_motivo_tmp = 'Sin definir'

                    motivoUno = CONF_motivos(
                    store = x.store_id,
                    id_motivo = counter,
                    motivo = m,
                    tipo_motivo = tipo_motivo_tmp
                    )
                    db.session.add(motivoUno)
                    counter = counter +1
                db.session.commit()

                ##### Envios ########
                ##### MANUAL ##########################################################3
                if 'manual' in table['envio']:     
                    manual = CONF_envios(
                        store = x.store_id,
                        metodo_envio = 'manual',
                        habilitado = 1,
                        titulo_boton = table['textos']['boton_envio_manual'],
                        descripcion_boton = table['textos']['boton_envio_manual_desc']
                    )    
                else: 
                    manual = CONF_envios(
                        store = x.store_id,
                        metodo_envio = 'manual',
                        habilitado = 0,
                        titulo_boton = 'Traer la orden a nuestro local',
                        descripcion_boton = 'Acercanos el/los productos a nuestros locales/depósito'
                    )

                db.session.add(manual)

                ##### COORDINAR ##########################################################3
                if 'coordinar' in table['envio']:     
                    coordinar = CONF_envios(
                        store = x.store_id,
                        metodo_envio = 'coordinar',
                        habilitado = 1,
                        titulo_boton = table['textos']['boton_envio_coordinar'],
                        descripcion_boton = table['textos']['boton_envio_coordinar_desc']
                    )
                    db.session.add(manual)
                else: 
                    coordinar = CONF_envios(
                        store = x.store_id,
                        metodo_envio = 'coordinar',
                        habilitado = 0,
                        titulo_boton = 'Coordinar método de retiro',
                        descripcion_boton = 'Coordiná con nosotros el método de envío que te quede mas cómodo'
                    )
                db.session.add(coordinar)

                ##### RETIRO ##########################################################3
                if 'retiro' in table['envio']:     
                    retiro = CONF_envios(
                        store = x.store_id,
                        metodo_envio = 'retiro',
                        habilitado = 1,
                        titulo_boton = table['textos']['boton_envio_retiro'],
                        descripcion_boton = table['textos']['boton_envio_retiro_desc']
                    )
                    db.session.add(retiro)
                else: 
                    retiro = CONF_envios(
                        store = x.store_id,
                        metodo_envio = 'retiro',
                        habilitado = 0,
                        titulo_boton = 'Retirar en tu domicilio',
                        descripcion_boton = 'Un servicio de correo pasara a buscar los productos por tu domicilio'
                    )
                db.session.add(retiro)

                db.session.commit()
                print ('Finalizado '+str(x.store_id)+' '+x.store_name)

                
        


  




