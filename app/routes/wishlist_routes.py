# In wishlist_routes.py (create this file)
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Product
from app.extensions import db

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    data = request.get_json()
    product_id = data.get('product_id')
    product = Product.query.get_or_404(product_id)
    
    current_user.add_to_wishlist(product)
    db.session.commit()
    
    return jsonify({'success': True})