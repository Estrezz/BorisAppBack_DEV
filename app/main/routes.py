import requests
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, session, Response
from flask_login import current_user, login_required
from sqlalchemy import func
from app import db
from app.email import send_email
from app.main.forms import EditProfileForm, EditProfileCompanyForm, EditMailsCompanyForm, EditCorreoCompanyForm, EditParamsCompanyForm, EditMailsFrontCompanyForm
from app.main.tiendanube import generar_envio_tiendanube, autorizar_tiendanube, buscar_codigo_categoria_tiendanube, buscar_datos_variantes_tiendanube
from app.models import User, Company, Order_header, Customer, Order_detail, Transaction_log, categories_filter, CONF_boris, CONF_envios, CONF_motivos
from app.main.interfaces import crear_pedido, cargar_pedidos, resumen_ordenes, toReady, toReceived, toApproved, toReject, traducir_estado, buscar_producto, genera_credito, actualiza_empresa, actualiza_empresa_categorias, actualiza_empresa_JSON, loguear_transaccion, finalizar_orden, devolver_linea, actualizar_stock, devolver_datos_boton, incializa_configuracion
import json
import re
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
        session['current_empresa'] = empresa.store_name
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home', empresa_name=session['current_empresa'])


@bp.route('/mantenimiento', methods=['GET', 'POST'])
def mantenimiento():
    return render_template('mantenimiento.html', title='Home',  empresa_name=session['current_empresa'])


@bp.route('/verautorizado', methods=['GET', 'POST'])
def ver_autorizado():
    autorizacion = Company.query.filter_by(store_id=current_user.store).first_or_404()
    usuario = re.sub('[\s+]', '', autorizacion.store_name[0:8].strip())
    return render_template('autorizado.html', codigo='OK', usuario=usuario, store=autorizacion)
    


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user,  empresa_name=session['current_empresa'])


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit() 
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('edit_profile.html', title='Editar perfil',
                           form=form,  empresa_name=session['current_empresa'])


@bp.route('/company/<empresa_id>')
@login_required
def company(empresa_id):
    empresa = Company.query.filter_by(store_id=empresa_id).first_or_404()
    if CONF_boris.query.filter_by(store=empresa_id).first():
        configuracion = CONF_boris.query.filter_by(store=empresa_id).first_or_404()
    else: 
        (flash('No se encuentran los datos de Configuracion - ponerse en contacto con soporte@borisreturns.com'))
        return redirect(url_for('main.ver_ordenes', estado='all', subestado='all'))
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos, pestaña='tienda', empresa_name=session['current_empresa'])


## Actualiza datos de la Tienda #######################################
@bp.route('/edit_storeinfo', methods=['GET', 'POST'])
@login_required
def edit_storeinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    if request.method == "POST":
        accion = request.form.get('boton')

        if accion == "cancelar":
            #return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos, pestaña='tienda', empresa_name=session['current_empresa'])
            return redirect(url_for('main.company', empresa_id=current_user.store ))
            
        if accion == "guardar":
            store_name =  request.form.get('store_name')
            store_address = request.form.get('store_address')
            admin_email = request.form.get('admin_email')
            store_phone = request.form.get('store_phone')
            stock_vuelve_config = request.form.get('stock_vuelve_config')
            contact_name = request.form.get('contact_name')
            contact_email = request.form.get('contact_email')
            contact_phone = request.form.get('contact_phone')
            empresa.store_name = store_name
            empresa.store_address = store_address
            empresa.admin_email = admin_email
            empresa.store_phone = store_phone
            if stock_vuelve_config == 'on':
                empresa.stock_vuelve_config = True
            else:
                empresa.stock_vuelve_config = False
            empresa.contact_name = contact_name
            empresa.contact_email = contact_email
            empresa.contact_phone = contact_phone
            db.session.commit()

            status = actualiza_empresa(empresa)
            if status != 'Failed':
                flash('Los datos se actualizaron correctamente')
            else:
                flash('Se produjo un error {}'. format(status))

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos, pestaña='tienda', empresa_name=session['current_empresa'])
    


## Actualiza datos de la Empresa de Correo #######################################
@bp.route('/edit_carrierinfo', methods=['GET', 'POST'])
@login_required
def edit_carrierinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    if request.method == "POST":
        accion = request.form.get('boton')

        if accion == "cancelar":
            return redirect(url_for('main.company', empresa_id=current_user.store ))
            
        if accion == "guardar":
            correo_usado =  request.form.get('correo_usado')
            shipping_address = request.form.get('shipping_address')
            shipping_number = request.form.get('shipping_number')
            shipping_floor = request.form.get('shipping_floor')
            shipping_zipcode = request.form.get('shipping_zipcode')
            shipping_city = request.form.get('shipping_city')
            shipping_province = request.form.get('shipping_province')
            shipping_country = request.form.get('shipping_country')
            shipping_info = request.form.get('shipping_info')
            correo_test = request.form.get('correo_test')
            correo_cost = request.form.get('shipping')

            empresa.correo_usado = correo_usado
            empresa.shipping_address = shipping_address
            empresa.shipping_number = shipping_number
            empresa.shipping_floor = shipping_floor
            if correo_test == 'on':
                empresa.correo_test = True
            else:
                empresa.correo_test = False
            empresa.shipping_zipcode = shipping_zipcode
            empresa.shipping_city = shipping_city
            empresa.shipping_province = shipping_province
            empresa.shipping_country = shipping_country
            empresa.shipping_info = shipping_info

            if empresa.correo_cost != correo_cost:
                empresa.correo_cost = correo_cost
                actualiza_empresa_JSON(empresa, 'shipping', correo_cost, 'otros')

            db.session.commit()

            status = actualiza_empresa(empresa)
            if status != 'Failed':
                flash('Los datos se actualizaron correctamente')
            else:
                flash('Se produjo un error {}'. format(status))
            
    return render_template('company.html', empresa=empresa, configuracion=configuracion,  envios=envios, motivos=motivos, pestaña='carrier', empresa_name=session['current_empresa'])


## Actualiza datos para configuración del portal  #######################################
@bp.route('/edit_portalinfo', methods=['GET', 'POST'])
@login_required
def edit_portalinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    if request.method == "POST":
        accion = request.form.get('boton')

        if accion == "cancelar":
            return redirect(url_for('main.company', empresa_id=current_user.store ))
            
        if accion == "guardar":
            param_logo = request.form.get('param_logo')
            param_fondo = request.form.get('param_fondo')
            ventana_cambios = request.form.get('ventana_cambios')
            ventana_devolucion = request.form.get('ventana_devolucion')
            cambio_otra_cosa = request.form.get('cambio_otra_cosa')
            cambio_cupon = request.form.get('cambio_cupon')
            cambio_opcion_otra_cosa = request.form.get('cambio_opcion_otra_cosa')
            cambio_opcion_cupon = request.form.get('cambio_opcion_cupon')
            cambio_opcion = request.form.get('cambio_opcion')
            

            empresa.param_logo = param_logo
            empresa.param_fondo = param_fondo

            if configuracion.ventana_cambios != ventana_cambios:
                configuracion.ventana_cambios = ventana_cambios
                status = actualiza_empresa_JSON(empresa, 'ventana_cambio', int(ventana_cambios), 'politica')

            if configuracion.ventana_devolucion != ventana_devolucion:
                configuracion.ventana_devolucion = ventana_devolucion
                actualiza_empresa_JSON(empresa, 'ventana_devolucion', int(ventana_devolucion), 'politica')

            if cambio_otra_cosa == 'on':
                configuracion.cambio_otra_cosa = True
                actualiza_empresa_JSON(empresa, 'otracosa', 'Si', 'otros')
            else:
                configuracion.cambio_otra_cosa = False
                actualiza_empresa_JSON(empresa, 'otracosa', 'No', 'otros')

            if cambio_cupon == 'on':
                configuracion.cambio_cupon = True
                actualiza_empresa_JSON(empresa, 'cupon', 'Si', 'otros')
            else:
                configuracion.cambio_cupon = False
                actualiza_empresa_JSON(empresa, 'cupon', 'No', 'otros')
            
            if configuracion.cambio_opcion != cambio_opcion :
                configuracion.cambio_opcion = cambio_opcion
                actualiza_empresa_JSON(empresa, 'elegir_opcion_cambio', cambio_opcion, 'textos')
            
            if configuracion.cambio_opcion_cupon != cambio_opcion_cupon :
                configuracion.cambio_opcion_cupon = cambio_opcion_cupon
                actualiza_empresa_JSON(empresa, 'elegir_opcion_cambio_cupon', cambio_opcion_cupon, 'textos')

            if configuracion.cambio_opcion_otra_cosa != cambio_opcion_otra_cosa :
                configuracion.cambio_opcion_otra_cosa = cambio_opcion_otra_cosa
                actualiza_empresa_JSON(empresa, 'elegir_opcion_cambio_otra_cosa', cambio_opcion_otra_cosa, 'textos')

            db.session.commit()

            status = actualiza_empresa(empresa)
            #### falta actualizar JSON del portal
            if status != 'Failed':
                flash('Los datos se actualizaron correctamente')
            else:
                flash('Se produjo un error {}'. format(status))

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos,pestaña='portal', empresa_name=session['current_empresa'])


################################# Mostrar Motivos  ###########################################################
@bp.route('/edit_motivosinfo', methods=['GET', 'POST'])
@login_required
def edit_motivosinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos, pestaña='motivos', empresa_name=session['current_empresa'])


######################################## Añadir un Motivos  ######################################
@bp.route('/add_motivo', methods=['GET', 'POST'])
@login_required
def add_motivo():
    max_id = db.session.query(func.max(CONF_motivos.id_motivo)).scalar()
    nuevo_motivo = request.form.get('nuevo_motivo')
    tipo_nuevo_motivo = request.form.get('tipo_nuevo_motivo')

    unMotivo = CONF_motivos(
            store = current_user.store,
            id_motivo = max_id +1,
            motivo = nuevo_motivo,
            tipo_motivo = tipo_nuevo_motivo
        )
    
    db.session.add(unMotivo)
    db.session.commit()

    ###### actualiza el JSON del Front
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    motivos_tmp = CONF_motivos.query.filter_by(store=current_user.store).all()
    motivos=[]
    for m in motivos_tmp:
        motivos.append(m.motivo)
        actualiza_empresa_JSON(empresa, 'motivos', motivos, 'otros')
    
    return redirect(url_for('main.edit_motivosinfo'))


##################################### Editar o Borrar un Motivos  ######################################
@bp.route('/editar_motivo/<id>', methods=['GET', 'POST'])
@login_required
def editar_motivo(id):

    if request.method == "POST":
        unMotivo = CONF_motivos.query.filter_by(store=current_user.store, id_motivo=id).first() 
        accion = request.form.get('boton')

        if accion == "update":
            unMotivo.motivo = request.form.get('motivo')
            unMotivo.tipo_motivo = request.form.get('tipo_motivo')

        if accion == "eliminar":
            db.session.delete(unMotivo)

        db.session.commit()

        ###### actualiza el JSON del Front
        empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
        motivos_tmp = CONF_motivos.query.filter_by(store=current_user.store).all()
        motivos=[]
        for m in motivos_tmp:
            motivos.append(m.motivo)
            actualiza_empresa_JSON(empresa, 'motivos', motivos, 'otros')

    return redirect(url_for('main.edit_motivosinfo'))


################ Métodos de envío  #######################################
@bp.route('/edit_enviosinfo', methods=['GET', 'POST'])
@login_required
def edit_enviosinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    if request.method == "POST":
        accion = request.form.get('boton')

        if accion == "cancelar":
            return redirect(url_for('main.company', empresa_id=current_user.store ))
            
        if accion == "guardar":
            metodos = []
            for m in envios:
                habilitado = request.form.get('habilitado'+m.metodo_envio)
                titulo_boton = request.form.get('titulo_boton'+m.metodo_envio)
                descripcion_boton = request.form.get('descripcion_boton'+m.metodo_envio)
                clave = devolver_datos_boton(m.metodo_envio)
                
                
                if habilitado == 'on':
                    m.habilitado = True
                    metodos.append(str.lower(m.metodo_envio))
                else:
                    m.habilitado = False

                if m.titulo_boton != titulo_boton:
                    m.titulo_boton = titulo_boton
                    actualiza_empresa_JSON(empresa, clave[0], titulo_boton, 'textos')

                if m.descripcion_boton != descripcion_boton:    
                    m.descripcion_boton = descripcion_boton
                    actualiza_empresa_JSON(empresa, clave[1], descripcion_boton, 'textos')
            
            db.session.commit()
           
            status = actualiza_empresa_JSON(empresa, 'envio', metodos, 'otros')
            flash('status {}'.format(status))

        #### falta actualizar JSON del portal

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos,pestaña='envios', empresa_name=session['current_empresa'])


################ Mails desde el portal  #######################################
@bp.route('/edit_mailsportalinfo', methods=['GET', 'POST'])
@login_required
def edit_mailsportalinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    if request.method == "POST":
        accion = request.form.get('boton')

        if accion == "cancelar":
            return redirect(url_for('main.company', empresa_id=current_user.store ))
            
        if accion == "guardar":
            confirma_manual_note = request.form.get('confirma_manual_note')
            confirma_coordinar_note = request.form.get('confirma_coordinar_note')
            confirma_moova_note = request.form.get('confirma_moova_note')

            if empresa.confirma_manual_note != confirma_manual_note:
                empresa.confirma_manual_note = confirma_manual_note
                actualiza_empresa_JSON(empresa, 'confirma_manual_note', confirma_manual_note, 'textos')
                
            if empresa.confirma_coordinar_note != confirma_coordinar_note:
                empresa.confirma_coordinar_note = confirma_coordinar_note
                actualiza_empresa_JSON(empresa, 'confirma_coordinar_note', confirma_coordinar_note, 'textos')

            if empresa.confirma_moova_note != confirma_moova_note:
                empresa.confirma_moova_note = confirma_moova_note
                actualiza_empresa_JSON(empresa, 'confirma_moova_note', confirma_moova_note, 'textos')
    
            db.session.commit() 

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos, pestaña='mailsportal', empresa_name=session['current_empresa'])   


################ Mails desde el Backoffice  #######################################
@bp.route('/edit_mailsbackinfo', methods=['GET', 'POST'])
@login_required
def edit_mailsbackinfo():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    configuracion = CONF_boris.query.filter_by(store=current_user.store).first_or_404()
    envios = CONF_envios.query.filter_by(store=current_user.store).all()
    motivos = CONF_motivos.query.filter_by(store=current_user.store).all()

    if request.method == "POST":
        accion = request.form.get('boton')

        if accion == "cancelar":
            return redirect(url_for('main.company', empresa_id=current_user.store ))
            
        if accion == "guardar":
            communication_email = request.form.get('communication_email')
            envio_manual_note = request.form.get('envio_manual_note')
            envio_coordinar_note = request.form.get('envio_coordinar_note')
            envio_correo_note = request.form.get('envio_correo_note')
            aprobado_note = request.form.get('aprobado_note')
            rechazado_note = request.form.get('rechazado_note')
            cupon_generado_note = request.form.get('cupon_generado_note')
            finalizado_note = request.form.get('finalizado_note')

            empresa.communication_email = communication_email
            empresa.envio_manual_note = envio_manual_note
            empresa.envio_coordinar_note = envio_coordinar_note
            empresa.envio_correo_note = envio_correo_note
            empresa.aprobado_note = aprobado_note
            empresa.rechazado_note = rechazado_note
            empresa.cupon_generado_note = cupon_generado_note
            empresa.finalizado_note = finalizado_note

            db.session.commit() 

    return render_template('company.html', empresa=empresa, configuracion=configuracion, envios=envios, motivos=motivos, pestaña='mailsback', empresa_name=session['current_empresa'])   
        
 



@bp.route('/categorias_filtro', methods=['GET', 'POST'])
@login_required
def filtrar_categorias():
    empresa = Company.query.filter_by(store_id=current_user.store).first()
    
    ##### carga un dicccionario con categorias desde la plataforma ######
    try:
        categorias
    except:
        if empresa.platform == 'tiendanube':
            categorias = buscar_codigo_categoria_tiendanube(empresa)
        else: 
            categorias = []

    select = request.form.get('categoria')
    accion = request.form.get('boton')
    
    #### Si se agregó una categoria ##############################
    if accion == 'agregar':
        if categories_filter.query.get(select):
            flash('Ya existe esa categoria')
        else:
            unaCategoria =  categories_filter(
                store=current_user.store,
                category_id = select,
                category_desc = categorias[float(select)]
            )
            db.session.add(unaCategoria)
            db.session.commit()
            status = actualiza_empresa_categorias(empresa)
            if status != 'Failed':
                flash('Los datos se actuaizaron correctamente')
            else:
                flash('Se produjo un error {}'. format(status)) 
    
    #### Si se quitó una categoria ##############################
    if accion == 'quitar':
        if categories_filter.query.get(select):
            unaCategoria = categories_filter.query.get(select)
            db.session.delete(unaCategoria)
            db.session.commit()
            status = actualiza_empresa_categorias(empresa)
            if status != 'Failed':
                flash('Los datos se actuaizaron correctamente')
            else:
                flash('Se produjo un error {}'. format(status))  
        else:
            flash('No se puede quitar esa categoria porque no existe')
     
    categorias_filtradas = categories_filter.query.filter_by(store=current_user.store).all()
    return render_template('category.html', categorias=categorias, categorias_filtradas=categorias_filtradas, title='Categorias', empresa_name=session['current_empresa'])



@bp.route('/search')  
def search():
    query =  request.args.get('search') 
    if Order_header.query.filter_by(order_number=query).first():
        req_search = Order_header.query.filter_by(order_number=query).first()
    else:
        flash('No se encontró ese nro de Orden')
        return redirect(url_for('main.ver_ordenes', estado='all', subestado='all'))
    return redirect(url_for('main.orden', orden_id=req_search.id))


##### Gestiona las lineas entrantes de las solicitudes
@bp.route('/gestion_lineas_entrantes/<orden_id>',methods=['GET', 'POST'])  
def gestion_lineas_entrantes(orden_id):
    if request.method == "POST":
        productos = request.form.getlist('prod_id')
        for p in productos: 
            variant = request.form.get("variant"+str(p))
            accion = request.form.get("accion"+str(p))
            accion_cantidad = request.form.get("accion_cantidad"+str(p))
            order_line = request.form.get("order_line"+str(p))
            ## Guarda el valor que se le reconoció al cliente al devolver el producto
            if request.form.get("precio"+str(p)) != None :
                monto_devuelto = request.form.get("precio"+str(p))
            else:
                monto_devuelto = 0
            # Asigna accion_stock dependiendo de si se eligió que el stock se reingrese o no
            if request.form.get("stockradio"+str(p)) == None:
                accion_stock = "No vuelve al stock"
            else: 
                accion_stock = "Vuelve al stock"
            devolver_linea(p, variant, accion_cantidad, orden_id, order_line, accion, accion_stock, monto_devuelto)
    return redirect(url_for('main.orden', orden_id=orden_id))


##### Gestiona las lineas salientes de las solicitudes
@bp.route('/gestion_lineas_saliente/<orden_id>',methods=['GET', 'POST'])  
def gestion_lineas_salientes(orden_id):
    if request.method == "POST":
        empresa = Company.query.get(current_user.store)
        ordenes = request.form.getlist('order_line_saliente')
        nuevaorden = request.form.get("nuevaorden")
        envio_nueva_orden = request.form.get("envio_nueva_orden")
        total_nueva_orden = request.form.get("total_nueva_orden")

        orden = Order_header.query.get(orden_id)
        #unCliente = orden.buyer
        #unaEmpresa = orden.pertenece
        
        # agrego datos de la nueva orden (forma de envio, costo de envio y total a cobrar)
        orden.nuevo_envio = nuevaorden
        orden.nuevo_envio_costo = envio_nueva_orden
        if float(total_nueva_orden) < 0:
            monto_total = 0
        else: 
            orden.nuevo_envio_total = total_nueva_orden
        orden.courier_coordinar_empresa = request.form.get("empresa_coordinada")
        orden.courier_coordinar_guia = request.form.get("guia_coordinada")
        

        if nuevaorden == None:
             flash('Debe especificar un método de creación para la nueva Orden')
             return redirect(url_for('main.orden', orden_id=orden_id))

        if  nuevaorden == 'manual': 
                envio_nuevo_metodo = 'Se envía manualmente'

        if  nuevaorden == 'manual_stock': 
            envio_nuevo_metodo = 'Se envía manualmente - se descuenta stock'
            if empresa.stock_vuelve_config == True:
                actualizar_stock(ordenes, empresa ,'saliente')
            else:
                send_email('Se ha generado una orden manual en BORIS ', 
                    sender=empresa.communication_email,
                    recipients=[empresa.admin_email], 
                    text_body=render_template('email/gestion_stock.txt',
                                            order=orden, envio=envio_nueva_orden, total=total_nueva_orden),
                    html_body=render_template('email/gestion_stock.html',
                                            order=orden, envio=envio_nueva_orden, total=total_nueva_orden),
                    attachments=None, 
                    sync=False)
          
        if  nuevaorden == 'tienda': 
            envio_nuevo_metodo = 'Se envía mediante nueva orden en Tienda'
            
            unCliente = orden.buyer
            unaEmpresa = orden.pertenece
            lineas = Order_detail.query.filter(Order_detail.order_line_number.in_(ordenes)).all()
            for l in lineas:
                #### si la diferencia es negativa, la pone en 0 ######
                if float(request.form.get("saliente_diferencia_precio"+str(l.prod_id))) < 0:
                    diferencia = 0
                else:
                    diferencia = request.form.get("saliente_diferencia_precio"+str(l.prod_id))
                l.accion_cambiar_por_diferencia = diferencia   
            db.session.commit()    
            ####### genera nueva ordenen tiendanube ###################
            if unaEmpresa.platform == 'tiendanube':
                generacion_envio = generar_envio_tiendanube(orden, lineas, unCliente, unaEmpresa)
                if generacion_envio == 'Failed':
                    return redirect(url_for('main.orden', orden_id=orden_id))

        # gestiono las lineas de la orden
        for o in ordenes:
            linea = Order_detail.query.get(str(o))
            linea.fecha_gestionado = datetime.utcnow()
            loguear_transaccion('CAMBIADO', str(linea.accion_cambiar_por_desc)+' '+envio_nuevo_metodo, orden_id, current_user.id, current_user.username)
            if linea.gestionado == 'Devuelto':
                linea.gestionado = 'Si'
            else:
                linea.gestionado = traducir_estado('CAMBIADO')[1]
            
        finalizar_orden(orden_id)
        db.session.commit()
        
    return redirect(url_for('main.orden', orden_id=orden_id))


##### Gestiona las lineas salientes de las solicitudes
@bp.route('/gestion_lineas_cupones/<orden_id>',methods=['GET', 'POST'])  
def gestion_lineas_cupones(orden_id):
    if request.method == "POST":
        total_cupon = request.form.get("total_cupon")
        ordenes = request.form.getlist('order_line_cupon')
        if float(total_cupon) != 0:
            empresa = Company.query.get(current_user.store)
            orden = Order_header.query.get(orden_id)
            unCliente = orden.buyer
            
            credito = genera_credito(empresa, total_cupon, unCliente, orden)
            envio_nuevo_metodo = 'Se genera cupon: '+credito+' por un total de'+total_cupon
            if credito == 'Failed':
                return redirect(url_for('main.orden', orden_id=orden_id))
        else: 
            envio_nuevo_metodo = 'Cupón cancelado - No se generó'

        for o in ordenes:
            linea = Order_detail.query.get(str(o))
            linea.fecha_gestionado = datetime.utcnow()
            loguear_transaccion('CAMBIADO', str(linea.name)+' '+envio_nuevo_metodo, orden_id, current_user.id, current_user.username)
            if linea.gestionado == 'Devuelto':
                linea.gestionado = 'Si'
            else:
                linea.gestionado = traducir_estado('CAMBIADO')[1]
            
        finalizar_orden(orden_id)
        db.session.commit()
    return redirect(url_for('main.orden', orden_id=orden_id))


@bp.route('/ordenes/<estado>/<subestado>', methods=['GET', 'POST'])
@login_required
def ver_ordenes(estado, subestado):
    resumen = resumen_ordenes(current_user.store) 
    page = request.args.get('page', 1, type=int)
    next_url = None
    prev_url = None
    if estado == 'all':
        ordenes =  Order_header.query.filter_by(store=current_user.store).all()
    else :
        if subestado == 'all':
            ordenes = db.session.query(Order_header).filter((Order_header.store == current_user.store)).filter((Order_header.status == estado))
        else: 
            ordenes = db.session.query(Order_header).filter((Order_header.store == current_user.store)).filter((Order_header.status == estado)).filter((Order_header.status_resumen == subestado))

    return render_template('ordenes.html', title='Ordenes', ordenes=ordenes, estado=estado, subestado=subestado,  resumen=resumen, empresa_name=session['current_empresa'])


@bp.route('/orden/mantenimiento/<orden_id>', methods=['GET', 'POST'])
@login_required
def mantener_orden(orden_id):
    orden = Order_header.query.filter_by(id=orden_id).first()
    lineas = Order_detail.query.filter_by(order=orden.id).all()
    return render_template('mantener_orden.html', orden=orden, lineas=lineas, customer=orden.buyer, empresa_name=session['current_empresa'])


@bp.route('/orden/eliminar/<orden_id>', methods=['GET', 'POST'])
@login_required
def eliminar_orden(orden_id):
    orden = Order_header.query.filter_by(id=orden_id).first()
    eliminar = request.form.get("bton")
    confirmacion = request.form.get("confirmacion")
    if eliminar == 'OK' and confirmacion == 'eliminar':
        flash('Se eliminó la orden {}'.format(orden.order_number))
        Transaction_log.query.filter_by(order_id=orden_id).delete()
        Order_detail.query.filter_by(order=orden_id).delete()
        Order_header.query.filter_by(id=orden_id).delete()
        db.session.commit()
    else: 
        flash('Se canceló la eliminación de la orden')
    return redirect(url_for('main.ver_ordenes', estado='all', subestado='all'))

@bp.route('/orden/<orden_id>', methods=['GET', 'POST'])
@login_required
def orden(orden_id):
    orden = Order_header.query.filter_by(id=orden_id).first()
    orden_linea = Order_detail.query.filter_by(order=orden_id).all()
    empresa = Company.query.get(orden.store)
    if request.form.get('nota'):
        orden.note = request.form.get('nota')
        db.session.commit()
        
    return render_template('orden.html', orden=orden, orden_linea=orden_linea, customer=orden.buyer, empresa=empresa, empresa_name=session['current_empresa'])


@bp.route('/orden/gestion/<orden_id>', methods=['GET', 'POST'])
@login_required
def gestionar_ordenes(orden_id):
    accion = request.args.get('accion_orden')
    orden = Order_header.query.filter_by(id=orden_id).first()
    orden_linea = Order_detail.query.filter_by(order=orden_id).all()
    empresa = Company.query.get(orden.store)
    # flash ('Accion {} - orden {} CIA {}'.format(accion, orden.courier, current_user.empleado))
    if accion == 'toReady':
        # if request.form['coordinar_empresa']:
        if request.form.get('coordinar_empresa') or request.form.get('coordinar_guia') or request.form.get('coordinar_roundtrip'):
            orden.courier_coordinar_empresa = request.form['coordinar_empresa']
            orden.courier_coordinar_guia = request.form.get('coordinar_guia')
            if request.form.get('coordinar_roundtrip') == "on":
                orden.courier_coordinar_roundtrip = True
            else:
                orden.courier_coordinar_roundtrip = False
            db.session.commit()
        toReady(orden, current_user.empleado)
    else: 
        if accion == 'toReceived':
            toReceived(orden.id)
        else:
            if accion == 'toApproved':
                toApproved(orden.id)
            else: 
                if accion == 'toReject': 
                    motivo = request.form.get('motivo')
                    toReject(orden.id, motivo)
    return render_template('orden.html', orden=orden, orden_linea=orden_linea, customer=orden.buyer, empresa=empresa, empresa_name=session['current_empresa'])
    

@bp.route('/gestion_producto/<orden_id>', methods=['GET', 'POST'])
@login_required
def gestionar_producto(orden_id):
    linea_id = request.args.get('linea_id')
    orden = Order_header.query.filter_by(id=orden_id).first()
    linea = Order_detail.query.get(str(linea_id))
    empresa = Company.query.get(orden.store)
    producto_nuevo = buscar_producto(linea.prod_id, empresa)
    return render_template('producto.html', producto=producto_nuevo, orden=orden, linea=linea, customer=orden.buyer, empresa=empresa,  empresa_name=session['current_empresa'])


@bp.route('/orden/historia/<orden_id>', methods=['GET', 'POST'])
@login_required
def historia_orden(orden_id):
    orden = Order_header.query.filter_by(id=orden_id).first()
    historia = Transaction_log.query.filter_by(order_id=orden_id).all()
    lineas = Order_detail.query.filter_by(order=orden.id).all()
    empresa = Company.query.get(orden.store)
    return render_template('historia_orden.html', orden=orden, historia=historia, lineas=lineas, customer=orden.buyer, empresa=empresa, empresa_name=session['current_empresa'])


@bp.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        orden = Order_header.query.filter_by(courier_order_id = str(data['id'])).first()
        orden.status = 'Shipping'
        orden.sub_status = traducir_estado(data['status'])[0]
        orden.status_resumen = traducir_estado(data['status'])[1]
        orden.last_update_date = data['date']

        usuario = User.query.filter_by(username = 'Webhook').first()
        unaTransaccion = Transaction_log(
            sub_status = traducir_estado(data['status'])[0],
            status_client = traducir_estado(data['status'])[2],
            order_id = orden.id,
            user_id = usuario.id,
            username = usuario.username
        )
        db.session.add(unaTransaccion)

        db.session.commit()
        return '', 200
    else:
        #abort(400)
        return "Error al actualizar estado del pedido", 400


@bp.route('/pedidos', methods=['POST'])
def recibir_pedidos():
    if request.method == 'POST':
        pedido = request.json
        
        ############# controlar si ya exste transaccion ###########################
        if Order_header.query.filter_by(order_number=pedido['orden_nro']).first():
            orden = Order_header.query.filter_by(order_number=pedido['orden_nro']).first()
            lineas = Order_detail.query.filter_by(order=orden.id).all()
            
            ### comprueba cantidad de articulos ###
            if len(lineas) == len(pedido['producto']):
                cantidad = 'misma'
            else: 
                cantidad = 'diferente'
            
            #### compruebo si son iguales (prodcutos / acciones ##########
            iguales = 'Si'
            accion = 'igual'
            for l in lineas:
                for p in pedido['producto']:
                    if l.prod_id == p['id']:
                        if l.accion == p['accion']:
                            continue
                        else:
                            accion = 'distinta'
                            break
                    else:
                        iguales = 'No'
                        break
            if (cantidad == 'misma' and iguales == 'Si' and accion == 'igual'):
                return "Solicitud duplicada", 409
            if (cantidad == 'misma' and iguales == 'Si' and accion == 'distinta'):
                return "Cambio de accion", 409
            if (cantidad == 'misma' and iguales == 'No'):
                return "Cambio de producto", 409
            if cantidad == 'diferente':
                return "Agrega / quita artículos", 409
            return str('cantidad '+ cantidad + 'iguales '+ iguales + 'accion ' + accion), 409

        nuevo_pedido = crear_pedido(pedido)
        usuario = User.query.filter_by(username = 'Webhook').first()

        unaTransaccion = Transaction_log(
            sub_status = traducir_estado(pedido['correo']['correo_status'])[0],
            status_client = traducir_estado(pedido['correo']['correo_status'])[2],
            order_id = nuevo_pedido.id,
            user_id = usuario.id,
            username = usuario.username
        )
        db.session.add(unaTransaccion)
        db.session.commit()
        return '', 200
    else:
        #abort(400)
        return "Error al cargar la solicitud", 400


@bp.route('/autorizar/<plataforma>', methods=['GET', 'POST'])
def autorizar(plataforma):
    if request.args.get('code') != None:
        codigo = request.args.get('code')
    else: 
        return render_template('autorizado.html', codigo='error')   
    
    #### Autoriza permisos en Tiendanube y asigna TOKEN
    ##### graba datos de la empresa en autorizacion
    autorizacion = autorizar_tiendanube(codigo)
    usuario = re.sub('[\s+]', '', autorizacion.store_name[0:8].strip())

    if autorizacion != 'Failed': 
        #### actualiza los datos de la empresa en FRONT - si la empresa ya existia no hace nada #####
        actualizado = actualiza_empresa(autorizacion)

        if actualizado != 'Failed':
            ##### inicializa las bases con los datos por default del JSON del Front ##############################3
            incializa_configuracion(autorizacion)

            send_email('Bienvenido a BORIS!', 
                sender=current_app.config['ADMINS'][0],  
                recipients=[current_app.config['ADMINS'][0],autorizacion.admin_email],
                text_body=render_template('email/bienvenido.txt', codigo='OK', usuario=usuario, store=autorizacion),
                html_body=render_template('email/bienvenido.html', codigo='OK', usuario=usuario, store=autorizacion), 
                attachments=None, 
                sync=False)
            return render_template('autorizado.html', codigo='OK', usuario=usuario, store=autorizacion)
        else:
            return render_template('autorizado.html', codigo='error_al_actualizar', store=actualizado )         
    else:
        return render_template('autorizado.html', codigo='error') 


@bp.route('/orden/tracking', methods=['GET', 'POST'])
def tracking_orden():
    if request.method == 'GET':
        orden_id = request.args.get('orden_id')
        orden = Order_header.query.filter_by(order_number=orden_id).first()
        # flash('Orden: {}'.format(orden.id))
        historia = Transaction_log.query.filter_by(order_id=orden.id).all()
        status_tmp = []
        for i in historia:
            if i.status_client != 'N0':
                status_tmp.append({
                "id":i.order_id,
                "Estado": i.status_client,
                "Fecha": str(i.fecha)
                })
        return json.dumps(status_tmp), 200





#### Se escribe nueva version para gestiona orden complata BORRAR ####
@bp.route('/cambiar', methods=['GET', 'POST'])
@login_required
def cambiar():
    orden_id = request.args.get('orden_id')
    order_line_number = request.args.get('order_line')
    orden = Order_header.query.filter_by(id=orden_id).first()
    linea = Order_detail.query.get(str(order_line_number))
    unCliente = orden.buyer
    unaEmpresa = orden.pertenece

    envio_nuevo = request.form.get('metodo_envio')

    if  envio_nuevo == 'manual': 
        envio_nuevo_metodo = 'Se envía manualmente'

    if envio_nuevo == 'tiendanube':
        generacion_envio = generar_envio_tiendanube(orden, linea, unCliente, unaEmpresa)
        envio_nuevo_metodo = 'Se envía mediante orden en Tiendanube'
        if generacion_envio == 'Failed':
            return redirect(url_for('main.orden', orden_id=orden_id))

    if  envio_nuevo == 'cupon': 
        #flash('Cupon x {} - {}'.format(request.form.get('monto'), unaEmpresa.platform ))
        monto = request.form.get('monto')
        credito = genera_credito(unaEmpresa, monto, unCliente, orden, linea)
        envio_nuevo_metodo = 'Se genera cupon: '+credito+' por '+monto

        if credito == 'Failed':
            return redirect(url_for('main.orden', orden_id=orden_id))
        

    linea = Order_detail.query.get(str(order_line_number))
    linea.nuevo_envio = envio_nuevo_metodo
    linea.fecha_gestionado = datetime.utcnow()
    loguear_transaccion('CAMBIADO', str(linea.name)+' '+envio_nuevo, orden_id, current_user.id, current_user.username)
    if linea.gestionado == 'Devuelto':
        linea.gestionado = 'Si'
    else:
        linea.gestionado = traducir_estado('CAMBIADO')[1]
    finalizar_orden(orden_id)
    db.session.commit()
    return redirect(url_for('main.orden', orden_id=orden_id))

    return 'Sucesss'


@bp.route('/buscar_variante', methods=['POST'])
def buscar_datos_variantes():
    prod_id = request.form.get('prod_id')
    variante = request.form.get('variante')
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    if empresa.platform == 'tiendanube':
        #flash('buscar_datos_variantes_tiendanube({}, {})'.format(prod_id, variante))
        variante = buscar_datos_variantes_tiendanube(prod_id, variante, empresa)
        #flash('variante variante {} prod {}'.format(variante, prod_id))
    if type(variante) != dict:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 
    #flash('variante {}'.format(variante))
    return json.dumps(variante)






#################################################################################
####### Tareasde Mantenimiento /Mantenimiento ###################################
#################################################################################

@bp.route('/cargar_pedidos', methods=['GET', 'POST'])
@login_required
def upload_pedidos():
    cargar_pedidos()
    ordenes =  Order_header.query.filter_by(store=current_user.store).all()
    return render_template('ordenes.html', title='Ordenes', ordenes=ordenes, empresa_name=session['current_empresa'])


@bp.route('/cargar_empresa', methods=['GET', 'POST'])
def cargar_empresa():
    if Company.query.filter_by(store_id='1447373').first():
        unaEmpresa = Company.query.filter_by(store_id='1447373').first()
        #unaEmpresa.store_url = 'https://demoboris.mitiendanube.com'
        flash('ya existe 1447373')
    else: 
        unaEmpresa = Company(
            store_id = '1447373',
            platform = 'tiendanube',
            platform_token_type = 'bearer',
            platform_access_token = 'cb9d4e17f8f0c7d3c0b0df4e30bcb2b036399e16',
            store_name = 'Demo Boris',
            store_url = 'https://demoboris.mitiendanube.com',
            correo_test = True,
            correo_apikey = 'b23920003684e781d87e7e5b615335ad254bdebc',
            correo_id = 'b22bc380-439f-11eb-8002-a5572ae156e7',
            correo_apikey_test = 'b23920003684e781d87e7e5b615335ad254bdebc',
            correo_id_test = 'b22bc380-439f-11eb-8002-a5572ae156e7'
        )
        db.session.add(unaEmpresa)
    if Company.query.filter_by(store_id='1631829').first():
        unaEmpresa2 = Company.query.filter_by(store_id='1631829').first()
        unaEmpresa2.platform = 'tiendanube'
        flash('ya existe 1631829')
    else: 
        unaEmpresa2 = Company(
            store_id = '1631829',
            platform = 'tiendanube',
            platform_token_type = 'bearer',
            platform_access_token = 'c4c8afc07063098d7afa72bef6fdaf67ba7e22a3',
            store_name = 'Demo de boca en boca',
            store_url = 'https://demodebocaenboca.mitiendanube.com',
            correo_test = True,
            correo_apikey = 'b23920003684e781d87e7e5b615335ad254bdebc',
            correo_id = 'b22bc380-439f-11eb-8002-a5572ae156e7',
            correo_apikey_test = 'b23920003684e781d87e7e5b615335ad254bdebc',
            correo_id_test = 'b22bc380-439f-11eb-8002-a5572ae156e7'
        )
        db.session.add(unaEmpresa2)

    if Company.query.filter_by(store_id='1').first():
        otraEmpresa = Company.query.filter_by(store_id='1').first()
        flash('ya existe 1')
    else: 
        otraEmpresa = Company(
            store_id = '1',
            platform = 'None',
            store_name = 'Boris'
        )
        db.session.add(otraEmpresa)

    unUsuario = User(
        username = 'Webhook',
        email = 'webhook@borisreturns.com',
        store = '1',
    )
    db.session.add(unUsuario)

    db.session.commit()

    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/borrar_pedidos', methods=['GET', 'POST'])
@login_required
def borrar_pedidos():
    orders =  Order_header.query.filter_by(store=1447373).all()
    orders2 = Order_header.query.all()
    flash('orders {}'.format( type(orders)))
    flash('orders2 {}'.format( type(orders2)))
    for u in orders:
        lineas = Order_detail.query.filter_by(order=u.id).all()
        for l in lineas:
            flash('Borrando Order_detail {} '.format(l))
            db.session.delete(l)
        flash('Borrando Order_header {} '.format(u))
        db.session.delete(u)

    #for u in orders:
    #    flash('Borrando Order_header {} '.format(u))
    #    db.session.delete(u)

    #orders = Order_detail.query.all()
    #for u in orders:
    #    flash('Borrando Order_detail {} '.format(u))
    #    db.session.delete(u)

    #users = User.query.all()
    #for u in users:
    #    flash('Users {} '.format(u))
    #    db.session.delete(u)

    #cia = Company.query.all()
    #for u in cia:
    #    flash('Company {} {}'.format(u, u.store_id))
    #    db.session.delete(u)
    
    db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))



    
    
    