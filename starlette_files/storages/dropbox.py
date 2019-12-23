import typing
from io import BytesIO
from os.path import join

from ..exceptions import MissingDependencyError
from .base import Storage

# Importing optional stuff required by dropbox store
try:
    import dropbox
except ImportError:  # pragma: no cover
    dropbox = None


class DropBoxStorageException(Exception):
    pass


class DropboxStorage(Storage):
    def __init__(
        self, oauth2_access_token: str, root_path: str, timeout: int = 60
    ) -> None:
        if dropbox is None:  # pragma: no cover
            raise MissingDependencyError(
                "dropbox must be installed to use the 'DropboxStorage' class."
            )

        self.root_path = root_path
        self.client = dropbox.Dropbox(oauth2_access_token, timeout=timeout)

    def _full_path(self, name):
        if name == "/":
            name = ""
        return join(self.root_path, name)

    def put(self, filename: str, stream: typing.IO) -> int:
        path = self._full_path(filename)
        stream.seek(0)
        data = stream.read()
        self.client.files_upload(data, path)
        return len(data)

    def delete(self, filename: str) -> None:
        self.client.files_delete(self._full_path(filename))

    def open(self, filename: str, mode: str = "rb") -> typing.IO:
        path = self._full_path(filename)
        file_metadata, response = self.client.files_download(path)
        if response.status_code == 200:
            return BytesIO(response.content)
        raise DropBoxStorageException(
            "Dropbox server returned a {} response when accessing {}".format(
                response.status_code, path
            )
        )

    def locate(self, filename: str) -> str:
        media = self.client.files_get_temporary_link(self._full_path(filename))
        return media.link
