import requests
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, session, Response
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User, Company, Order_header, Customer, Order_detail, Transaction_log
from app.main.interfaces import cargar_pedidos, resumen_ordenes, toReady, toApproved, traducir_estado
import json

from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home')


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit() 
        #return redirect(url_for('main.edit_profile'))
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('edit_profile.html', title='Editar perfil',
                           form=form)


@bp.route('/Dashboard', methods=['GET', 'POST'])
@login_required
def vision_general():
    resumen = resumen_ordenes(current_user.store) 
    return render_template('dashboard.html', title='Vision General', resumen=resumen)


@bp.route('/ordenes/<estado>', methods=['GET', 'POST'])
@login_required
def ver_ordenes(estado):
    if estado == 'all':
        ordenes =  Order_header.query.filter_by(store=current_user.store).all()
    else :
        ordenes = db.session.query(Order_header).filter((Order_header.store == current_user.store)).filter((Order_header.status == estado))
    return render_template('ordenes.html', title='Ordenes', ordenes=ordenes, estado=estado)


@bp.route('/borrar_pedidos', methods=['GET', 'POST'])
@login_required
def borrar_pedidos():
    orders = Order_header.query.all()
    for u in orders:
        flash('Borrando Order_header {} '.format(u))
        db.session.delete(u)

    orders = Order_detail.query.all()
    for u in orders:
        flash('Borrando Order_detail {} '.format(u))
        db.session.delete(u)

#    users = User.query.all()
#    for u in users:
#        flash('Users {} '.format(u))
#        db.session.delete(u)

#    cia = Company.query.all()
#    for u in cia:
#        flash('Company {} '.format(u))
#        db.session.delete(u)
    
    db.session.commit()
    return render_template('ordenes.html', title='Ordenes')


@bp.route('/cargar_pedidos', methods=['GET', 'POST'])
@login_required
def upload_pedidos():
    cargar_pedidos()
    ordenes =  Order_header.query.filter_by(store=current_user.store).all()
    return render_template('ordenes.html', title='Ordenes', ordenes=ordenes)


@bp.route('/cargar_empresa', methods=['GET', 'POST'])
@login_required
def cargar_empresa():
    unaEmpresa = Company(
        store_id = '1447373',
        platform = 'TIendaNube',
        store_name = 'Demo Boris',
        correo_apikey = 'b23920003684e781d87e7e5b615335ad254bdebc',
        correo_id = 'b22bc380-439f-11eb-8002-a5572ae156e7'
    )
    db.session.add(unaEmpresa)

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


@bp.route('/orden/<orden_id>')
@login_required
def orden(orden_id):
    orden = Order_header.query.filter_by(id=orden_id).first()
    orden_linea = Order_detail.query.filter_by(order=orden_id).all()
    return render_template('orden.html', orden=orden, orden_linea=orden_linea, customer=orden.buyer)


@bp.route('/gestion_orden/<orden_id>', methods=['GET', 'POST'])
@login_required
def gestionar_ordenes(orden_id):
    accion = request.args.get('accion_orden')
    orden = Order_header.query.filter_by(id=orden_id).first()
    orden_linea = Order_detail.query.filter_by(order=orden_id).all()
    # flash ('Accion {} - orden {} CIA {}'.format(accion, orden.courier, current_user.empleado))
    if accion == 'toReady':
        toReady(orden.courier_order_id, current_user.empleado)
    else: 
        if accion == 'toApproved':
            toApproved(orden.id)
    #return redirect(url_for('main.user', username=current_user.username))
    return render_template('orden.html', orden=orden, orden_linea=orden_linea, customer=orden.buyer)
    


@bp.route('/gestion_producto/<orden_id>', methods=['GET', 'POST'])
@login_required
def gestionar_producto(orden_id):
    linea_id = request.args.get('linea_id')
    orden = Order_header.query.filter_by(id=orden_id).first()
    linea = Order_detail.query.get(str(linea_id))
    return render_template('producto.html', orden=orden, linea=linea, customer=orden.buyer)


@bp.route('/historia_orden/<orden_id>', methods=['GET', 'POST'])
@login_required
def historia_orden(orden_id):
    orden = Order_header.query.filter_by(id=orden_id).first()
    historia = Transaction_log.query.filter_by(order_id=orden_id).all()
    return render_template('historia_orden.html', orden=orden, historia=historia, customer=orden.buyer)


@bp.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        orden = Order_header.query.filter_by(courier_order_id = str(data['id'])).first()
        orden.sub_status = traducir_estado(data['status'])
        orden.last_update_date = data['date']

        usuario = User.query.filter_by(username = 'Webhook').first()
        unaTransaccion = Transaction_log(
            sub_status = orden.sub_status,
            order_id = orden.id,
            user_id = usuario.id,
            username = usuario.username
        )
        db.session.add(unaTransaccion)

        db.session.commit()
        return '', 200
    else:
        abort(400)


@bp.route('/devolver', methods=['GET', 'POST'])
@login_required
def devolver():
    prod_id = request.args.get('prod_id')
    variant = request.args.get('variant')
    cantidad = request.args.get('cantidad')
    orden_id = request.args.get('orden_id')
    order_line_number = request.args.get('order_line')
    accion = request.args.get('accion')
    
    url = "https://api.tiendanube.com/v1/1447373/products/"+str(prod_id)+"/variants/"+str(variant)
    payload={}
    headers = {
        'User-Agent': 'Boris (erezzonico@borisreturns.com)',
        'Content-Type': 'application/json',
        'Authentication': 'bearer cb9d4e17f8f0c7d3c0b0df4e30bcb2b036399e16'
     }

    # Trae stock actual
    order = requests.request("GET", url, headers=headers, data=payload).json()
    stock_tmp = int(order['stock']) + int(cantidad)
    stock = {
        "stock": stock_tmp
    }
    # Aumenta el stock de la tienda en la cantidad devuelta
    #order = requests.request("PUT", url, headers=headers, data=json.dumps(stock)).json()
    order = requests.request("PUT", url, headers=headers, data=json.dumps(stock))

    if order.status_code != 200:
        flash('Hubo un problema en la devolcuión No se devolvió el stock. Error {}'.format(solicitud.status_code))
    else:
        linea = Order_detail.query.get(str(order_line_number))
        loguear_transaccion('Devuelto', orden_id, current_user.id, current_user.username)
        if accion == 'devolver':
            linea.gestionado = 'Si'
            db.session.commit()
            #finalizar_orden
        if accion == 'cambiar':
            linea.gestionado = 'Devuelto'
            db.session.commit()

    return redirect(url_for('main.orden', orden_id=orden_id))
    

def loguear_transaccion(sub_status, order_id, user_id, username):
    unaTransaccion = Transaction_log(
        sub_status = sub_status,
        order_id = order_id,
        user_id = user_id,
        username = username
    )
    db.session.add(unaTransaccion)
    db.session.commit()
    return 'Success'




    