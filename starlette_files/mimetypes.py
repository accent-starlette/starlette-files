import mimetypes as mdb
import typing

import magic


def magic_mime_from_buffer(buffer: bytes) -> str:
    return magic.from_buffer(buffer, mime=True)


def guess_extension(mimetype: str) -> typing.Optional[str]:
    """
    Due the python bugs 'image/jpeg' overridden:
    - https://bugs.python.org/issue4963
    - https://bugs.python.org/issue1043134
    - https://bugs.python.org/issue6626#msg91205
    """

    if mimetype == "image/jpeg":
        return ".jpeg"
    return mdb.guess_extension(mimetype)
