import time
import typing
import uuid
from io import BytesIO

from sqlalchemy.ext.mutable import MutableDict

from .exceptions import ContentTypeValidationError, MissingDependencyError
from .mimetypes import guess_extension, magic_mime_from_buffer
from .storages import Storage

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


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
        cls, file: typing.IO, original_filename: str
    ) -> "FileAttachment":
        instance = cls()

        unique_name = str(uuid.uuid4())

        instance.original_filename = original_filename
        instance.uploaded_on = time.time()

        # use python magic to get the content type
        content_type = cls._guess_content_type(file)
        extension = guess_extension(content_type)

        instance.content_type = content_type
        instance.extension = extension
        instance.saved_filename = f"{unique_name}{extension}"

        # validate
        instance.validate()

        size = instance.storage.put(instance.path, file)

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

    @property
    def open(self) -> typing.IO:
        return self.storage.open(self.path)


class ImageAttachment(FileAttachment):

    directory: str = "images"
    allowed_content_type: typing.List[str] = ["image/jpeg", "image/png"]

    @classmethod
    async def create_from(
        cls, file: typing.IO, original_filename: str
    ) -> "ImageAttachment":
        if Image is None:
            raise MissingDependencyError(
                "pillow must be installed to use the 'ImageAttachment' class."
            )

        instance = cls()

        unique_name = str(uuid.uuid4())

        instance.original_filename = original_filename
        instance.uploaded_on = time.time()

        # use python magic to get the content type
        content_type = cls._guess_content_type(file)
        extension = guess_extension(content_type)

        instance.content_type = content_type
        instance.extension = extension
        instance.saved_filename = f"{unique_name}{extension}"

        # validate
        instance.validate()

        output = BytesIO()

        with Image.open(file) as image:
            instance.width, instance.height = image.size
            image.save(output, image.format)

        size = instance.storage.put(instance.path, output)
        instance.file_size = size

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
