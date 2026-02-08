from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import BackgroundTasks
from typing import Dict, List
from app.core.config import settings
from pathlib import Path


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates' / 'email'
)

fm = FastMail(conf)


async def send_invoice_email(
    email_to: str,
    order_id: int,
    customer_email: str,
    items: List[Dict],
    total_without_tax: float,
    total_tax: float,
    total_amount: float,
    paid_amount: float,
    balance_amount: float,
    balance_denominations: Dict[int, int]
):
    """
    Send invoice email to customer.
    
    Args:
        email_to: Customer email address
        order_id: Order ID
        customer_email: Customer email
        items: List of order items
        total_without_tax: Subtotal without tax
        total_tax: Total tax amount
        total_amount: Grand total
        paid_amount: Amount paid by customer
        balance_amount: Change to be returned
        balance_denominations: Breakdown of change denominations
    """
    
    # Prepare email body
    items_html = ""
    for item in items:
        items_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{item['product_name']}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{item['unit_price']:.2f}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{item['tax_amount']:.2f}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{item['total_price']:.2f}</td>
        </tr>
        """
    
    denominations_html = ""
    if balance_denominations:
        for denom, count in sorted(balance_denominations.items(), reverse=True):
            denominations_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">₹{denom}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{count}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{denom * count:.2f}</td>
            </tr>
            """
    
    html_body = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .invoice-header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .invoice-details {{ margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #f2f2f2; padding: 12px; text-align: left; border: 1px solid #ddd; }}
                .total-section {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="invoice-header">
                <h1>INVOICE</h1>
                <p>Order ID: #{order_id}</p>
            </div>
            
            <div class="invoice-details">
                <p><strong>Customer Email:</strong> {customer_email}</p>
                <p><strong>Date:</strong> {order_id}</p>
            </div>
            
            <h2>Order Items</h2>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
                        <th style="text-align: center;">Quantity</th>
                        <th style="text-align: right;">Unit Price</th>
                        <th style="text-align: right;">Tax</th>
                        <th style="text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="total-section">
                <table style="width: 400px; margin-left: auto;">
                    <tr>
                        <td><strong>Subtotal (without tax):</strong></td>
                        <td style="text-align: right;">₹{total_without_tax:.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Total Tax:</strong></td>
                        <td style="text-align: right;">₹{total_tax:.2f}</td>
                    </tr>
                    <tr style="background-color: #e0e0e0;">
                        <td><strong>Grand Total:</strong></td>
                        <td style="text-align: right;"><strong>₹{total_amount:.2f}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Paid Amount:</strong></td>
                        <td style="text-align: right;">₹{paid_amount:.2f}</td>
                    </tr>
                    <tr style="background-color: #d4edda;">
                        <td><strong>Balance/Change:</strong></td>
                        <td style="text-align: right;"><strong>₹{balance_amount:.2f}</strong></td>
                    </tr>
                </table>
            </div>
            
            {f'''
            <h2>Change Denominations</h2>
            <table style="width: 400px;">
                <thead>
                    <tr>
                        <th>Denomination</th>
                        <th style="text-align: center;">Count</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {denominations_html}
                </tbody>
            </table>
            ''' if balance_denominations else ''}
            
            <div class="footer">
                <p>Thank you for your business!</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject=f"Invoice #{order_id} - Billing System",
        recipients=[email_to],
        body=html_body,
        subtype=MessageType.html
    )
    
    try:
        await fm.send_message(message)
        print(f"Invoice email sent successfully to {email_to}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
