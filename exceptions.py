class ConfigFileNotFound(Exception):
    code = "CONFIG_FILE_NOT_FOUND"

    def __init__(self):
        self.message = "Config file (config.yml) was not found"
        super().__init__(self.message)


class ConfigFieldIsEmpty(Exception):
    code = "FIELD_IS_EMPTY"

    def __init__(self, field: str):
        self.field = field
        self.message = f"{field} is empty"

        super().__init__(self.message)


class MethodNotImplemented(Exception):
    code = 'METHOD_NOT_IMPLEMENTED'

    def __init__(self):
        self.message = "Method not implemented"
