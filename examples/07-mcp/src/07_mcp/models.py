"""Data models for demonstrating LSP features."""

from dataclasses import dataclass, field


@dataclass
class Product:
    name: str
    price: float
    category: str
    quantity: int = 0

    def total_value(self) -> float:
        return self.price * self.quantity

    def apply_discount(self, percent: float) -> float:
        discount = self.price * (percent / 100)
        return self.price - discount


@dataclass
class Inventory:
    products: list[Product] = field(default_factory=list)

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def total_inventory_value(self) -> float:
        return sum(p.total_value() for p in self.products)

    def find_by_category(self, category: str) -> list[Product]:
        return [p for p in self.products if p.category == category]
