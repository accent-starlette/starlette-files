import time
import typing
import uuid

from sqlalchemy.ext.mutable import MutableDict
from starlette.datastructures import UploadFile

from .exceptions import ContentTypeValidationError
from .mimetypes import guess_extension, magic_mime_from_buffer
from .storages import Storage


class FileAttachment(MutableDict):

    storage: Storage
    directory: str = "files"
    allowed_content_type: typing.List[str] = []

    @staticmethod
    def _guess_content_type(file: typing.IO) -> str:
        content = file.read(1024)

        if isinstance(content, str):
            content = str.encode(content)

        file.seek(0)

        return magic_mime_from_buffer(content)

    def validate(self) -> None:
        if self.content_type not in self.allowed_content_type:
            raise ContentTypeValidationError(
                self.content_type, self.allowed_content_type
            )

    @classmethod
    async def create_from(
        cls, file: UploadFile, original_filename: str
    ) -> "FileAttachment":
        instance = cls()

        unique_name = str(uuid.uuid4())

        instance.original_filename = original_filename
        instance.uploaded_on = time.time()

        # use python magic to get the content type
        content_type = cls._guess_content_type(file.file)
        extension = guess_extension(content_type)

        instance.content_type = content_type
        instance.extension = extension
        instance.saved_filename = f"{unique_name}{extension}"

        # validate
        instance.validate()

        size = instance.storage.put(instance.path, file.file)

        instance.file_size = size

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
