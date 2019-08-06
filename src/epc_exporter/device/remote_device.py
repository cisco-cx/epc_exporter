from paramiko import SSHClient, WarningPolicy
from paramiko_expect import SSHClientInteraction

from device import AbstractDevice

PROMPT = '.*# '


class RemoteDevice(AbstractDevice):

    def __init__(self, hostname, username, password):
        self._hostname = hostname
        self._username = username
        self._password = password
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(WarningPolicy())
        self._session = None
        super().__init__()

    def start_session(self):
        self.client.connect(hostname=self._hostname, username=self._username, password=self._password)

        interact = SSHClientInteraction(self.client, timeout=10, display=True)
        interact.expect(PROMPT)
        self._session = interact

    def stop_session(self):
        self._session.send("exit")
        self._session.expect()
        self._session.close()

    def exec(self, command: str) -> str:
        if self._session is None:
            return ""

        '''send command'''
        self._session.send(command)
        self._session.expect(PROMPT)

        cmd_output_uname = self._session.current_output_clean

        return cmd_output_uname
