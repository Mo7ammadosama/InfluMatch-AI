"""Common response schemas and helpers — WaslAI.jo"""
from math import ceil


def make_page(data: list, total: int, skip: int, limit: int) -> dict:
    """Return a standardised paginated response envelope.

    Shape: {"data": [...], "total": N, "page": P, "pages": PP, "limit": L}
    """
    page  = (skip // limit) + 1 if limit > 0 else 1
    pages = ceil(total / limit) if total > 0 and limit > 0 else 1
    return {"data": data, "total": total, "page": page, "pages": pages, "limit": limit}
