from orders.models import OrderItem, Order
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


class InvalidOrderStatusException(Exception):
    def __init__(self):
        self.message = f"Orders with status {Order.Status.DRAFT} only can be reserved"

    def __str__(self) -> str:
        return self.message


class EmptyOrderException(Exception):
    def __init__(self):
        self.message = "Order items is empty"

    def __str__(self) -> str:
        return self.message
