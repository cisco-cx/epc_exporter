from abc import ABC, abstractmethod


class AbstractDevice(ABC):
    @abstractmethod
    def exec(self, command):
        pass

    @abstractmethod
    def start_session(self):
        pass

    @abstractmethod
    def stop_session(self):
        pass

    @abstractmethod
    def enable_test_commands(self):
        pass


class TestDevice(AbstractDevice):
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
