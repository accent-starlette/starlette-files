from ..rect import Rect
from ..utils import to_rgb
from .base import Operation

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


class FillOperation(Operation):
    def construct(self, size, *extra):
        # Get width and height
        width_str, height_str = size.split("x")
        self.width = int(width_str)
        self.height = int(height_str)

        # Crop closeness
        self.crop_closeness = 0

        for extra_part in extra:
            if extra_part.startswith("c"):
                self.crop_closeness = int(extra_part[1:])
            else:
                raise ValueError("Unrecognised filter spec part: %s" % extra_part)

        # Divide it by 100 (as it's a percentage)
        self.crop_closeness /= 100

        # Clamp it
        if self.crop_closeness > 1:
            self.crop_closeness = 1

    def run(self, pillow, attachment, env):
        image_width, image_height = pillow.size
        focal_point = attachment.focal_point

        # Get crop aspect ratio
        crop_aspect_ratio = self.width / self.height

        # Get crop max
        crop_max_scale = min(image_width, image_height * crop_aspect_ratio)
        crop_max_width = crop_max_scale
        crop_max_height = crop_max_scale / crop_aspect_ratio

        # Initialise crop width and height to max
        crop_width = crop_max_width
        crop_height = crop_max_height

        # Use crop closeness to zoom in
        if focal_point is not None:
            # Get crop min
            crop_min_scale = max(
                focal_point.width, focal_point.height * crop_aspect_ratio
            )
            crop_min_width = crop_min_scale
            crop_min_height = crop_min_scale / crop_aspect_ratio

            # Sometimes, the focal point may be bigger than the image...
            if not crop_min_scale >= crop_max_scale:
                # Calculate max crop closeness to prevent upscaling
                max_crop_closeness = max(
                    1
                    - (self.width - crop_min_width) / (crop_max_width - crop_min_width),
                    1
                    - (self.height - crop_min_height)
                    / (crop_max_height - crop_min_height),
                )

                # Apply max crop closeness
                crop_closeness = min(self.crop_closeness, max_crop_closeness)

                if 1 >= crop_closeness >= 0:
                    # Get crop width and height
                    crop_width = (
                        crop_max_width
                        + (crop_min_width - crop_max_width) * crop_closeness
                    )
                    crop_height = (
                        crop_max_height
                        + (crop_min_height - crop_max_height) * crop_closeness
                    )

            fp_x, fp_y = focal_point.centroid
        else:
            # Fall back to positioning in the centre
            fp_x = image_width / 2
            fp_y = image_height / 2
        fp_u = fp_x / image_width
        fp_v = fp_y / image_height

        # Position crop box based on focal point UV
        crop_x = fp_x - (fp_u - 0.5) * crop_width
        crop_y = fp_y - (fp_v - 0.5) * crop_height

        # Convert crop box into rect
        rect = Rect.from_point(crop_x, crop_y, crop_width, crop_height)

        # Make sure the entire focal point is in the crop box
        if focal_point is not None:
            rect = rect.move_to_cover(focal_point)

        # Don't allow the crop box to go over the image boundary
        rect = rect.move_to_clamp(Rect(0, 0, image_width, image_height))

        # Crop!
        pillow = pillow.crop(rect.round())

        # Get scale for resizing
        # The scale should be the same for both the horizontal and
        # vertical axes
        aftercrop_width, aftercrop_height = pillow.size
        scale = self.width / aftercrop_width

        # Only resize if the image is too big
        if scale < 1.0:

            # convert 1 and P images to RGB to improve resize quality
            pillow = to_rgb(pillow)

            # Resize!
            pillow = pillow.resize((self.width, self.height), Image.ANTIALIAS)

        return pillow
