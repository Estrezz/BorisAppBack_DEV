import requests
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, session, Response
from flask_login import current_user, login_required
from app import db
from app.email import send_email
from app.main.forms import EditProfileForm, EditProfileCompanyForm, EditMailsCompanyForm, EditCorreoCompanyForm, EditParamsCompanyForm, EditMailsFrontCompanyForm
from app.main.tiendanube import generar_envio_tiendanube, autorizar_tiendanube, buscar_codigo_categoria_tiendanube, buscar_datos_variantes_tiendanube
from app.models import User, Company, Order_header, Customer, Order_detail, Transaction_log, categories_filter
from app.main.interfaces import crear_pedido, cargar_pedidos, resumen_ordenes, toReady, toReceived, toApproved, toReject, traducir_estado, buscar_producto, genera_credito, actualiza_empresa, actualiza_empresa_categorias, actualiza_empresa_JSON, loguear_transaccion, finalizar_orden, devolver_linea, actualizar_stock
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
    return render_template('company.html', empresa=empresa, empresa_name=session['current_empresa'])


@bp.route('/edit_profile_company', methods=['GET', 'POST'])
@login_required
def edit_profile_company():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    query =  request.args.get('formulario')
    
    if query == "Datos de la tienda":
        form = EditProfileCompanyForm(obj=empresa)
    if query == "Correo":
        form = EditCorreoCompanyForm(obj=empresa)
    if query == "Parametros":
        form = EditParamsCompanyForm(obj=empresa)
    if query == "Mails":
        form = EditMailsCompanyForm(obj=empresa)

    if form.validate_on_submit():
        form.populate_obj(empresa)
        db.session.commit() 
        #### Actualiza los datos de la empresa en el FRONT ####
        status = actualiza_empresa(empresa)
        if status != 'Failed':
            flash('Los datos se actualizaron correctamente')
        else:
            flash('Se produjo un error {}'. format(status))
        return redirect(url_for('main.company', empresa_id=empresa.store_id))

    return render_template('edit_profile_company.html', title='Editar perfil',
                           form=form, titulo=query, empresa_name=session['current_empresa'])


@bp.route('/edit_profile_company_front', methods=['GET', 'POST'])
@login_required
def edit_profile_company_front():
    empresa = Company.query.filter_by(store_id=current_user.store).first_or_404()
    query =  request.args.get('formulario')
    
    form = EditMailsFrontCompanyForm(obj=empresa)
    if form.validate_on_submit():
       
        if empresa.confirma_manual_note != form.confirma_manual_note.data:
            empresa.confirma_manual_note = form.confirma_manual_note.data
            actualiza_empresa_JSON(empresa, 'confirma_manual_note', form.confirma_manual_note.data)
            
        if empresa.confirma_coordinar_note != form.confirma_coordinar_note.data:
            empresa.confirma_coordinar_note = form.confirma_coordinar_note.data
            actualiza_empresa_JSON(empresa, 'confirma_coordinar_note', form.confirma_coordinar_note.data)

        if empresa.confirma_moova_note != form.confirma_moova_note.data:
            empresa.confirma_moova_note = form.confirma_moova_note.data
            actualiza_empresa_JSON(empresa, 'confirma_moova_note', form.confirma_moova_note.data)
  
        db.session.commit() 
        return redirect(url_for('main.company', empresa_id=empresa.store_id))

    return render_template('edit_profile_company.html', title='Editar perfil',
                           form=form, titulo=query, empresa_name=session['current_empresa'])



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


### BORRAR ####
# @bp.route('/producto/historia/<linea_id>', methods=['GET', 'POST'])
# @login_required
# def historia_producto(linea_id):
#    linea = Order_detail.query.get(str(linea_id))
#    return render_template('historia_producto.html', linea=linea, empresa_name=session['current_empresa'])


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
        abort(400)


@bp.route('/pedidos', methods=['POST'])
def recibir_pedidos():
    if request.method == 'POST':
        pedido = request.json
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
        abort(400)


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
        #### actualiza los datos de la empresa en FRONT #####
        actualizado = actualiza_empresa(autorizacion)
        if actualizado != 'Failed':
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



#### Se escribe nueva version para gestion de lineas en conjunto ###################
#@bp.route('/devolver', methods=['GET', 'POST'])
#@login_required
#def devolver():
#    prod_id = request.args.get('prod_id')
#    variant = request.args.get('variant')
#    cantidad = request.args.get('cantidad')
#    orden_id = request.args.get('orden_id')
#    order_line_number = request.args.get('order_line')
#    accion = request.args.get('accion')
#    accion_stock = request.form['stockradio']
#    linea = Order_detail.query.get(str(order_line_number))
#    orden = Order_header.query.get(orden_id)
#
#    if request.form.get('monto') != None :
#        monto_devuelto = request.form.get('monto')
#    else:
#        monto_devuelto = 0
#    
#    if accion_stock != 'no_vuelve':
#        empresa = Company.query.get(current_user.store)
#        if empresa.stock_vuelve_config == True:
#            if empresa.platform == 'tiendanube':
#                #devolucion = devolver_stock_tiendanube(empresa, prod_id, variant, cantidad)
#                #if devolucion == 'Failed':
#
#                return redirect(url_for('main.orden', orden_id=orden_id))
#        else: 
#            ## Si la configuracion de stock_vuelve_config es False (el stock no se devuelve fisicamente)
#            ## Envía mail al administrador de la empresa avisando para que lo devuelva por sistema
#            send_email('Se ha devuelto un artículo en BORIS ', 
#                sender=empresa.communication_email,
#                recipients=[empresa.admin_email], 
#                text_body=render_template('email/articulo_devuelto.txt',
#                                         order=orden, linea=linea),
#                html_body=render_template('email/articulo_devuelto.html',
#                                         order=orden, linea=linea), 
#                attachments=None, 
#                sync=False)
#        
#    # linea = Order_detail.query.get(str(order_line_number))
#    linea.monto_devuelto = monto_devuelto
#    linea.restock = accion_stock
#    linea.fecha_gestionado = datetime.utcnow()
#    loguear_transaccion('DEVUELTO',str(linea.name)+' '+accion_stock, orden_id, current_user.id, current_user.username)
#    if accion == 'devolver':
#        linea.gestionado = 'Si'
#        db.session.commit()
#    if accion == 'cambiar':
#        if linea.gestionado == 'Cambiado':
#            linea.gestionado = 'Si'
#        else: 
#            linea.gestionado = traducir_estado('DEVUELTO')[1]
#        db.session.commit()
#    finalizar_orden(orden_id)
#    return redirect(url_for('main.orden', orden_id=orden_id))

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



    
    
    