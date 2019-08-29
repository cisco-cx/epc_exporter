"""
device module provides the remote device module.
This device uses ssh to collect command outputs on the device
"""

from paramiko import SSHClient, WarningPolicy
from paramiko_expect import SSHClientInteraction

from device import AbstractDevice

PROMPT = '.*# '


class RemoteDevice(AbstractDevice):
    """ Remote device """

    def __init__(self, hostname, username, password, test_password=None):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._test_pasword = test_password
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(WarningPolicy())
        self._session = None
        self._test_commands_enabled = False
        super().__init__()

    def start_session(self):
        self.client.connect(hostname=self._hostname,
                            username=self._username,
                            password=self._password)

        interact = SSHClientInteraction(self.client, timeout=10, display=True)
        interact.expect(PROMPT)
        self._session = interact

    def stop_session(self):
        self._session.send("exit")
        self._session.expect()
        self._session.close()
        self._session = None

    def enable_test_commands(self):
        if self._session is None:
            return ""

        if not self._test_commands_enabled:
            self._session.send("cli test-commands")
            self._session.expect("Password:")
            self._session.send(self._test_pasword)
            self._session.expect(PROMPT)
            self._test_commands_enabled = True

    def exec(self, command: str) -> str:
        if self._session is None:
            return ""
        # send command
        self._session.send(command)
        self._session.expect(PROMPT)

        cmd_output_uname = self._session.current_output_clean

        return cmd_output_uname
