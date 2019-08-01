from ..utils import to_rgb
from .base import Operation

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


class MinMaxOperation(Operation):
    def construct(self, size):
        width_str, height_str = size.split("x")
        self.width = int(width_str)
        self.height = int(height_str)

    def run(self, pillow, attachment, env):
        image_width, image_height = pillow.size

        horz_scale = self.width / image_width
        vert_scale = self.height / image_height

        if self.method == "min":
            if image_width <= self.width or image_height <= self.height:
                return

            if horz_scale > vert_scale:
                width = self.width
                height = int(image_height * horz_scale)
            else:
                width = int(image_width * vert_scale)
                height = self.height

        elif self.method == "max":
            if image_width <= self.width and image_height <= self.height:
                return

            if horz_scale < vert_scale:
                width = self.width
                height = int(image_height * horz_scale)
            else:
                width = int(image_width * vert_scale)
                height = self.height

        else:
            # Unknown method
            return

        # convert 1 and P images to RGB to improve resize quality
        pillow = to_rgb(pillow)

        return pillow.resize((width, height), Image.ANTIALIAS)
