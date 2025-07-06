from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm
from app.models import User, Product, Order
from app.extensions import db, bcrypt
from werkzeug.security import check_password_hash
from app.decorators import super_admin_required
import pandas as pd
from io import BytesIO
from fpdf import FPDF


superadmin_bp = Blueprint('superadmin',__name__)

@superadmin_bp.route('/login', methods=['GET', 'POST'])
def superadmin_login():
    form = LoginForm() 

    if form.validate_on_submit():  
        superadmin = User.query.filter_by(email=form.email.data).first()
        if superadmin and bcrypt.check_password_hash(superadmin.password, form.password.data):
            login_user(superadmin)
            if superadmin.role.name == 'Super Admin':
                flash ('Login successfull!','success')
                return redirect(url_for('superadmin.superadmin_dashboard'))
            else:
                flash('Not authorized for admin access', 'danger')
                return redirect(url_for('superadmin.superadmin_login'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('superadmin/login.html', form=form) 


# Superadmin dashboard (after login)
@superadmin_bp.route('/superadmin/dashboard')
@login_required
@super_admin_required  
def superadmin_dashboard():
    if current_user.role.name not in ['Super Admin']:
        return redirect(url_for('superadmin.superadmin_login'))
    products = Product.query.all()
    return render_template('superadmin/superadmin_dashboard.html', products=products)


@superadmin_bp.route('/superadmin/manage-users')
@login_required
@super_admin_required
def manage_users():
    users = User.query.all()
    return render_template('superadmin/manage_users.html', users=users)


# Manage Products Page
@superadmin_bp.route('/superadmin/manage-products')
@login_required
@super_admin_required
def manage_products():
    products = Product.query.all()
    return render_template('superadmin/manage_products.html', products=products)

# Manage Orders Page
@superadmin_bp.route('/superadmin/manage-orders')
@login_required
@super_admin_required
def manage_orders():
    orders = Order.query.all()
    return render_template('superadmin/manage_orders.html', orders=orders)

# Reports Page
@superadmin_bp.route('/superadmin/reports')
@login_required
@super_admin_required
def reports():
    return render_template('superadmin/reports.html')

# Invoices Page
@superadmin_bp.route('/superadmin/invoices')
@login_required
@super_admin_required
def manage_invoices():
    return render_template('superadmin/manage_invoices.html')

# Download CSV
@superadmin_bp.route('/superadmin/download/<string:data_type>/csv')
@login_required
@super_admin_required
def download_csv(data_type):
    data = get_data_as_df(data_type)
    output = BytesIO()
    data.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, download_name=f"{data_type}_report.csv", as_attachment=True, mimetype='text/csv')

# Download Excel
@superadmin_bp.route('/superadmin/download/<string:data_type>/excel')
@login_required
@super_admin_required
def download_excel(data_type):
    data = get_data_as_df(data_type)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return send_file(output, download_name=f"{data_type}_report.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Download PDF
@superadmin_bp.route('/superadmin/download/<string:data_type>/pdf')
@login_required
@super_admin_required
def download_pdf(data_type):
    data = get_data_as_df(data_type)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    col_width = 190 // len(data.columns)
    for col in data.columns:
        pdf.cell(col_width, 10, col, border=1)
    pdf.ln()
    for i, row in data.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return send_file(output, download_name=f"{data_type}_report.pdf", as_attachment=True, mimetype='application/pdf')

# Utility function
def get_data_as_df(data_type):
    if data_type == 'users':
        data = User.query.with_entities(User.id, User.name, User.email).all()
        return pd.DataFrame(data, columns=['ID', 'Name', 'Email'])
    elif data_type == 'products':
        data = Product.query.with_entities(Product.id, Product.name, Product.price).all()
        return pd.DataFrame(data, columns=['ID', 'Name', 'Price'])
    elif data_type == 'orders':
        data = Order.query.with_entities(Order.id, Order.status, Order.total_amount).all()
        return pd.DataFrame(data, columns=['ID', 'Status', 'Total Amount'])
    else:
        return pd.DataFrame()
