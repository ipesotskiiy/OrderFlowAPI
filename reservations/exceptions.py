from orders.models import Order, OrderItem
from stocks.models import Stock


class InsufficientStockException(Exception):
    def __init__(self, stock: Stock, order_item: OrderItem):
        self.message = (
            f"Stock {stock.id} available quantity "
            f"{stock.available_quantity} lower than "
            f"order item {order_item.id} quantity "
            f"{order_item.quantity}"
        )

    def __str__(self) -> str:
        return self.message


class StockNotFoundException(Exception):
    def __init__(self, order_item_id: int):
        self.message = f"Stock not found for order item {order_item_id}"

    def __str__(self) -> str:
        return self.message


class InvalidOrderStatusReserveException(Exception):
    def __init__(self):
        self.message = f"Orders with status {Order.Status.DRAFT} only can be reserved"

    def __str__(self) -> str:
        return self.message


class InvalidOrderStatusExpireException(Exception):
    def __init__(self):
        self.message = (f"Orders with status {Order.Status.RESERVED} "
                        f"only can be expired")

    def __str__(self) -> str:
        return self.message


class InvalidTimeExpireOrderException(Exception):
    def __init__(self):
        self.message = "It is too early to change the order status to expired"

    def __str__(self) -> str:
        return self.message


class EmptyOrderException(Exception):
    def __init__(self):
        self.message = "Order items is empty"

    def __str__(self) -> str:
        return self.message


class ReservedQuantityLowerOrderItemQuantityException(Exception):
    def __init__(
        self,
        stock_reserved_quantity,
        order_item_quantity
    ):
        self.message = (
            f"Stock reserved quantity ({stock_reserved_quantity}) "
            f"lower than order item quantity ({order_item_quantity})"
        )

    def __str__(self) -> str:
        return self.message


class EmptyDatetimeConfirmAdvance(Exception):
    def __init__(self, order_obj_id):
        self.message = f"Order {order_obj_id} datetime_confirm_advance is None"

    def __str__(self) -> str:
        return self.message
