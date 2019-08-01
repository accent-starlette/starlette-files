from .base import Operation


class FormatOperation(Operation):
    def construct(self, fmt):
        self.format = fmt

        if self.format not in ["jpeg", "png"]:
            raise ValueError("Format must be either 'jpeg' or 'png'")

    def run(self, pillow, attachment, env):
        env["output-format"] = self.format
