"""device module provides the abstract and test device module """

from abc import ABC, abstractmethod


class AbstractDevice(ABC):
    """Abstract device class """

    @abstractmethod
    def exec(self, command):
        """
        Execute command, requires session to be established
        before executing command
        """
        pass

    @abstractmethod
    def start_session(self):
        """ Start a new device session """
        pass

    @abstractmethod
    def stop_session(self):
        """ Stop the device session """
        pass

    @abstractmethod
    def enable_test_commands(self):
        """
        EPC specific: enables test command mode on the EPC device.
        Test mode is required to allow for running vppctl commands
        """
        pass


class TestDevice(AbstractDevice):
    """Test device class, loads command output from filesystem """

    def __init__(self, data_dir: str):
        self._data_dir = data_dir
        super().__init__()

    def start_session(self):
        pass

    def stop_session(self):
        pass

    def enable_test_commands(self):
        pass

    def exec(self, command: str) -> str:
        filename = command.replace(' ', '_').replace('"', '')
        data_file = '{}/{}.txt'.format(self._data_dir, filename)
        with open(data_file, 'r') as file:
            return file.read()
