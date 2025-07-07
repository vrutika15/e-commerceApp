from .admin_routes import admin_bp
from .user_routes import user_bp
from .product_routes import product_bp
from .order_routes import order_bp
from .misc_routes import misc_bp
from .superadmin_routes import superadmin_bp
from .cart_routes import cart_bp
from .wishlist_routes import wishlist_bp


def register_blueprints(app):
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(misc_bp)
    app.register_blueprint(superadmin_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)