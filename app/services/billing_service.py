from sqlalchemy.orm import Session
from typing import Dict, List
from fastapi import BackgroundTasks

from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.denomination import Denomination

from app.schemas.billing import BillingRequest
from app.services.email_service import send_invoice_email



def calculate_denominations(db: Session, balance: float) -> Dict[int, int]:

    denominations = (
        db.query(Denomination)
        .order_by(Denomination.value.desc())
        .all()
    )

    remaining = int(balance)
    result = {}

    for denom in denominations:
        if remaining <= 0:
            break

        usable_notes = min(
            remaining // denom.value,
            denom.available_count
        )

        if usable_notes > 0:
            result[denom.value] = usable_notes
            remaining -= denom.value * usable_notes

    return result



def generate_bill(db: Session, billing_data: BillingRequest, background_tasks: BackgroundTasks = None):

    total_without_tax = 0
    total_tax = 0

    order_items_data = []

    for item in billing_data.items:

        product = (
            db.query(Product)
            .filter(Product.product_id == item.product_id)
            .first()
        )

        if not product:
            raise Exception(f"Product {item.product_id} not found")

        if product.available_stock < item.quantity:
            raise Exception(
                f"Insufficient stock for product {product.product_id}"
            )

        purchase_price = product.price * item.quantity
        tax_amount = purchase_price * product.tax_percentage / 100
        total_price = purchase_price + tax_amount

        total_without_tax += purchase_price
        total_tax += tax_amount

        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price,
            "tax_amount": tax_amount,
            "total_price": total_price
        })


    total_amount = total_without_tax + total_tax
    balance_amount = billing_data.paid_amount - total_amount

    if balance_amount < 0:
        raise Exception("Paid amount is less than total bill")


    order = Order(
        customer_email=billing_data.customer_email,
        total_without_tax=total_without_tax,
        total_tax=total_tax,
        total_amount=total_amount,
        paid_amount=billing_data.paid_amount,
        balance_amount=balance_amount
    )

    db.add(order)
    db.flush()  # generates order.id before commit


    for item in order_items_data:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            tax_amount=item["tax_amount"],
            total_price=item["total_price"]
        )

        db.add(order_item)

        # Reduce stock
        item["product"].available_stock -= item["quantity"]


    balance_denominations = calculate_denominations(
        db,
        balance_amount
    )


    db.commit()
    db.refresh(order)
    
    # Prepare email data
    email_items = []
    for item in order_items_data:
        email_items.append({
            "product_name": item["product"].name,
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "tax_amount": item["tax_amount"],
            "total_price": item["total_price"]
        })
    
    # Send invoice email asynchronously
    if background_tasks:
        background_tasks.add_task(
            send_invoice_email,
            email_to=billing_data.customer_email,
            order_id=order.id,
            customer_email=order.customer_email,
            items=email_items,
            total_without_tax=total_without_tax,
            total_tax=total_tax,
            total_amount=total_amount,
            paid_amount=billing_data.paid_amount,
            balance_amount=balance_amount,
            balance_denominations=balance_denominations
        )

    return {
        "order_id": order.id,
        "customer_email": order.customer_email,
        "total_without_tax": total_without_tax,
        "total_tax": total_tax,
        "total_amount": total_amount,
        "paid_amount": billing_data.paid_amount,
        "balance_amount": balance_amount,
        "balance_denominations": balance_denominations
    }
