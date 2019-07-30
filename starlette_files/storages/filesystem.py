import typing
from os import makedirs, remove
from os.path import abspath, dirname, exists, join

from ..constants import KB
from ..helpers import copy_stream
from .base import Storage


class FileSystemStorage(Storage):
    def __init__(self, root_path: str, chunk_size: int = 32 * KB):
        self.root_path = abspath(root_path)
        self.chunk_size = chunk_size

    def _get_physical_path(self, filename: str) -> str:
        return join(self.root_path, filename)

    def put(self, filename: str, stream: typing.IO) -> int:
        physical_path = self._get_physical_path(filename)
        physical_directory = dirname(physical_path)

        if not exists(physical_directory):
            makedirs(physical_directory, exist_ok=True)

        stream.seek(0)

        with open(physical_path, mode="wb") as target_file:
            return copy_stream(stream, target_file, chunk_size=self.chunk_size)

    def delete(self, filename: str) -> None:
        physical_path = self._get_physical_path(filename)
        remove(physical_path)

    def open(self, filename: str, mode: str = "rb") -> typing.IO:
        return open(self._get_physical_path(filename), mode=mode)

    def locate(self, filename: str) -> str:
        return f"{self.root_path}/{filename}"
