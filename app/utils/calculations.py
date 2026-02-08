def calculate_item_total(price: float, quantity: int, tax_percentage: float):
    """
    Calculate purchase price, tax and total price for an item.
    """

    purchase_price = price * quantity
    tax_amount = purchase_price * tax_percentage / 100
    total_price = purchase_price + tax_amount

    return purchase_price, tax_amount, total_price


def calculate_final_amount(total_without_tax: float, total_tax: float):
    """
    Calculate final total amount.
    """
    return total_without_tax + total_tax


def calculate_balance(paid_amount: float, total_amount: float):
    """
    Calculate balance amount to return.
    """
    return paid_amount - total_amount
