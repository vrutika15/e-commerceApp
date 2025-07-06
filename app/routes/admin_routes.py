from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Product, Role
from app.forms import LoginForm, ProductForm, SignupForm
from app.decorators import admin_required, super_admin_required
import os 
from app.models import Category
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin',__name__)

# Admin Login Route
@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            if admin.role.name == 'Admin' or admin.role.name == 'Super Admin':
                flash('Login successful!', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Not authorized for admin access', 'danger')
                return redirect(url_for('admin.admin_login'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('admin_login.html', form=form)


# Admin dashboard (after login)
@admin_bp.route('/admin/dashboard')
@login_required
@admin_required  # Restrict access to Admin and Super Admin only
def admin_dashboard():
    if current_user.role.name not in ['Admin', 'Super Admin']:
        return redirect(url_for('admin.admin_login'))
    products = Product.query.all()
    return render_template('admin_dashboard.html', products=products)


# Manage products (Admin and Super Admin)
@admin_bp.route('/admin/manage_products', methods=['GET', 'POST'])
@login_required
@admin_required  # Only Admin and Super Admin can manage products
def manage_products():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():   
        # Handle image upload
        image_file = form.image_url.data
        image_relative_path = None


        if image_file:
            # Secure the filename and save the image
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'images')
            os.makedirs(upload_folder, exist_ok=True)


            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)

            image_relative_path = f'images/{filename}'


        # Create a new product object with form data
        product = Product(
            title=form.title.data,
            price=form.price.data,
            description=form.description.data,
            image_url=image_relative_path,  # Store the image path in DB
            category_id=form.category_id.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('admin.manage_products'))
    
    products = Product.query.all()
    return render_template('admin_manage_products.html', form=form, products=products)


# Manage users (Super Admin only)
@admin_bp.route('/admin/manage_users')
@login_required
@super_admin_required  # Only Super Admin can manage users
def manage_users():
    users = User.query.all()
    return render_template('admin_manage_users.html', users=users)


# Super Admin Route to Edit User (For managing roles, etc.)
@admin_bp.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required  # Only Super Admin can edit users
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()  # Fetch all roles from the database

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        
        # Only update the password if it's provided
        if request.form['password']:
            user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        user.role_id = request.form['role_id']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))  # Redirect to the users management page
    
    return render_template('admin_edit_users.html', user=user, roles=roles)


# Super Admin Route to Delete User
@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['GET'])
@login_required
@super_admin_required  # Only Super Admin can delete users
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))