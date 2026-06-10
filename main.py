from exceptions import (
    ConfigFileNotFound,
    ConfigFieldIsEmpty,
    MethodNotImplemented,
)

class Config:
    def __init__(self, config_dict: dict[str, str]):
        self._dir_path: str = self._field_from_dict(config_dict, "dir_path")
    
    @staticmethod
    def _field_from_dict(config_dict: dict[str, str], field_key: str) -> str:
        value = config_dict.get(field_key)

        if value is None or not value.strip():
           raise ConfigFieldIsEmpty(field_key)

        return value 

    @property
    def dir_path(self) -> str:
        return self._dir_path


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
    
    def diff(self):
        raise MethodNotImplemented()

    def add(self):
        raise MethodNotImplemented()

    def stash(self):
        raise MethodNotImplemented()

    def commit(self):
        raise MethodNotImplemented()
