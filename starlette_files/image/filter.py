import typing

from ..exceptions import InvalidImageOperationError
from . import operations, utils


class ImageFilter:

    _registered_operations = None

    def __init__(self, specs: typing.List[str]):
        self.specs = specs

    @property
    def operations(self):
        # search for operations
        self._search_for_operations()

        ops = []

        # ensure all requested specs are valid and build the list of operations
        for op_spec in self.specs:
            op_spec_parts = op_spec.split("-")

            if op_spec_parts[0] not in self._registered_operations:
                raise InvalidImageOperationError(
                    "Unrecognised operation: %s" % op_spec_parts[0]
                )

            op_class = self._registered_operations[op_spec_parts[0]]
            ops.append(op_class(*op_spec_parts))

        return ops

    def run(self, attachment, image, output):
        original_format = image.format

        env = {"original-format": original_format}

        for operation in self.operations:
            image = operation.run(image, attachment, env) or image

        if "output-format" in env:
            output_format = env["output-format"].upper()
        else:
            output_format = original_format

        if output_format == "JPEG":
            image = utils.to_rgb(image)
            image.save(
                output, output_format, quality=85, progressive=True, optimize=True
            )

        elif output_format == "PNG":
            image.save(output, output_format, optimize=True)

        return output

    @classmethod
    def _search_for_operations(cls):
        if cls._registered_operations is not None:
            return

        registered = [
            ("original", operations.DoNothingOperation),
            ("width", operations.WidthHeightOperation),
            ("height", operations.WidthHeightOperation),
            ("min", operations.MinMaxOperation),
            ("max", operations.MinMaxOperation),
            ("fill", operations.FillOperation),
            ("crop", operations.CropOperation),
            ("scale", operations.ScaleOperation),
            ("format", operations.FormatOperation),
        ]

        cls._registered_operations = dict(registered)
