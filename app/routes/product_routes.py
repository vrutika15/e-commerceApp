from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Product,Category
from app.forms import ProductForm
from app.decorators import admin_required, super_admin_required
import os 
from werkzeug.utils import secure_filename


product_bp = Blueprint('product',__name__)


# Admin Route to edit product
@product_bp.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required  # Only Admin and Super Admin can edit products
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    # Load categories into form
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        # Update text fields
        product.title = form.title.data
        product.price = form.price.data
        product.description = form.description.data
        product.category_id = form.category_id.data

        # Check for image upload
        if form.image_url.data and hasattr(form.image_url.data, 'filename') and form.image_url.data.filename != '':
            image_file = form.image_url.data
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join('static', 'images')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)
            product.image_url = f'images/{filename}'  # Save relative path

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.manage_products'))

    return render_template('admin_edit_products.html', form=form, product=product)


# Admin Route to delete product
@product_bp.route('/admin/product/delete/<int:product_id>', methods=['GET'])
@login_required
@admin_required  # Only Admin and Super Admin can delete products
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.manage_products'))


#Admin route to view the product detail page:
@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    related_products = Product.query.filter(Product.category_id == product.category_id,Product.id != product.id).limit(3).all()
    return render_template('product_detail.html', product=product, related_products = related_products)



#Submit Review
@product_bp.route('/product/<int:product_id>/submit_review', methods=['POST'])
@login_required
def submit_review(product_id):
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    if not rating or not comment:
        flash('Please fill out all fields.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    new_review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()
    
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('product.product_detail', product_id=product_id))
