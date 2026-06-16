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


class FileNotFound(Exception):
    code = "FILE_NOT_FOUND"

    def __init__(self, file_with_path: str):
        self.file_with_path = file_with_path
        self.message = f"File not found: {self.file_with_path}"
        super().__init__(self.message)


class FilePermissionError(Exception):
    code = "FILE_PERMISSION_ERROR"

    def __init__(self, file_with_path: str):
        self.file_with_path = file_with_path
        self.message = f"Permission denied for file: {self.file_with_path}"
        super().__init__(self.message)


class MethodNotImplemented(Exception):
    code = 'METHOD_NOT_IMPLEMENTED'

    def __init__(self):
        self.message = "Method not implemented"
        super().__init__(self.message)
