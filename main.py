import hashlib

from exceptions import (
    ConfigFileNotFound,
    ConfigFieldIsEmpty,
    FileNotFound,
    FilePermissionError,
    MethodNotImplemented,
)

class Config:
    def __init__(self, config_dict: dict[str, str]):
        self._dir_path: str = self._field_from_dict(config_dict, "dir_path")
        self._hash_algorithm: str = self._field_from_dict(config_dict, "hash_algorithm")
    
    @staticmethod
    def _field_from_dict(config_dict: dict[str, str], field_key: str) -> str:
        value = config_dict.get(field_key)

        if value is None or not value.strip():
           raise ConfigFieldIsEmpty(field_key)

        return value 

    @property
    def dir_path(self) -> str:
        return self._dir_path
    
    @property
    def hash_algorithm(self) -> str:
        return self._hash_algorithm


class TreeEntry:
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
    
    def compute_file_hash(self, file_name: str):
        file_absolute_path = f"{self.get_path()}/{file_name}"

        try:
            with open(file_absolute_path, "rb") as file:
                digest = hashlib.file_digest(file, self.config.hash_algorithm)
        except FileNotFoundError:
            raise FileNotFound(file_absolute_path)
        except PermissionError:
            raise FilePermissionError(file_absolute_path)

        file_hash = digest.hexdigest()
        return file_hash
    
    def add(self):
        raise MethodNotImplemented()

    def diff(self):
        raise MethodNotImplemented()

    def stash(self):
        raise MethodNotImplemented()

    def commit(self):
        raise MethodNotImplemented()
