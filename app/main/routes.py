from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User, Company, Order_header, Customer, Order_detail
from app.main.interfaces import cargar_pedidos

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


@bp.route('/pedidos', methods=['GET', 'POST'])
@login_required
def ver_pedidos():
   # pedidos = cargar_pedidos()
    ordenes =  Order_header.query.filter_by(store=current_user.store).all()
    return render_template('pedidos.html', title='Pedidos', ordenes=ordenes)



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
    
    db.session.commit()
    return render_template('pedidos.html', title='Pedidos')

@bp.route('/cargar_pedidos', methods=['GET', 'POST'])
@login_required
def upload_pedidos():
    cargar_pedidos()
    #ordenes =  Order_header.query.all()
    ordenes =  Order_header.query.filter_by(store=current_user.store).all()
    #for i in ordenes:
    #    flash('ordenes id:{} nro:{} empresa: {} store {}'.format(i.id, i.order_number, i.store, current_user.store))
    return render_template('pedidos.html', title='Pedidos', ordenes=ordenes)


@bp.route('/cargar_empresa', methods=['GET', 'POST'])
@login_required
def cargar_empresa():
    unaEmpresa = Company(
        store_id = '1447373',
        platform = 'TIendaNube',
        store_name = 'Demo Boris'
    )

    db.session.add(unaEmpresa)
    db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))

@bp.route('/orden/<orden_id>')
@login_required
def orden(orden_id):
    orden = Order_detail.query.filter_by(order=orden_id).all()
    return render_template('orden.html', orden=orden)
    