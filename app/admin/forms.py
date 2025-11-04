from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, DecimalField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('handbag', 'Handbag'),
        ('watch', 'Wristwatch')
    ], validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    stock_level = IntegerField('Stock Quantity', validators=[NumberRange(min=0)])
    description = TextAreaField('Description')
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Add Product')