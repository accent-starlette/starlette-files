import inspect

from ...exceptions import InvalidFilterSpecError

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


class Operation:
    def __init__(self, method, *args):
        self.method = method
        self.args = args

        # Check arguments
        try:
            inspect.getcallargs(self.construct, *args)
        except TypeError as e:
            raise InvalidFilterSpecError(e)

        # Call construct
        try:
            self.construct(*args)
        except ValueError as e:
            raise InvalidFilterSpecError(e)

    def construct(self, *args):
        raise NotImplementedError()

    def run(self, pillow, attachment, env: dict) -> Image:
        raise NotImplementedError()
