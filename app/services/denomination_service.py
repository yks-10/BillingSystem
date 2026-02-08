from sqlalchemy.orm import Session
from typing import Dict

from app.models.denomination import Denomination


def calculate_denominations(db: Session, balance_amount: float) -> Dict[int, int]:
    """
    Calculate balance denominations using greedy approach.

    Args:
        db: Database session
        balance_amount: amount to return to customer

    Returns:
        Dictionary with denomination value as key
        and count as value.
        Example: {500: 1, 50: 2, 20: 1}
    """

    if balance_amount <= 0:
        return {}

    denominations = (
        db.query(Denomination)
        .order_by(Denomination.value.desc())
        .all()
    )

    remaining_amount = int(balance_amount)
    result = {}

    for denom in denominations:

        if remaining_amount <= 0:
            break

        # maximum notes that can be used
        usable_count = min(
            remaining_amount // denom.value,
            denom.available_count
        )

        if usable_count > 0:
            result[denom.value] = usable_count
            remaining_amount -= denom.value * usable_count

    return result
