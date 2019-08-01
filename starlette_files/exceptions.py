class ContentTypeValidationError(Exception):
    def __init__(self, content_type=None, valid_content_types=None):

        if content_type is None:
            message = "Content type is not provided. "
        else:
            message = "Content type is not supported %s. " % content_type

        if valid_content_types:
            message += "Valid options are: %s" % ", ".join(valid_content_types)

        super().__init__(message)


class InvalidFilterSpecError(Exception):
    pass


class InvalidImageOperationError(Exception):
    pass


class MaximumAllowedFileLengthError(Exception):
    def __init__(self, max_length: int):
        super().__init__("Cannot store files larger than: %d bytes" % max_length)


class MissingDependencyError(Exception):
    pass
