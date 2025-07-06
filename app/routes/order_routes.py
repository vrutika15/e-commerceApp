from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Order
from app.decorators import admin_required, super_admin_required

order_bp = Blueprint('order',__name__)

@order_bp.route('/admin/orders', methods=['GET'])
@login_required
@super_admin_required
def view_orders():
    orders = Order.query.all()
    return render_template('admin_view_orders.html', orders=orders)


@order_bp.route('/admin/order/details/<int:order_id>', methods=['GET'])
@login_required
@admin_required
def view_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin_view_order_details.html', order=order)

@order_bp.route('/admin/order/update_status/<int:order_id>/<string:status>', methods=['GET'])
@login_required
@admin_required  # Ensure only Admins and Super Admins can access this route
def update_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    
    # Check if the status is valid (you can modify this list with other status options as neede
    if status not in ['Completed', 'Pending']:
        flash('Invalid status!', 'danger')
        return redirect(url_for('order.view_orders'))
    
    # Update the status of the order
    order.status = status
    db.session.commit()
    
    flash(f'Order status updated to {status}!', 'success')
    return redirect(url_for('order.view_orders'))

@order_bp.route('/admin/order/cancel/<int:order_id>', methods=['GET'])
@login_required
@admin_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == 'Completed':
        flash('Completed orders cannot be canceled.', 'danger')
    else:
        order.status = 'Canceled'
        db.session.commit()
        flash('Order has been canceled.', 'success')
    
    return redirect(url_for('order.view_orders'))


@order_bp.route('/order/confirmation/<int:order_id>', methods=['GET'])
@login_required
def order_confirmation(order_id):
    # Fetch the order based on the order ID
    order = Order.query.get_or_404(order_id)


    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('order.home'))

    return render_template('user_order_confirmation.html', order=order)