from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, URL, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProductForm(FlaskForm):
    title = StringField('Product Title', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[Length(max=255)])
    image_url =  FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!'), Optional()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Product')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')
