from abc import ABC, abstractmethod
from typing import Optional

class Outputer(ABC):
    @abstractmethod
    def output(self, content: str) -> None:
        """输出给定的内容"""
        ...


class PrintOutputer(Outputer):
    def output(self, content: str) -> None:
        print(content)


class FileOutputer(Outputer):
    DEFAULT_PATH = 'product_report.txt'

    def __init__(self, path: Optional[str] = DEFAULT_PATH, **kwargs) -> None:
        self.path = path

    def output(self, content: str) -> None:
        with open(self.path, 'a') as f:
            f.write(f'{content}\n')


class CombineOutputer(Outputer):
    def __init__(self) -> None:
        self._print_outputer = PrintOutputer()
        self._file_outputer = FileOutputer()

    def output(self, content: str) -> None:
        self._print_outputer.output(content)
        self._file_outputer.output(content)
