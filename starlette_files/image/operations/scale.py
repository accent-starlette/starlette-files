from .base import Operation


class ScaleOperation(Operation):
    def construct(self, percent):
        self.percent = float(percent)

    def run(self, pillow, attachment, env):
        image_width, image_height = pillow.size

        scale = self.percent / 100
        width = int(image_width * scale)
        height = int(image_height * scale)

        return pillow.resize((width, height))
