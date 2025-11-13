# app\admin\forms.py
# This file defines form classes used in the admin section of the Flask web app.
# It uses Flask-WTF (a Flask extension for working with WTForms) to handle and validate web forms.

from flask_wtf import FlaskForm  
# Imports the FlaskForm base class from flask_wtf.
# All form classes in Flask-WTF must inherit from FlaskForm to get form handling features.

from flask_wtf.file import FileField, FileAllowed  
# Imports FileField (for uploading files) and FileAllowed (for restricting allowed file types).

from wtforms import StringField, DecimalField, IntegerField, SelectField, TextAreaField, SubmitField  
# Imports different types of form fields:
# - StringField: for text input
# - DecimalField: for numeric input with decimals
# - IntegerField: for whole numbers
# - SelectField: for dropdown selection
# - TextAreaField: for multi-line text input
# - SubmitField: for the form’s submit button

from wtforms.validators import DataRequired, NumberRange  
# Imports validators:
# - DataRequired: ensures the field is not empty
# - NumberRange: checks that numeric values fall within a given range

# ----------------------------- PRODUCT FORM -----------------------------
class ProductForm(FlaskForm):  
    # Defines a form for adding or editing product details.

    name = StringField('Product Name', validators=[DataRequired()])  
    # Text input for the product name.
    # 'DataRequired()' means this field must not be left empty.

    category = SelectField('Category', choices=[  
        ('handbag', 'Handbag'),
        ('watch', 'Wristwatch')
    ], validators=[DataRequired()])  
    # Dropdown menu for selecting a product category.
    # Each tuple ('handbag', 'Handbag') represents (value, label).
    # The 'DataRequired()' validator ensures the user selects something.

    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0.01)])  
    # Field for entering the product price.
    # Must not be empty and must be greater than or equal to 0.01.

    stock_level = IntegerField('Stock Quantity', validators=[NumberRange(min=0)])  
    # Field for entering how many units of the product are in stock.
    # Must be 0 or higher (no negative stock allowed).

    description = TextAreaField('Description')  
    # Multi-line text area for optional product description.
    # No validator here — it’s optional.

    image = FileField('Product Image', validators=[  
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])  
    # Field for uploading a product image.
    # Restricts uploads to specific image file types using FileAllowed.

    submit = SubmitField('Add Product')  
    # Button to submit the form.

# ----------------------------- BATCH UPLOAD FORM -----------------------------
class BatchUploadForm(FlaskForm):  
    # Defines a form for uploading a CSV file to import multiple products at once.

    csv_file = FileField('CSV File', validators=[  
        DataRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])  
    # File upload field restricted to CSV files.
    # DataRequired ensures a file is selected before submission.

    submit = SubmitField('Upload & Import')  
    # Button to submit the CSV upload form.
