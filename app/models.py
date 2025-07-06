from app.extensions import db
from datetime import datetime
from enum import Enum
from flask_login import UserMixin


#Product Likes
product_likes = db.Table(
    'product_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

#wishlist (also many products are stored in wishlist)
wishlist_items = db.Table(
    'wishlist_items',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

# Enum for Order Status
class OrderStatusEnum(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'

# Enum for Payment Status
class PaymentStatusEnum(Enum):
    UNPAID = 'unpaid'
    PAID = 'paid'
    REFUNDED = 'refunded'


# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationship to User
    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'


# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', back_populates='users')

    user_info = db.relationship('UserInfo', back_populates='user', uselist=False)
    cart = db.relationship('Cart', back_populates='user', uselist=False)
    orders = db.relationship('Order', back_populates='user', lazy=True)
    reviews = db.relationship('Review', back_populates='user', lazy=True)


    # NEW: Many-to-many relationship to liked products
    liked_products = db.relationship('Product',secondary='product_likes',back_populates='liked_by_users',lazy='dynamic')

    #wishlist:
    wishlist = db.relationship('Product', secondary='wishlist_items', back_populates='wishlisted_by_users', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


     # Optional helper methods for wishlist
    def has_in_wishlist(self, product):
        return self.wishlist.filter(wishlist_items.c.product_id == product.id).count() > 0

    def add_to_wishlist(self, product):
        if not self.has_in_wishlist(product):
            self.wishlist.append(product)

    def remove_from_wishlist(self, product):
        if self.has_in_wishlist(product):
            self.wishlist.remove(product)

    # Optional helper methods for likes
    def has_liked_product(self, product):
        return self.liked_products.filter(product_likes.c.product_id == product.id).count() > 0

    def like_product(self, product):
        if not self.has_liked_product(product):
            self.liked_products.append(product)

    def unlike_product(self, product):
        if self.has_liked_product(product):
            self.liked_products.remove(product)


# UserInfo Model
class UserInfo(db.Model):
    __tablename__ = 'users_info'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    street_address = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    state = db.Column(db.String(150), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='user_info')

    def __repr__(self):
        return f'<UserInfo {self.full_name}>'



# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', back_populates='products')

    reviews = db.relationship('Review', back_populates='product', lazy=True)

    liked_by_users = db.relationship('User', secondary='product_likes', back_populates='liked_products', lazy='dynamic')

    wishlisted_by_users = db.relationship('User', secondary='wishlist_items', back_populates='wishlist', lazy='dynamic')

    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum([r.rating for r in self.reviews]) / len(self.reviews), 2)

    def __repr__(self):
        return f'<Product {self.title}>'


# Category Model
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    products = db.relationship('Product', back_populates='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


# Review Model
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.rating}>'


# Cart Model
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='cart')

    is_ordered = db.Column(db.Boolean, default=False, nullable=False)

    items = db.relationship('CartItem', back_populates='cart', lazy=True)

    def __repr__(self):
        return f'<Cart {self.id}>'


# CartItem Model (split from OrderItem)
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)

    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product')

    def __repr__(self):
        return f'<CartItem {self.product_id} x {self.quantity}>'


# Order Model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatusEnum), default=PaymentStatusEnum.UNPAID, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address = db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='orders')

    items = db.relationship('OrderItem', back_populates='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'


# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.product_id} x {self.quantity}>'
