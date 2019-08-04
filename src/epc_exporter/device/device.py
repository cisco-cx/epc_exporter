from abc import ABC, abstractmethod


class AbstractDevice(ABC):

    @abstractmethod
    def exec(self, command):
        pass


class TestDevice(AbstractDevice):

    def __init__(self, data_dir: str):
        self._data_dir = data_dir
        super().__init__()

    def exec(self, command: str) -> str:
        filename = command.replace(' ', '_')
        data_file = '{}/{}.txt'.format(self._data_dir, filename)
        with open(data_file, 'r') as file:
            return file.read()
