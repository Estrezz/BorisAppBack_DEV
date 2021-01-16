from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, session, Response
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User, Company, Order_header, Customer, Order_detail
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

#@bp.route('/pedidos', methods=['GET', 'POST'])
#@login_required
#def ver_pedidos():
#    ordenes =  Order_header.query.filter_by(store=current_user.store).all()
#    return render_template('pedidos.html', title='Pedidos', ordenes=ordenes)


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

    cia = Company.query.all()
    for u in cia:
        flash('Company {} '.format(u))
        db.session.delete(u)
    
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
    # flash ('Accion {} - orden {} CIA {}'.format(accion, orden.courier, current_user.empleado))
    if accion == 'toReady':
        toReady(orden.courier_order_id, current_user.empleado)
    else: 
        if accion == 'toApproved':
            toApproved(orden.id)
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        
        data = request.json
       
        orden = Order_header.query.filter_by(courier_order_id = str(data['id'])).first()
       
        orden.sub_status = traducir_estado(data['status'])
        orden.last_update_date = data['date']
        db.session.commit()

        print('Se actualizo la orden ' + str(orden.order_number) + ' al estado ' + orden.sub_status)
        return '', 200
    else:
        abort(400)





    