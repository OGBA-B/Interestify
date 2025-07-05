from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


def paginate_results(items: List[T], offset: int = 0, limit: int = 50) -> List[T]:
    """
    Paginate a list of items

    Args:
        items: List of items to paginate
        offset: Starting index
        limit: Number of items per page

    Returns:
        Paginated list of items
    """
    if offset < 0:
        offset = 0

    if limit <= 0:
        limit = 50

    start_index = offset
    end_index = offset + limit

    return items[start_index:end_index]


def create_paginated_response(
    items: List[T], offset: int, limit: int, total_items: int
) -> PaginatedResponse[T]:
    """
    Create a paginated response object

    Args:
        items: List of items for current page
        offset: Starting index
        limit: Number of items per page
        total_items: Total number of items

    Returns:
        PaginatedResponse object
    """
    page = (offset // limit) + 1 if limit > 0 else 1
    total_pages = (total_items + limit - 1) // limit if limit > 0 else 1

    # Special handling for zero limit
    if limit == 0:
        has_next = False
        has_previous = False
    else:
        has_next = offset + limit < total_items
        has_previous = offset > 0

    return PaginatedResponse(
        items=items,
        total=total_items,
        page=page,
        page_size=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )
