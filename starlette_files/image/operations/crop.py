from .base import Operation


class CropOperation(Operation):
    def construct(self):
        pass

    def run(self, pillow, attachment, env):
        focal_point = attachment.focal_point

        if not focal_point:
            return

        return pillow.crop(focal_point)
