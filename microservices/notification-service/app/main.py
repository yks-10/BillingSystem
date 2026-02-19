"""Notification Service FastAPI application."""

from fastapi import FastAPI, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path for shared modules
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.schemas.notification import (
    InvoiceEmailRequest,
    GenericEmailRequest,
    EmailResponse
)
from .config import settings

app = FastAPI(
    title="Notification Service",
    description="Microservice for sending notifications (email, SMS, etc.)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email configuration
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
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)

fm = FastMail(conf)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


def generate_invoice_html(request: InvoiceEmailRequest) -> str:
    """Generate HTML for invoice email."""
    # Build items HTML
    items_html = ""
    for item in request.items:
        items_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{item['product_name']}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{item['unit_price']:.2f}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{item['tax_amount']:.2f}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{item['total_price']:.2f}</td>
        </tr>
        """
    
    # Build denominations HTML
    denominations_html = ""
    if request.balance_denominations:
        for denom, count in sorted(request.balance_denominations.items(), reverse=True):
            denominations_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">₹{denom}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{count}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₹{denom * count:.2f}</td>
            </tr>
            """
    
    denominations_section = f'''
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
    ''' if request.balance_denominations else ''
    
    html = f"""
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
                <p>Order ID: #{request.order_id}</p>
            </div>
            
            <div class="invoice-details">
                <p><strong>Customer Email:</strong> {request.customer_email}</p>
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
                        <td style="text-align: right;">₹{request.total_without_tax:.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Total Tax:</strong></td>
                        <td style="text-align: right;">₹{request.total_tax:.2f}</td>
                    </tr>
                    <tr style="background-color: #e0e0e0;">
                        <td><strong>Grand Total:</strong></td>
                        <td style="text-align: right;"><strong>₹{request.total_amount:.2f}</strong></td>
                    </tr>
                    <tr>
                        <td><strong>Paid Amount:</strong></td>
                        <td style="text-align: right;">₹{request.paid_amount:.2f}</td>
                    </tr>
                    <tr style="background-color: #d4edda;">
                        <td><strong>Balance/Change:</strong></td>
                        <td style="text-align: right;"><strong>₹{request.balance_amount:.2f}</strong></td>
                    </tr>
                </table>
            </div>
            
            {denominations_section}
            
            <div class="footer">
                <p>Thank you for your business!</p>
                <p>This is an automated email. Please do not reply.</p>
            </div>
        </body>
    </html>
    """
    return html


@app.post("/notifications/email/invoice", response_model=EmailResponse)
async def send_invoice_email(request: InvoiceEmailRequest, background_tasks: BackgroundTasks):
    """Send invoice email to customer."""
    try:
        html_body = generate_invoice_html(request)
        
        message = MessageSchema(
            subject=f"Invoice #{request.order_id} - Billing System",
            recipients=[request.email_to],
            body=html_body,
            subtype=MessageType.html
        )
        
        # Send email in background
        background_tasks.add_task(fm.send_message, message)
        
        return EmailResponse(
            success=True,
            message=f"Invoice email queued for {request.email_to}",
            email_id=str(request.order_id)
        )
    except Exception as e:
        return EmailResponse(
            success=False,
            message=f"Failed to send email: {str(e)}"
        )


@app.post("/notifications/email/generic", response_model=EmailResponse)
async def send_generic_email(request: GenericEmailRequest, background_tasks: BackgroundTasks):
    """Send generic email."""
    try:
        message = MessageSchema(
            subject=request.subject,
            recipients=request.recipients,
            body=request.html if request.html else request.body,
            subtype=MessageType.html if request.html else MessageType.plain
        )
        
        # Send email in background
        background_tasks.add_task(fm.send_message, message)
        
        return EmailResponse(
            success=True,
            message=f"Email queued for {len(request.recipients)} recipient(s)"
        )
    except Exception as e:
        return EmailResponse(
            success=False,
            message=f"Failed to send email: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
