from decimal import Decimal


class InvalidOrderStatusForPaymentException(Exception):
    def __init__(self):
        self.message = "Orders with status Reserved only can be paid"

    def __str__(self) -> str:
        return self.message


class OrderHasPaymentException(Exception):
    def __init__(self, order_id: int):
        self.message = f"Order {order_id} already has payment"

    def __str__(self) -> str:
        return self.message


class PaymentPartException(Exception):
    def __init__(
        self,
        full_sum: Decimal,
        advance: Decimal,
        remaining: Decimal,
    ):
        self.message = (
            f"Payment amounts must be greater than zero."
            f"Your parts: full sum {full_sum}, advance: {advance}, "
            f"remaining: {remaining}"
        )

    def __str__(self) -> str:
        return self.message


class DoubleAdvancePaidException(Exception):
    def __init__(self):
        self.message = "Advance already paid"

    def __str__(self) -> str:
        return self.message
