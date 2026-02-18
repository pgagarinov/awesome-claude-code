"""Analysis module using polars - demonstrates LSP with third-party libs."""

import polars as pl

from .models import Inventory, Product


def create_sample_inventory() -> Inventory:
    inv = Inventory()
    inv.add_product(Product("Laptop", 999.99, "Electronics", 50))
    inv.add_product(Product("Mouse", 29.99, "Electronics", 200))
    inv.add_product(Product("Notebook", 4.99, "Stationery", 500))
    inv.add_product(Product("Pen", 1.99, "Stationery", 1000))
    return inv


def inventory_to_dataframe(inventory: Inventory) -> pl.DataFrame:
    """Convert inventory to a Polars DataFrame."""
    return pl.DataFrame(
        {
            "name": [p.name for p in inventory.products],
            "price": [p.price for p in inventory.products],
            "category": [p.category for p in inventory.products],
            "quantity": [p.quantity for p in inventory.products],
            "total_value": [p.total_value() for p in inventory.products],
        }
    )


def analyze_by_category(df: pl.DataFrame) -> pl.DataFrame:
    """Group by category and compute aggregates."""
    return df.group_by("category").agg(
        pl.col("total_value").sum().alias("category_total"),
        pl.col("quantity").sum().alias("total_units"),
        pl.col("price").mean().alias("avg_price"),
    )


def find_expensive_products(df: pl.DataFrame, threshold: float) -> pl.DataFrame:
    """Filter products above a price threshold."""
    return df.filter(pl.col("price") > threshold)


def main() -> None:
    inv = create_sample_inventory()
    df = inventory_to_dataframe(inv)
    print(df)

    summary = analyze_by_category(df)
    print("\nCategory summary:")
    print(summary)

    expensive = find_expensive_products(df, 10.0)
    print(f"\nProducts over $10:")
    print(expensive)


if __name__ == "__main__":
    main()
