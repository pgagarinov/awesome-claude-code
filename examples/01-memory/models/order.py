"""Order data model."""


class Order:
    def __init__(self, order_id: int, total: float) -> None:
        self.order_id = order_id
        self.total = total
