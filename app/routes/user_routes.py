from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import db, bcrypt
from app.models import User, Product, Cart
from app.forms import LoginForm, SignupForm

user_bp = Blueprint('user',__name__)



# Home page (User View)
@user_bp.route('/')
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

# User Login Route
@user_bp.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login Successful', 'success')
            return redirect(url_for('user.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('user_login.html', form=form)


# User Signup Route
@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, username=form.username.data, password=hashed_password, role_id=3)  # Default to User role
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully', 'success')
        return redirect(url_for('user.user_login'))
    return render_template('user_signup.html', form=form)

# Cart Route
@user_bp.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_amount = sum([item.product.price * item.quantity for item in cart_items])
    return render_template('user_cart_page.html', cart_items=cart_items, total_amount=total_amount)

# Checkout Route (Stripe Integration)
@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_amount = sum([item.product.price * item.quantity for item in cart_items])

    # Stripe payment processing code here...

    return render_template('user_checkout.html', cart_items=cart_items, total_amount=total_amount)

# Add to Cart
@user_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if cart_item:
        cart_item.quantity += 1  # Increase quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product.id, quantity=1)

    db.session.add(cart_item)
    db.session.commit()
    flash(f'{product.title} added to cart!', 'success')
    return redirect(url_for('user.home'))

# Update Cart Quantity
@user_bp.route('/update_cart/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    try:
        quantity = int(request.form['quantity'])
        if quantity < 1:
            flash('Quantity must be greater than 0', 'warning')
        else:
            cart_item.quantity = quantity
            db.session.commit()
            flash('Cart updated successfully!', 'success')
    except ValueError:
        flash('Invalid quantity entered.', 'danger')
    return redirect(url_for('user.cart'))
