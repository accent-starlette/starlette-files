import typing
from io import BytesIO

from .constants import KB


def copy_stream(source, target: typing.IO, *, chunk_size: int = 16 * KB) -> int:
    length = 0
    while 1:
        buf = source.read(chunk_size)
        if not buf:
            break
        length += len(buf)
        target.write(buf)
    return length


def get_length(source: typing.IO) -> int:
    buffer = BytesIO()
    return copy_stream(source, buffer)
