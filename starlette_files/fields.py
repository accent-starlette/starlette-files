import hashlib
import io
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
from .image.filter import ImageFilter
from .image.rect import Rect
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
        self.uploaded_on = int(time.time())

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
    def create_from(cls, file: typing.IO, original_filename: str) -> "FileAttachment":
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
    def uploaded_on(self) -> int:
        return self.get("uploaded_on")

    @uploaded_on.setter
    def uploaded_on(self, value: int):
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
    def create_from(cls, file: typing.IO, original_filename: str) -> "ImageAttachment":
        if Image is None:
            raise MissingDependencyError(
                "pillow must be installed to use the 'ImageAttachment' class."
            )

        instance = cls()

        instance.set_defaults(file, original_filename)
        instance.validate()

        with Image.open(file) as image:
            instance.width, instance.height = image.size

        instance.storage.put(instance.path, file)

        return instance

    def get_focal_point(self) -> typing.Union[Rect, None]:
        if None in [
            self.focal_point_x,
            self.focal_point_y,
            self.focal_point_width,
            self.focal_point_height,
        ]:
            return None

        return Rect(
            self.focal_point_x,
            self.focal_point_y,
            self.focal_point_x + self.focal_point_width,
            self.focal_point_y + self.focal_point_height,
        )

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

    @property
    def focal_point_x(self) -> int:
        return self.get("focal_point_x")

    @focal_point_x.setter
    def focal_point_x(self, value: int) -> None:
        self["focal_point_x"] = value

    @property
    def focal_point_y(self) -> int:
        return self.get("focal_point_y")

    @focal_point_y.setter
    def focal_point_y(self, value: int) -> None:
        self["focal_point_y"] = value

    @property
    def focal_point_width(self) -> int:
        return self.get("focal_point_width")

    @focal_point_width.setter
    def focal_point_width(self, value: int) -> None:
        self["focal_point_width"] = value

    @property
    def focal_point_height(self) -> int:
        return self.get("focal_point_height")

    @focal_point_height.setter
    def focal_point_height(self, value: int) -> None:
        self["focal_point_height"] = value

    @property
    def cache_key(self) -> str:
        """
        can be used in renditions to check if the original image has changed
        since the rendition was created to determine whether the rendition
        needs to be recreated. 
        """

        vary_fields = [
            str(self.file_size),
            str(self.focal_point_x),
            str(self.focal_point_y),
            str(self.focal_point_width),
            str(self.focal_point_height),
        ]
        vary_string = "-".join(vary_fields)
        return hashlib.sha1(vary_string.encode("utf-8")).hexdigest()[:8]


class ImageRenditionAttachment(FileAttachment):
    directory: str = "image-renditions"
    focal_point = None

    @classmethod
    def create_from(  # type: ignore
        cls, attachment: "ImageAttachment", filter_specs: typing.List[str] = []
    ) -> "ImageRenditionAttachment":
        instance = cls()

        instance.focal_point = attachment.get_focal_point()

        filter_cls = ImageFilter(specs=filter_specs)

        with attachment.open as original_file:
            with Image.open(original_file) as original_image:
                unique_name = str(uuid.uuid4())
                generated_bytes = filter_cls.run(instance, original_image, io.BytesIO())
                instance.cache_key = attachment.cache_key
                instance.file_size = get_length(generated_bytes)

                with Image.open(generated_bytes) as generated_image:
                    image_format = generated_image.format.lower()
                    content_type = f"image/{image_format}"
                    extension = guess_extension(content_type)

                    instance.content_type = content_type
                    instance.extension = extension
                    instance.saved_filename = f"{unique_name}{extension}"
                    instance.width, instance.height = generated_image.size

                    instance.storage.put(instance.path, generated_bytes)

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

    @property
    def cache_key(self) -> str:
        return self.get("cache_key")

    @cache_key.setter
    def cache_key(self, value: str) -> None:
        self["cache_key"] = value
