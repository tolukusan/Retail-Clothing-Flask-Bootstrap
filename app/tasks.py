from flask import render_template
from flask_mail import Message
# Import mail and the Celery instance from the top-level app package
from app import mail 


def send_welcome_email( recipient_email, username):
    
    msg = Message(
        subject="Welcome to Our Community!",
        recipients=[recipient_email],
        html=render_template(
            'emails/welcome.html', 
            username=username, 
        )
    )
    
    try:
        # Flask-Mail works automatically inside the Celery ContextTask
        mail.send(msg)
        print(f"Background Task: Successfully sent welcome email to {recipient_email}")
        return 'SUCCESS'
    except Exception as e:
        # Log failure and instruct Celery to retry later
        print(f"Background Task: FAILED to send email to {recipient_email}. Retrying in 60s. Error: {e}")
    
def send_order_confirmation_email(user, order, order_items):
    """
    Sends order confirmation email with details.
    """
    msg = Message(
        subject=f"Order #{order.order_id} Confirmed!",
        recipients=[user.email],
        sender="no-reply@yourapp.com"
    )

    # Plain text version
    msg.body = f"""
Hello {user.name},

Thank you for your order! Here are the details:

Order ID: #{order.order_id}
Date: {order.order_date.strftime('%B %d, %Y at %I:%M %p')}
Payment Method: {order.payment_method}

Items:
"""
    for item in order_items:
        msg.body += f"- {item.product.name} x{item.qty} @ £{item.price_at_purchase:.2f} = £{item.price_at_purchase * item.qty:.2f}\n"

    msg.body += f"""
Subtotal: £{order.sub_total:.2f}
Shipping: £{order.shipping_cost:.2f}
Grand Total: £{order.grand_total:.2f}

Your order is being processed. We'll notify you when it's shipped.

Thanks for shopping with us!
"""

    # Optional: HTML version (nicer)
    msg.html = f"""
    <h2>Order #{order.order_id} Confirmed!</h2>
    <p>Hi <strong>{user.name}</strong>,</p>
    <p>Thank you for your order!</p>

    <ul>
        <li><strong>Order ID:</strong> #{order.order_id}</li>
        <li><strong>Date:</strong> {order.order_date.strftime('%B %d, %Y at %I:%M %p')}</li>
        <li><strong>Payment:</strong> {order.payment_method}</li>
    </ul>

    <h3>Items:</h3>
    <table border="0" cellpadding="5" cellspacing="0">
    """
    for item in order_items:
        msg.html += f"""
        <tr>
            <td>{item.product.name}</td>
            <td>x{item.qty}</td>
            <td>@ £{item.price_at_purchase:.2f}</td>
            <td>= £{item.price_at_purchase * item.qty:.2f}</td>
        </tr>
        """
    msg.html += f"""
    </table>

    <hr>
    <p><strong>Subtotal:</strong> £{order.sub_total:.2f}</p>
    <p><strong>Shipping:</strong> £{order.shipping_cost:.2f}</p>
    <p><strong>Grand Total:</strong> £{order.grand_total:.2f}</p>

    <p>We'll email you again when your order ships.</p>
    <p>Thanks for shopping with us!</p>
    """

    try:
        mail.send(msg)
        print(f"Order confirmation email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send order email: {e}")
        # Optional: log or flash in production    