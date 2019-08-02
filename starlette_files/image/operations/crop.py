from ..rect import Rect
from .base import Operation


class CropOperation(Operation):
    def construct(self, size=None):
        if size:
            left_str, top_str, width_str, height_str = size.split("x")
            self.left = int(left_str)
            self.top = int(top_str)
            self.width = int(width_str)
            self.height = int(height_str)

    def run(self, pillow, attachment, env):
        image_width, image_height = pillow.size
        focal_point = attachment.focal_point

        if hasattr(self, "left"):
            crop_x = min(self.left, image_width - 1)
            crop_y = min(self.top, image_height - 1)

            remaining_after_x = image_width - crop_x
            remaining_after_y = image_height - crop_y

            max_crop_width = min(self.width, crop_x * 2, remaining_after_x * 2)
            max_crop_height = min(self.height, crop_y * 2, remaining_after_y * 2)

            rect = Rect.from_point(crop_x, crop_y, max_crop_width, max_crop_height)

            pillow = pillow.crop(rect)

        elif focal_point:
            pillow = pillow.crop(focal_point)

        return pillow
