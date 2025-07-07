from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Product, CartItem, Cart

cart_bp = Blueprint('cart', __name__)


#cart route to add product to cart
@cart_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if cart_item:
        cart_item.quantity += 1  # Increase quantity if the item is already in the cart
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product.id, quantity=1)  # Add a new item to the cart

    db.session.add(cart_item)
    db.session.commit()
    flash(f'{product.title} added to cart!', 'success')
    return redirect(url_for('user.cart'))