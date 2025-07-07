from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.decorators import admin_required
from app import db
from app.models import Product, Category, Review
from app.forms import ProductForm, ReviewForm
import os
from werkzeug.utils import secure_filename


product_bp = Blueprint('product', __name__)

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


# Route to show product detail and submit review (GET and POST)
@product_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id).limit(3).all()
    reviews = Review.query.filter_by(product_id=product_id).all()
    form = ReviewForm()

    # Handling review submission via POST (traditional form)
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            product_id=product.id
        )
        db.session.add(review)
        db.session.commit()
        flash("Review submitted successfully!", "success")
        return redirect(url_for('product.product_detail', product_id=product_id))

    return render_template('product_detail.html', product=product, related_products=related_products, reviews=reviews, form=form)


# Route to handle review submission (AJAX)
# @product_bp.route('/submit_review/<int:product_id>', methods=['POST'])
# @login_required
# def submit_review(product_id):
    # product = Product.query.get_or_404(product_id)
    # form = ReviewForm()
# 
    # if form.validate_on_submit():
        # review = Review(
            # rating=form.rating.data,
            # comment=form.comment.data,
            # user_id=current_user.id,
            # product_id=product.id
        # )
        # db.session.add(review)
        # db.session.commit()
# 
        # Return a JSON response after saving the review
        # return jsonify(success=True)
# 
    # return jsonify(success=False)
