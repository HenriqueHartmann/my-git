import csv
import hashlib
import uuid

from pathlib import Path

from exceptions import (
    ConfigFileNotFound,
    ConfigFieldIsEmpty,
    FileNotFound,
    FilePermissionError,
    FileExtensionNotSupportedError,
    DirectoryNotFound,
    DirectoryPermissionError,
    OperationalSystemError,
    MethodNotImplemented,
)

class Config:
    INDEX_FILE_EXTENSION = ".csv"
    INDEX_FILE_CSV_DELIMITER = ";"
    INDEX_ENCODING = "utf-8"


    def __init__(self, config_dict: dict[str, str]):
        self._dir_path = self._get_directory_field(self._field_from_dict(config_dict, "dir_path"))
        self._hash_algorithm = self._field_from_dict(config_dict,"hash_algorithm",)
        self._index = self._get_index_field(self._field_from_dict(config_dict, "index"))
    
    @staticmethod
    def _field_from_dict(config_dict: dict[str, str], field_key: str) -> str:
        value = config_dict.get(field_key)

        if value is None or not value.strip():
            raise ConfigFieldIsEmpty(field_key)

        return value

    @classmethod
    def _get_directory_field(cls, value: str) -> Path:
        return Path(value)

    @classmethod
    def _get_index_field(cls, value: str) -> Path:
        path = Path(value)

        try:
            if not path.is_file():
                raise FileNotFound(str(path))

            if path.suffix.lower() != cls.INDEX_FILE_EXTENSION:
                raise FileExtensionNotSupportedError(
                    str(path),
                    cls.INDEX_FILE_EXTENSION,
                )

            return path

        except PermissionError:
            raise FilePermissionError(str(path))
        except OSError as exc:
            raise OperationalSystemError(str(exc))

    @property
    def dir_path(self) -> Path:
        return self._dir_path
    
    @property
    def hash_algorithm(self) -> str:
        return self._hash_algorithm
    
    @property
    def index(self) -> Path:
        return self._index


class TreeEntry:
    id: str
    sha: str
    index: int
    path: str


class Client:
    def __init__(self):
        self.config: Config | None = None

        with open('config.yml') as config_file:
            import yaml
            config_dict = yaml.load(config_file, Loader=yaml.FullLoader)

            if config_dict is None:
                raise ConfigFileNotFound()

            self.config = Config(config_dict)
        
    def get_path(self):
        return self.config.dir_path
    
    def _get_file_path(self, file_path: str) -> Path:
        absolute_path = Path(self.get_path()) / file_path

        try:
            if not absolute_path.is_file():
                raise FileNotFound(str(absolute_path))

            return absolute_path

        except PermissionError:
            raise FilePermissionError(str(absolute_path))
        except OSError as exc:
            raise OperationalSystemError(str(exc))
    
    def _compute_file_hash(self, file_path: str):
        path = self._get_file_path(file_path)

        with path.open("rb") as file:
            digest = hashlib.file_digest(file, self.config.hash_algorithm)

        return digest.hexdigest()
    
    def _get_directory(self) -> Path:
        absolute_path = self.get_path()

        try:
            path = Path(absolute_path)

            if not path.is_dir():
                raise DirectoryNotFound(absolute_path)

            return path

        except PermissionError:
            raise DirectoryPermissionError(absolute_path)
        except OSError as exc:
            raise OperationalSystemError(str(exc))
    
    def _filter_index(self, file_path: str):
        try:
            with open(self.config.index, mode="r", encoding=self.config.INDEX_ENCODING) as file:
                reader = csv.DictReader(file, delimiter=self.config.INDEX_FILE_CSV_DELIMITER)
                if not reader.fieldnames:
                    return False
                
                print("CSV LINHAS")
                for row in reader:
                    print(row["path"])
                    if row["path"] == file_path:
                        print(row)

        except PermissionError:
            raise FilePermissionError(str(self.config.index))
        except OSError as exc:
            raise OperationalSystemError(str(exc))

    def status(self):
        path = self._get_directory()

        print("\nARQUIVOS:\n")
        for file in path.rglob('*'):
            if file.is_file():
                print(f"file - {file.name}")

    def add(self, path):
        # SEARCH FOR SIZE (BYTE) AND TIMESTAMP
        change_uuid = uuid.uuid7()
        file_hash = self.compute_file_hash(self, file_path)

        raise MethodNotImplemented()

    def diff(self):
        raise MethodNotImplemented()

    def stash(self):
        raise MethodNotImplemented()

    def commit(self):
        raise MethodNotImplemented()
