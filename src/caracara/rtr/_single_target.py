"""Single target interactions"""
from .._tool import Tool


class SingleTarget(Tool):
    """Class to represent single target interactions"""

    BASE_COMMAND = "run"  # This will prolly need to dynamic

    def connect_to_host(self: object, aid: str):
        """
        Initializes a RTR session with
        the host matching the AID provided
        """
        hdr = f"Initializing session with host {aid}"
        self.display(f"{hdr}")

        session = self.api.rtr.init_session(body={
            "device_id": aid
            })
        if session["status_code"] == 201:
            sess_id = session["body"]["resources"][0]["session_id"]
            self.display(f"{hdr} [ {sess_id} ]")
        else:
            sess_id = False
            self.display(f"{hdr} [ FAILED ]")

        return sess_id

    def disconnect_from_host(self: object, session_id: str):
        """
        Deletes the RTR session as specified by session ID
        and then returns the status code.
        """
        self.display(f"Disconnecting session {session_id}")
        return self.api.rtr.delete_session(session_id=session_id)["status_code"]

    @classmethod
    def set_base_command(cls: object, command: str):
        """Determines the base command based upon the value of the provided command"""
        # Not sure if this is the way to go
        if command[:3].lower() == "ls ":
            returned = "ls"
        elif command[:4].lower() == "cat ":
            returned = "cat"
        elif command[:10] == "runscript ":
            returned = "runscript"
        else:
            returned = cls.BASE_COMMAND

        return returned

    def execute_command(self: object, cmd: str, sess_id: str):
        """
        Executes a RTR Admin command, waits for it to complete,
        and then returns the result
        """
        payload = {}
        payload["base_command"] = self.set_base_command(cmd)
        payload["session_id"] = sess_id
        payload["command_string"] = cmd
        req = self.api.rtr_admin.execute_admin_command(payload)
        if req["status_code"] != 201:
            # print(req["body"]["errors"][0]["message"])
            # raise SystemExit(
            #     "Unable to execute command. "
            #     )
            returned = req["body"]["errors"][0]["message"]
        else:
            request_id = req["body"]["resources"][0]["cloud_request_id"]
            completed = False
            hdr = "Waiting on command to finish executing"
            self.display(hdr)
            # cnt = 1
            while not completed:
                self.display(hdr)
                # cnt += 1
                requested = self.api.rtr_admin.check_admin_command_status(
                    cloud_request_id=request_id,
                    sequence_id=0
                    )
                try:
                    completed = requested["body"]["resources"][0]["complete"]
                except IndexError:
                    print(requested)    # Move to a debug handler

            self.display(f"{hdr} complete!")
            # Need to wire in an error handler here and pass stderr

            returned = requested["body"]["resources"][0]["stdout"]

        return returned
