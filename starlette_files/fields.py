import time
import typing
import uuid

from sqlalchemy.ext.mutable import MutableDict

from .constants import MB
from .exceptions import (
    ContentTypeValidationError,
    MaximumAllowedFileLengthError,
    MissingDependencyError,
)
from .helpers import get_length
from .mimetypes import guess_extension, magic_mime_from_buffer
from .storages import Storage

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


class FileAttachment(MutableDict):

    storage: Storage
    directory: str = "files"
    allowed_content_types: typing.List[str] = []
    max_length = MB * 2

    @staticmethod
    def _guess_content_type(file: typing.IO) -> str:
        content = file.read(1024)

        if isinstance(content, str):
            content = str.encode(content)

        file.seek(0)

        return magic_mime_from_buffer(content)

    def set_defaults(self, file: typing.IO, original_filename: str) -> None:
        unique_name = str(uuid.uuid4())

        self.original_filename = original_filename
        self.uploaded_on = time.time()

        # use python magic to get the content type
        content_type = self._guess_content_type(file)
        extension = guess_extension(content_type)

        self.content_type = content_type
        self.extension = extension
        self.file_size = get_length(file)
        self.saved_filename = f"{unique_name}{extension}"

    def validate(self) -> None:
        if self.content_type not in self.allowed_content_types:
            raise ContentTypeValidationError(
                self.content_type, self.allowed_content_types
            )
        if self.file_size > self.max_length:
            raise MaximumAllowedFileLengthError(self.max_length)

    @classmethod
    async def create_from(
        cls, file: typing.IO, original_filename: str
    ) -> "FileAttachment":
        instance = cls()

        instance.set_defaults(file, original_filename)
        instance.validate()

        instance.storage.put(instance.path, file)

        return instance

    @property
    def original_filename(self) -> str:
        return self.get("original_filename")

    @original_filename.setter
    def original_filename(self, value: str) -> None:
        self["original_filename"] = value

    @property
    def saved_filename(self) -> str:
        return self.get("saved_filename")

    @saved_filename.setter
    def saved_filename(self, value: str) -> None:
        self["saved_filename"] = value

    @property
    def uploaded_on(self) -> float:
        return self.get("uploaded_on")

    @uploaded_on.setter
    def uploaded_on(self, value: float):
        self["uploaded_on"] = value

    @property
    def file_size(self) -> int:
        return self.get("file_size")

    @file_size.setter
    def file_size(self, value: int):
        self["file_size"] = value

    @property
    def content_type(self) -> str:
        return self.get("content_type")

    @content_type.setter
    def content_type(self, value: str) -> None:
        self["content_type"] = value

    @property
    def extension(self) -> typing.Optional[str]:
        return self.get("extension")

    @extension.setter
    def extension(self, value: str) -> None:
        self["extension"] = value

    @property
    def path(self) -> str:
        return f"{self.directory}/{self.saved_filename}"

    @property
    def locate(self) -> str:
        return self.storage.locate(self.path)

    @property
    def open(self) -> typing.IO:
        return self.storage.open(self.path)


class ImageAttachment(FileAttachment):

    directory: str = "images"
    allowed_content_types: typing.List[str] = ["image/jpeg", "image/png"]

    @classmethod
    async def create_from(
        cls, file: typing.IO, original_filename: str
    ) -> "ImageAttachment":
        if Image is None:
            raise MissingDependencyError(
                "pillow must be installed to use the 'ImageAttachment' class."
            )

        instance = cls()

        instance.set_defaults(file, original_filename)
        instance.validate()

        instance.width, instance.height = Image.open(file).size

        instance.storage.put(instance.path, file)

        return instance

    @property
    def width(self) -> int:
        return self.get("width")

    @width.setter
    def width(self, value: int) -> None:
        self["width"] = value

    @property
    def height(self) -> int:
        return self.get("height")

    @height.setter
    def height(self, value: int) -> None:
        self["height"] = value
