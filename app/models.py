from app.extensions import db
from datetime import datetime
from enum import Enum
from flask_login import UserMixin

# Association Tables
product_likes = db.Table(
    'product_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

wishlist_items = db.Table(
    'wishlist_items',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

# Enums
class OrderStatusEnum(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'

class PaymentStatusEnum(Enum):
    UNPAID = 'unpaid'
    PAID = 'paid'
    REFUNDED = 'refunded'

class ShipmentStatusEnum(Enum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

# Role
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'

# User
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
    orders = db.relationship('Order', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')

    liked_products = db.relationship('Product', secondary=product_likes, back_populates='liked_by_users', lazy='dynamic')
    wishlist = db.relationship('Product', secondary=wishlist_items, back_populates='wishlisted_by_users', lazy='dynamic')

    def has_in_wishlist(self, product):
        return self.wishlist.filter(wishlist_items.c.product_id == product.id).count() > 0

    def add_to_wishlist(self, product):
        if not self.has_in_wishlist(product):
            self.wishlist.append(product)

    def remove_from_wishlist(self, product):
        if self.has_in_wishlist(product):
            self.wishlist.remove(product)

    def has_liked_product(self, product):
        return self.liked_products.filter(product_likes.c.product_id == product.id).count() > 0

    def like_product(self, product):
        if not self.has_liked_product(product):
            self.liked_products.append(product)

    def unlike_product(self, product):
        if self.has_liked_product(product):
            self.liked_products.remove(product)

    def __repr__(self):
        return f'<User {self.username}>'

# UserInfo
class UserInfo(db.Model):
    __tablename__ = 'users_info'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20))
    street_address = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    state = db.Column(db.String(150), nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='user_info')

    def __repr__(self):
        return f'<UserInfo {self.first_name} {self.last_name}>'

# Category
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship('Product', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'

# Product
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', back_populates='products')

    reviews = db.relationship('Review', back_populates='product')
    liked_by_users = db.relationship('User', secondary=product_likes, back_populates='liked_products', lazy='dynamic')
    wishlisted_by_users = db.relationship('User', secondary=wishlist_items, back_populates='wishlist', lazy='dynamic')

    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 2)

    def __repr__(self):
        return f'<Product {self.title}>'

# Review
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.rating}>'

# Cart
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)
    is_ordered = db.Column(db.Boolean, default=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='cart')

    items = db.relationship('CartItem', back_populates='cart')

    def __repr__(self):
        return f'<Cart {self.id}>'

# CartItem
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

# Order
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

    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))
    coupon = db.relationship('Coupon', back_populates='orders')

    invoice = db.relationship('Invoice', back_populates='order', uselist=False)
    shipment = db.relationship('Shipment', back_populates='order', uselist=False)
    payment = db.relationship('Payment', back_populates='order', uselist=False)
    items = db.relationship('OrderItem', back_populates='order')

    def __repr__(self):
        return f'<Order {self.id}>'

# OrderItem
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

# Payment
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(PaymentStatusEnum), default=PaymentStatusEnum.UNPAID, nullable=False)

    order = db.relationship('Order', back_populates='payment')

    def __repr__(self):
        return f'<Payment {self.id} - {self.status}>'

# Shipment
class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100))
    shipped_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    shipment_status = db.Column(db.Enum(ShipmentStatusEnum), default=ShipmentStatusEnum.PENDING, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True)
    order = db.relationship('Order', back_populates='shipment')

    def __repr__(self):
        return f'<Shipment {self.id} - {self.shipment_status}>'

# Coupon
class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Float)
    discount_amount = db.Column(db.Float)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)

    orders = db.relationship('Order', back_populates='coupon')

    def apply_discount(self, original_amount):
        discount = 0
        if self.discount_amount:
            discount = self.discount_amount
        elif self.discount_percent:
            discount = original_amount * (self.discount_percent / 100)
        return round(original_amount - discount, 2), round(discount, 2)

    def __repr__(self):
        return f'<Coupon {self.code}>'

# Invoice
class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    issued_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float,  nullable=True)
    paid = db.Column(db.Boolean, default=False)

    order = db.relationship('Order', back_populates='invoice')

    def __repr__(self):
        return f'<Invoice {self.invoice_number} for Order {self.order_id}>'
