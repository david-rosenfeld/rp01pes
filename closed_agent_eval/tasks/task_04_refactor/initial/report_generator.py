"""Report generation module."""


def generate_sales_report(sales_data: list[dict]) -> str:
    """Generate a sales report."""
    lines = []
    lines.append("=" * 50)
    lines.append("SALES REPORT")
    lines.append("=" * 50)
    lines.append("")

    total = 0
    for sale in sales_data:
        lines.append(f"  {sale['product']}: ${sale['amount']:.2f}")
        total += sale['amount']

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"  TOTAL: ${total:.2f}")
    lines.append("=" * 50)

    return "\n".join(lines)


def generate_inventory_report(inventory_data: list[dict]) -> str:
    """Generate an inventory report."""
    lines = []
    lines.append("=" * 50)
    lines.append("INVENTORY REPORT")
    lines.append("=" * 50)
    lines.append("")

    total_items = 0
    for item in inventory_data:
        lines.append(f"  {item['name']}: {item['quantity']} units")
        total_items += item['quantity']

    lines.append("")
    lines.append("-" * 50)
    lines.append(f"  TOTAL ITEMS: {total_items}")
    lines.append("=" * 50)

    return "\n".join(lines)
