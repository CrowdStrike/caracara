"""
Caracara batching support.

This module contains all the required code to generically parallelise retrieval of data batches.

The endpoints handled here typically look for a list of IDs in the body
and return back a dictionary of data.

For paginated results that send back IDs, the pagination code file contains
the required code to pull this data down as quickly as possible.
"""
import concurrent.futures
import logging
import multiprocessing

from functools import partial
from threading import current_thread
from typing import Callable, Dict, List

from caracara.common.constants import DATA_BATCH_SIZE


BATCH_LOGGER = logging.getLogger(__name__)


def batch_data_pull_threads() -> int:
    """
    Return maximum number of threads to spin up in a thread pool.

    Result is either 20, or 2x the number of cores, whichever is smallest.
    """
    cores = multiprocessing.cpu_count()
    thread_count = min(cores * 2, 20)
    BATCH_LOGGER.debug("Will use up to %d threads for batch data retrieval", thread_count)
    return thread_count


def batch_get_data(lookup_ids: str, func: Callable[[object, List[str], str], Dict]):
    """Retrieve details for the list of AIDs provided.

    Arguments
    ---------
    lookup_ids: str
        List of IDs to retrieve data for.
    func: Python function, object
        Method to call by each created thread.

    Returns
    -------
    dict: A dictionary of all results returned.
    """
    resources = []

    BATCH_LOGGER.info("Batch data retrieval for %s (%d items)", func.__name__, len(lookup_ids))
    BATCH_LOGGER.debug(str(lookup_ids))

    # Divide the list of item IDs into a list of lists, each of size DATA_BATCH_SIZE
    batches = [lookup_ids[i:i+DATA_BATCH_SIZE] for i in range(0, len(lookup_ids), DATA_BATCH_SIZE)]
    BATCH_LOGGER.info("Divided the item IDs into %d batches", len(batches))

    threads = batch_data_pull_threads()

    def worker(batch_func: Callable[[List[str]], Dict], worker_lookup_ids: List[str]) -> Dict:
        thread_name = current_thread().name
        BATCH_LOGGER.info(
            "%s | Batch worker started with a list of %d items. Function: %s",
            thread_name, len(worker_lookup_ids), batch_func.__name__,
        )
        resources = batch_func(ids=worker_lookup_ids)["body"]["resources"]
        BATCH_LOGGER.info("%s | Retrieved %d resources", thread_name, len(resources))
        BATCH_LOGGER.debug("%s | %s", thread_name, resources)

        return resources

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        partial_worker = partial(worker, func)
        completed = executor.map(partial_worker, batches)

    for complete in completed:
        BATCH_LOGGER.debug("Completed a batch")
        resources.extend(complete)

    resources_dict = {}
    for resource in resources:
        if 'id' in resource:
            resources_dict[resource['id']] = resource
        elif 'device_id' in resource:
            resources_dict[resource['device_id']] = resource
        else:
            raise Exception("No ID field to build the dictionary from")

    BATCH_LOGGER.debug("Returned resources")
    BATCH_LOGGER.debug(resources_dict)

    return resources_dict
