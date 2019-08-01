from ..utils import to_rgb
from .base import Operation

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


class WidthHeightOperation(Operation):
    def construct(self, size):
        self.size = int(size)

    def run(self, pillow, attachment, env):
        image_width, image_height = pillow.size

        if self.method == "width":
            if image_width <= self.size:
                return

            scale = self.size / image_width

            width = self.size
            height = int(image_height * scale)

        elif self.method == "height":
            if image_height <= self.size:
                return

            scale = self.size / image_height

            width = int(image_width * scale)
            height = self.size

        else:
            # Unknown method
            return

        # convert 1 and P images to RGB to improve resize quality
        pillow = to_rgb(pillow)

        return pillow.resize((width, height), Image.ANTIALIAS)
