class ConfigFileNotFound(Exception):
    code = "CONFIG_FILE_NOT_FOUND"

    def __init__(self):
        super().__init__("Config file (config.yml) was not found")


class ConfigFieldIsEmpty(Exception):
    code = "FIELD_IS_EMPTY"

    def __init__(self, field: str):
        self.field = field
        super().__init__(f"{field} is empty")


class FileNotFound(Exception):
    code = "FILE_NOT_FOUND"

    def __init__(self, file_with_path: str):
        self.file_with_path = file_with_path
        super().__init__(f"File not found: {file_with_path}")


class FilePermissionError(Exception):
    code = "FILE_PERMISSION_ERROR"

    def __init__(self, file_with_path: str):
        self.file_with_path = file_with_path
        super().__init__(f"Permission denied for file: {file_with_path}")


class FileExtensionNotSupportedError(Exception):
    code = "FILE_EXTENSION_NOT_SUPPORTED_ERROR"

    def __init__(self, file_with_path: str, extension: str):
        self.file_with_path = file_with_path
        self.extension = extension
        super().__init__(
            f"File extension '{extension}' is not supported: {file_with_path}"
        ) 


class DirectoryNotFound(Exception):
    code = "DIRECTORY_NOT_FOUND"

    def __init__(self, dir_with_path: str):
        self.dir_with_path = dir_with_path
        super().__init__(f"Directory not found: {dir_with_path}")


class DirectoryPermissionError(Exception):
    code = "DIRECTORY_PERMISSION_ERROR"

    def __init__(self, dir_with_path: str):
        self.dir_with_path = dir_with_path
        super().__init__(f"Permission denied for directory: {dir_with_path}")


class OperationalSystemError(Exception):
    code = "OPERATIONAL_SYSTEM_ERROR"

    def __init__(self, message: str = "Operational system error"):
        super().__init__(message)


class TimezoneNotFoundError(Exception):
    code = "TIMEZONE_NOT_FOUND_ERROR"

    def __init__(self, timezone: str):
        super().__init__(f'Timezone "{timezone}" is not supported.')


class MethodNotImplemented(Exception):
    code = "METHOD_NOT_IMPLEMENTED"

    def __init__(self):
        super().__init__("Method not implemented")
