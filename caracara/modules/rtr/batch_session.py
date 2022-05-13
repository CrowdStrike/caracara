"""Real Time Response (RTR) batch session abstraction class."""
import concurrent.futures
from dataclasses import dataclass
import logging

from datetime import datetime, timedelta
from functools import partial, wraps
from threading import current_thread
from typing import Dict, List

from falconpy import (
    RealTimeResponse,
    RealTimeResponseAdmin,
)

from caracara.common.batching import batch_data_pull_threads
from caracara.modules.rtr.constants import (
    MAX_BATCH_SESSION_HOSTS,
    MAX_BATCH_SESSION_THREADS,
    RTR_COMMANDS,
    SESSION_EXPIRY,
    SESSION_REFRESH_TIMEOUT,
)
from caracara.modules.rtr.get_file import GetFile


def _batch_session_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.batch_sessions is None:
            raise Exception("You must connect to hosts with the connect() function first")

        self.auto_refresh_sessions(self.default_timeout)

        return func(self, *args, **kwargs)
    return wrapper


class InnerRTRBatchSession:  # pylint: disable=too-few-public-methods
    """
    Container class representing a single batch session of up to 10,000 systems.

    Many of these may be used in parallel to support batches of > 10,000 systems.
    These are referred to colloquially as "batches of batches. In other words,
    a batch of batches an RTRBatchSession object, which itself contains
    a list of InnerRTRBatchSession objects.
    """

    batch_id: str = None
    devices: Dict = None
    expiry: datetime = None
    logger: logging.Logger = None

    def __init__(
        self,
        batch_id: str,
        devices: Dict,
        expiry: datetime,
        logger: logging.Logger
    ):
        """Configure an inner batch of RTR sessions."""
        self.batch_id = batch_id
        self.devices = devices
        self.expiry = expiry
        self.logger = logger.getChild(batch_id)

    def __str__(self):
        """Return a loggable string showing the RTR batch ID and system count."""
        return f"{self.batch_id}: {len(self.devices)} devices"


@dataclass
class BatchGetCmdRequest:
    """A batch get request targeted to a specific set of devices within a batch RTR session."""

    batch_get_cmd_req_id: str
    devices: Dict


def generic_rtr_worker(
    session: InnerRTRBatchSession,
    func: partial,
    logger: logging.Logger,
    device_ids: List[str] = None,
):
    """
    Execute a partial function against an RTR batch session.

    This is a generic function designed to be used by a ThreadPoolExecutor
    to execute a partial function against an RTR batch session.
    """
    thread_name = current_thread().name
    logger = logger.getChild(__name__)
    logger.info(
        "%s | Executing %s function against RTR batch: %s (args: %s; kwargs: %s)",
        thread_name, func.func.__name__, session.batch_id, func.args, func.keywords,
    )
    if device_ids:
        device_ids_in_batch = list(
            filter(lambda x: x in session.devices.keys(), device_ids)
        )
        func.keywords['optional_hosts'] = device_ids_in_batch
    response = func(batch_id=session.batch_id)['body']
    logger.debug("%s | %s", thread_name, response)
    return response


class RTRBatchSession:
    """
    Real Time Response (RTR) Batch Session.

    Enables interactions with one or more systems via the RTR API.
    One RTRBatchSession object can connect to an unlimited number of systems by abstracting
    away a list of InnerRTRBatchSession objects.
    Each InnerRTRBatchSession object behind the scenes can communicate with up to 10,000
    individual systems (known as a "batch"). An RTRBatchSession can then multiplex these
    to command "batches of batches" of systems, thus removing the cloud-enforced connection
    limit.
    """

    admin_api: RealTimeResponseAdmin = None
    api: RealTimeResponse = None
    batch_sessions: List[InnerRTRBatchSession] = None
    default_timeout = 30
    logger = logging.getLogger(__name__)

    @_batch_session_required
    def device_ids(self) -> List[str]:
        """Return a list of device IDs from all inner batch sessions."""
        return [x.devices.keys() for x in self.batch_sessions]

    def connect(
        self,
        device_ids: List[str],
        queueing: bool = False,
        timeout: int = default_timeout,
    ):
        """
        Establish a connection to one or more hosts.

        This function must be executed before any other commands can be run.
        """
        self.logger.info("Establishing an RTR batch session with %d systems", len(device_ids))
        self.logger.debug(device_ids)

        batches = []
        for i in range(0, len(device_ids), MAX_BATCH_SESSION_HOSTS):
            batches.append(device_ids[i:i+MAX_BATCH_SESSION_HOSTS])
        self.logger.info("Divided up devices into %d batches", len(batches))

        def worker(batch_device_ids: List[str], batch_func: partial):
            thread_name = current_thread().name
            self.logger.info(
                "%s | Batch worker started with a list of %d devices",
                thread_name, len(batch_device_ids),
            )
            response = batch_func(host_ids=batch_device_ids)['body']
            resources = response['resources']
            self.logger.info("%s | Connected to %s systems", thread_name, len(resources))
            self.logger.debug("%s | %s", thread_name, response)
            batch_data = InnerRTRBatchSession(
                batch_id=response['batch_id'],
                devices=resources,
                expiry=datetime.now() + timedelta(seconds=SESSION_EXPIRY),
                logger=self.logger,
            )
            return batch_data

        batch_func = partial(
            self.api.batch_init_sessions,
            queue_offline=queueing,
            timeout=timeout,
            timeout_duration=f'{timeout}s',
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_BATCH_SESSION_THREADS
        ) as executor:
            completed = executor.map(worker, batches, [batch_func])

        self.batch_sessions = []
        for complete in completed:
            self.logger.info("Completed a batch of RTR connections")
            self.batch_sessions.append(complete)

        device_count = sum(len(d.devices) for d in self.batch_sessions)
        self.logger.info("Connected to %d devices", device_count)
        self.logger.debug(self.batch_sessions)

    @_batch_session_required
    def disconnect(self):
        """Disconnect the RTR batch session."""
        for session in self.batch_sessions:
            self.logger.info("Disconnecting batch RTR session with ID %s", session.batch_id)
            self.api.delete_session(session.batch_id)

    @_batch_session_required
    def get(
        self,
        file_path: str,
        device_ids: List[str] = None,
        timeout: int = default_timeout,
    ) -> List[BatchGetCmdRequest]:
        """
        Upload a file to the Falcon cloud from the path specified.

        This function will execute the GET command against every system within every inner batch
        session. This allows you to retrieve a file at the same path from every connected system.
        Returns a tuple containing the batch get request ID and the responses
        """
        self.logger.info("Using a batch GET to retrieve the file at path %s", file_path)

        partial_get_func = partial(
            self.api.batch_get_command,
            file_path=file_path,
            timeout=timeout,
            timeout_duration=f'{timeout}s',
        )
        partial_worker = partial(generic_rtr_worker, logger=self.logger, device_ids=device_ids)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_BATCH_SESSION_THREADS
        ) as executor:
            completed: List[Dict] = executor.map(
                partial_worker,
                self.batch_sessions,
                [partial_get_func],
            )

        batch_get_cmd_reqs: List[BatchGetCmdRequest] = []
        for complete in completed:
            self.logger.info("Executed commands on a batch of %d hosts", len(complete))
            batch_get_cmd_req = BatchGetCmdRequest(
                batch_get_cmd_req_id=complete['batch_get_cmd_req_id'],
                devices=complete['combined']['resources'],
            )
            batch_get_cmd_reqs.append(batch_get_cmd_req)

        return batch_get_cmd_reqs

    def get_status(
        self,
        batch_get_cmd_reqs: List[BatchGetCmdRequest],
        timeout: int = default_timeout
    ) -> List[GetFile]:
        """
        Get a list of successful file uploads based on a list of batch get command requests.

        Each returned GetFile object will represent a file that has been successfully uploaded as a
        result of a batch get command.
        """
        self.logger.info("Checking the status of %d batch get requests", len(batch_get_cmd_reqs))

        def worker(batch_get_cmd_req: BatchGetCmdRequest, func: partial) -> List[GetFile]:
            thread_name = current_thread().name
            logger = self.logger.getChild(__name__)
            logger.info(
                "%s | Getting the status of batch get request %s",
                thread_name, batch_get_cmd_req.batch_get_cmd_req_id,
            )
            response = func(batch_get_cmd_req_id=batch_get_cmd_req.batch_get_cmd_req_id)['body']
            logger.debug("%s | %s", thread_name, response)

            resources: Dict = response['resources']
            get_files: List[GetFile] = []
            for device_id, get_data in resources.items():
                get_file = GetFile(
                    device_id=device_id,
                    filename=get_data['name'],
                    session_id=get_data['session_id'],
                    sha256=get_data['sha256'],
                    size=get_data['size'],
                    batch_session=self,
                )
                get_files.append(get_file)

            return get_files

        threads = batch_data_pull_threads()
        partial_func = partial(
            self.api.batch_get_command_status,
            timeout=timeout,
            timeout_duration=f'{timeout}s',
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            completed = executor.map(worker, batch_get_cmd_reqs, [partial_func])

        all_get_files: List[GetFile] = []

        for complete in completed:
            all_get_files.extend(complete)

        return all_get_files

    def get_status_by_req_id(
        self,
        batch_get_cmd_req_id: str,
        timeout: int = default_timeout,
    ) -> List[GetFile]:
        """Get a list of successful file uploads based on an individual batch request ID."""
        self.logger.info("Checking the status of a batch get with ID %s", batch_get_cmd_req_id)
        response = self.api.batch_get_command_status(
            batch_get_cmd_req_id=batch_get_cmd_req_id,
            timeout=timeout,
            timeout_duration=f'{timeout}s',
        )['body']
        self.logger.debug(response)
        resources: List[Dict] = response['resources']
        self.logger.info("Batch GET has retrieved %d files so far", len(resources))
        self.logger.debug(resources)

        if not resources:
            return []

        get_files: List[GetFile] = []
        for device_id in resources.keys():
            get_file = GetFile(
                device_id=device_id,
                filename=resources[device_id]['name'],
                session_id=resources[device_id]['session_id'],
                sha256=resources[device_id]['sha256'],
                size=resources[device_id]['size'],
                batch_session=self,
            )
            get_files.append(get_file)

        return get_files

    @_batch_session_required
    def refresh_sessions(self, timeout: int = default_timeout):
        """Refresh a batch RTR session, resetting the timeout back to 10 minutes."""
        self.logger.info("Refreshing batch RTR session")

        def worker(session: InnerRTRBatchSession, func: partial):
            thread_name = current_thread().name
            self.logger.info("%s | Refreshing batch session %s", thread_name, session.batch_id)
            func(batch_id=session.batch_id)
            return session.batch_id

        batch_func = partial(
            self.api.batch_refresh_sessions,
            timeout=timeout,
            timeout_duration=f'{timeout}s',
        )

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_BATCH_SESSION_THREADS
        ) as executor:
            completed = executor.map(worker, self.batch_sessions, [batch_func])

        for complete in completed:
            self.logger.info("Refreshed session %s", complete)

    @_batch_session_required
    def run_generic_command(
        self,
        command_string: str,
        device_ids: List[str] = None,
        timeout: int = default_timeout,
    ) -> Dict:
        """Execute an RTR command against all systems in the batch session."""
        base_command = command_string.split(' ')[0]
        if base_command not in RTR_COMMANDS:
            raise Exception(f"{base_command} is not a valid RTR command")

        self.logger.info("Executing a command via RTR:\n%s", command_string)

        # Permissions level will either be a string (e.g. admin), or
        # a dictionary of further permission levels based on the first
        # command parameter (such as 'query' for the reg command, or
        # -Raw for the runscript command)
        permissions_level = RTR_COMMANDS[base_command]
        if isinstance(permissions_level, dict):
            command_parameter_1 = command_string.split(' ')[1].split('=')[0]
            if command_parameter_1 in permissions_level:
                permissions_level = permissions_level[command_parameter_1]
            else:
                permissions_level = permissions_level['_default']

        if permissions_level == "admin":
            cmd_func = self.admin_api.batch_admin_command
        elif permissions_level == "active_responder":
            cmd_func = self.api.batch_active_responder_command
        elif permissions_level == "read_only":
            cmd_func = self.api.batch_command
        else:
            raise Exception(f"{base_command} does not have a valid permissions level")

        partial_cmd_func = partial(
            cmd_func,
            base_command=base_command,
            command_string=command_string,
            timeout=timeout,
            timeout_duration=f'{timeout}s',
        )
        partial_worker = partial(generic_rtr_worker, logger=self.logger, device_ids=device_ids)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=MAX_BATCH_SESSION_THREADS
        ) as executor:
            completed: List[Dict] = executor.map(
                partial_worker,
                self.batch_sessions,
                [partial_cmd_func],
            )

        all_responses: Dict = {}
        for complete in completed:
            self.logger.info("Executed commands on a batch of %d hosts", len(complete))
            all_responses.update(complete['combined']['resources'])

        return all_responses

    @_batch_session_required
    def run_raw_script(
        self,
        script_text: str,
        script_timeout: int = 60,
        device_ids: List[str] = None,
        timeout: int = None,
    ) -> Dict:
        """Execute a raw RTR script on all systems in the batch session."""
        if not timeout:
            timeout = script_timeout + 10

        self.logger.info(
            "Running a raw script via RTR. Timeout: %d; script timeout: %d",
            timeout, script_timeout,
        )

        command_string = f"runscript -Raw=```{script_text}``` -Timeout={script_timeout}"
        self.logger.debug(command_string)
        resources = self.run_generic_command(command_string, device_ids, timeout)
        return resources

    def auto_refresh_sessions(self, timeout: int = default_timeout):
        """
        Automatically refresh every RTR batch session if they are going to expire soon.

        This function gets called by every function that makes an API request
        to the RTR API. This is done to attempt to ensure that we do not lose
        an active RTR session due to it expiring.
        We will refresh an RTR session before making a call to it if there are
        fewer than three minutes remaining.
        """
        session_near_expiry = False
        for session in self.batch_sessions:
            remaining_secs = (session.expiry - datetime.now()).total_seconds()
            self.logger.debug("RTR session %s has %ds remaining", session.batch_id, remaining_secs)
            if remaining_secs < SESSION_REFRESH_TIMEOUT:
                session_near_expiry = True
        if session_near_expiry:
            self.refresh_sessions(timeout)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        rtr_api: RealTimeResponse,
        rtr_admin_api: RealTimeResponseAdmin,
        default_timeout: int = 30,
        device_ids: List[str] = None,
        queueing: bool = False,
        timeout: int = default_timeout,
    ):
        """
        Create an RTRBatchSession object, representing a batch of remote systems.

        If you pass a list of Device Agent IDs (AIDs), this constructor will automatically
        call the inner connect() function, thus establishing as many batch sessions as required
        to establish remote connections to these systems.
        """
        self.api = rtr_api
        self.admin_api = rtr_admin_api
        self.default_timeout = default_timeout

        # Provides the option to connect straight away on class init
        if device_ids is not None:
            self.connect(
                device_ids=device_ids,
                queueing=queueing,
                timeout=timeout,
            )

    def __enter__(self):
        """Treat an RTR batch session as a context manager."""
        if not self.batch_sessions:
            raise Exception(
                "You should pass device_ids to the constructor to automatically "
                "connect and the context manager functionality"
            )

    def __exit__(self, *args, **kwargs):
        """Disconnect from all systems when leaving the context manager."""
        self.disconnect()
