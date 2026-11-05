from orders.models import OrderItem
from stocks.models import Stock


class InvalidOrderStatusCancelException(Exception):
    def __init__(self):
        self.message = "Orders with status Confirmed only can be cancelled"

    def __str__(self) -> str:
        return self.message


class AdvanceNotPaidException(Exception):
    def __init__(self, order_id: int):
        self.message = f"Advance is not paid in order {order_id}"

    def __str__(self) -> str:
        return self.message


class NoAdvancePaidDateException(Exception):
    def __init__(self, order_id: int):
        self.message = f"No datetime advance is not paid in order {order_id}"

    def __str__(self) -> str:
        return self.message


class LateCancelOrderException(Exception):
    def __init__(self, order_id: int):
        self.message = f"Order {order_id} already can't be cancelled"

    def __str__(self) -> str:
        return self.message


class ReservedQuantityStockException(Exception):
    def __init__(self, stock: Stock, order_item: OrderItem):
        self.message = (
            f"Stock {stock.id} reserved quantity "
            f"{stock.reserved_quantity} lower than "
            f"order item {order_item.id} quantity "
            f"{order_item.quantity}"
        )

    def __str__(self) -> str:
        return self.message

class AdvanceReturnException(Exception):
    def __init__(self, order_id: int):
        self.message = f"Advance already return for order {order_id}"

    def __str__(self) -> str:
        return self.message
