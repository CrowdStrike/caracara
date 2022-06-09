"""
Caracara: Pagination functions.

This file contains code for all types of pagination styles used by the
Falcon APIs, to avoid code repetition within the individual modules.

The endpoints handled here typically return a list of IDs based on some
kind of filter operation. If you are looking for parallised batching
of data dictionaries returned in response to a list of IDs, the batching
code file contains the required code to pull this data down as quickly
as possible.

Three types of paginator are in use:

Style 1 (Numerical Offset)
We paginate by providing a limit (default: 100), and grabbing pages with
that number of items per page. Keep going until len(list of items) == total

It may be theoretically possible to parallise these requests, as an offset
and limit are used instead of a token that changes per page.

Pages are structured like this
{
    "meta": {
        "pagination": {
            "limit": items_per_page_maximum: int,
            "offset": items_to_skip: int,
            "total": total_number_of_items: int,
        }
    }
}



Style 2 (Token Offset)
In this style, a token is returned by the server. When we send the token
to the server, we get the next page of content as well as another token.
We keep requesting data until we have all the items.

It is not possible to parallise these requests because each page depends
on the retrieval of its token from the previous page

Pages are structured like this
{
    "meta": {
            "limit": items_per_page_maximum: int,
            "offset": page_token: str,
            "total": total_number_of_items: int,
    }
}

Style 3
Used in Intel. TBC.
"""
import concurrent.futures
import logging

from functools import partial
from threading import current_thread
from typing import Callable, Dict, List

from caracara.common.batching import batch_data_pull_threads
from caracara.common.constants import PAGINATION_LIMIT, SCROLL_BATCH_SIZE


def all_pages_numbered_offset(
    func: Callable[[Dict[str, Dict]], List[Dict] or List[str]],
    logger: logging.Logger,
    body: Dict = None,
    limit: int = PAGINATION_LIMIT,
):
    """Grab all pages from a paginated call in Style 1 (numerical offset)."""
    logger = logger.getChild("pagination_numbered_offset")
    logger.info(f"Grabbing all pages from the {func.__name__} function (limit: {limit})")

    offset = 0
    found_all = False
    all_resources = []

    while not found_all:
        logger.info(f"Grabbing batch of items {offset + 1} up to {offset + limit}")
        req_body = {
            "limit": limit,
            "offset": offset,
        }
        if body:
            req_body.update(body)

        response = func(body=req_body)['body']
        resources = response['resources']
        logger.info(f"Retrieved a batch of {len(resources)} items")
        logger.debug(response)
        all_resources.extend(resources)

        # If there are no resources returned, we may get a KeyError later
        if not all_resources:
            return []

        if response['meta']['pagination']['total'] > len(all_resources):
            offset = response['meta']['pagination']['offset']
        else:
            found_all = True

    return all_resources


def _numbered_offset_parallel_worker(
    func: Callable[[Dict[str, Dict]], List[Dict] or List[str]] or partial,
    limit: int,
    logger: logging.Logger,
    batch_offset: int,
) -> List[Dict]:
    thread_name = current_thread().name
    if isinstance(func, partial):
        logger.info(
            "%s | Batch worker started with limit %d and offset %d; partial function: %s",
            thread_name, limit, batch_offset, func.func.__name__,
        )
    else:
        logger.info(
            "%s | Batch worker started with offset %s; function: %s",
            thread_name, limit, func.__name__,
        )
    response = func(offset=batch_offset, limit=limit)['body']
    logger.debug("%s | %s", thread_name, response)
    resources = response['resources']
    logger.info("%s | Retrieved %d resources", thread_name, len(resources))

    return resources


def all_pages_numbered_offset_parallel(
    func: Callable[[Dict[str, Dict]], List[Dict] or List[str]] or partial,
    logger: logging.Logger,
    limit: int = PAGINATION_LIMIT,
) -> List[Dict]:
    """Grab all pages from a paginated call in Style 1 (numerical offset), super charged."""
    logger = logger.getChild(__name__)
    if isinstance(func, partial):
        logger.info(
            "Pagination Style 1: Grabbing all pages from the partial %s function (limit: %d)",
            func.func.__name__, limit,
        )
    else:
        logger.info(
            "Pagination Style 1: Grabbing all pages from the %s function (limit: %d)",
            func.__name__, limit,
        )

    # Get the first page to figure out how many items to pull
    logger.info("Grabbing first batch of items 1 to up to %s", limit)
    response = func(offset=0, limit=limit)['body']
    logger.debug(response)

    resources = response['resources']
    logger.info("Retrieved a batch of %d items", len(resources))
    all_resources: List[Dict] = resources

    if not all_resources:
        logger.info("No resources received; returning an empty list")
        return []

    total = response['meta']['pagination']['total']
    logger.info("Total number of resources: %s", total)
    if total == len(all_resources):
        # Received all resources in the first batch
        return all_resources

    """
    List of limits to request from Falcon (e.g., for 301 items, with
    a limit of 100):
    batches = [100,        200,        300]
                ^           ^           ^
               pg2         pg3         pg4
        items 100 - 199  200 - 299  300 - 301

    We already have pg1 (0 - 99) from the first API call
    """
    batches = list(range(limit, total, limit))
    logger.info("Divided offsets into %d of %d", len(batches), limit)
    logger.debug(batches)

    threads = batch_data_pull_threads()

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        partial_worker = partial(_numbered_offset_parallel_worker, func, limit, logger)
        completed = executor.map(
            partial_worker,
            batches,
        )

    for complete in completed:
        logger.debug("Completed a batch")
        all_resources.extend(complete)

    logger.debug("Returning resource list")
    logger.debug(all_resources)
    return all_resources


def all_pages_token_offset(
    func: Callable[[Dict[str, Dict]], List[Dict] or List[str]] or partial,
    logger: logging.Logger,
    limit: int = SCROLL_BATCH_SIZE,
) -> List:
    """Grab all pages from a token offset-based pagination endpoint (Style 2)."""
    logger = logger.getChild(__name__)
    if isinstance(func, partial):
        logger.info(
            "Pagination Style 2: Grabbing all pages from the partial %s function (limit: %d)",
            func.func.__name__, limit,
        )
    else:
        logger.info(
            "Pagination Style 2: Grabbing all pages from the %s function (limit: %d)",
            func.__name__, limit,
        )

    complete = False
    item_ids = []
    offset = None

    current_page = 0

    while not complete:
        current_page += 1
        logger.info(
            "Fetching page %d: %d to up to %d",
            current_page, len(item_ids) + 1, limit * current_page,
        )
        response = func(limit=limit, offset=offset)['body']
        logger.debug(response)
        item_ids.extend(response['resources'])
        if not item_ids:
            # Nothing was returned, so bail out in case the pagination data does not exist
            return []

        if response['meta']['pagination']['total'] > len(item_ids):
            offset = response['meta']['pagination']['offset']
        else:
            complete = True

    logger.debug("Returned IDs:")
    logger.debug(item_ids)

    return item_ids
