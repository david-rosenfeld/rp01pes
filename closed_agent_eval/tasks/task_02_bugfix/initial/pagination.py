"""Pagination utilities."""


def paginate(items: list, page: int, per_page: int = 10) -> dict:
    """
    Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Page number (1-indexed)
        per_page: Items per page

    Returns:
        Dict with 'items', 'page', 'total_pages', 'has_next', 'has_prev'
    """
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page

    start = page * per_page
    end = start + per_page

    page_items = items[start:end]

    return {
        'items': page_items,
        'page': page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }
