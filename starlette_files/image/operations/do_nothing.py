from .base import Operation


class DoNothingOperation(Operation):
    def construct(self):
        pass

    def run(self, pillow, attachment, env):
        pass
