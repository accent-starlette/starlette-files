import typing

from ..constants import KB


class Storage:
    """ The abstract base class for all stores. """

    def put(self, filename: str, stream: typing.IO) -> int:
        """
        Should be overridden in inherited class and puts the file-like object
        as the given filename in the store.

        :param filename: the target filename.
        :param stream: the source file-like object
        :return: length of the stored file.
        """
        raise NotImplementedError()

    def delete(self, filename: str) -> None:
        """
        Should be overridden in inherited class and deletes the given file.

        :param filename: The filename to delete
        """
        raise NotImplementedError()

    def open(self, filename: str, mode: str = "rb") -> typing.IO:
        """
        Should be overridden in inherited class and return a file-like object
        representing the file in the store.
        :param filename: The filename to open.
        :param mode: same as the `mode` in famous :func:`.open` function.
        """
        raise NotImplementedError()

    def locate(self, filename: str) -> str:
        """
        If overridden in the inherited class, should locate the file's url
        to share in public space or a path of some sort to locate it.

        This method is not used internally by starlette-files it is just a 
        handy helper that gets returned by an Attachment property.

        :param filename: The filename to locate.
        """
        raise NotImplementedError()
