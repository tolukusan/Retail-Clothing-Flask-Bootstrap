from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class WalletTopUpForm(FlaskForm):
    """
    Form to handle the user topping up their wallet balance.
    """
    amount = DecimalField(
        'Top-Up Amount (£)',
        validators=[
            DataRequired(message="A top-up amount is required."),
            NumberRange(min=0.01, message="Amount must be a positive value.")
        ],
        places=2  # Ensures input is treated as currency with two decimal places
    )
    submit = SubmitField('Top Up Wallet')
