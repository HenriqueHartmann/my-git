import csv
import hashlib
import uuid
import zoneinfo

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from exceptions import (
    ConfigFileNotFound,
    ConfigFieldIsEmpty,
    IndexDictNotLoaded,
    FileNotFound,
    FilePermissionError,
    FileExtensionNotSupportedError,
    DirectoryNotFound,
    DirectoryPermissionError,
    OperationalSystemError,
    TimezoneNotFoundError,
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
        self._objects_path = self._get_directory_field(self._field_from_dict(config_dict, "objects_path"))
        self._refs_path = self._get_directory_field(self._field_from_dict(config_dict, "refs_path"))
        self._timezone = self._get_timezone_field(self._field_from_dict(config_dict, "timezone"))
    
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

    @staticmethod
    def _get_timezone_field(value: str) -> zoneinfo.ZoneInfo:
        try:
            return zoneinfo.ZoneInfo(value)
        except zoneinfo.ZoneInfoNotFoundError:
            raise TimezoneNotFoundError(value)

    @property
    def dir_path(self) -> Path:
        return self._dir_path
    
    @property
    def hash_algorithm(self) -> str:
        return self._hash_algorithm
    
    @property
    def index(self) -> Path:
        return self._index

    @property
    def objects_path(self) -> Path:
        return self._objects_path

    @property
    def refs_path(self) -> Path:
        return self._refs_path

    @property
    def timezone(self) -> zoneinfo.ZoneInfo:
        return self._timezone


@dataclass(frozen=True)
class TreeEntry:
    id: str
    sha: str
    index: int
    path: str
    timestamp: str
    size: int

    def get_datetime(self, timezone: zoneinfo.ZoneInfo) -> datetime | None:
        if not self.timestamp:
            return None

        return datetime.fromisoformat(self.timestamp).replace(tzinfo=timezone)


class Client:
    def __init__(self):
        self.config: Config | None = None
        self.index_dict: dict[str, TreeEntry] | None = None

        with open('config.yml') as config_file:
            import yaml
            config_dict = yaml.load(config_file, Loader=yaml.FullLoader)

            if config_dict is None:
                raise ConfigFileNotFound()

            self.config = Config(config_dict)

        self.index_dict = {}

        with open(self.config.index, mode="r", encoding=self.config.INDEX_ENCODING) as file:
            reader = csv.DictReader(file, delimiter=self.config.INDEX_FILE_CSV_DELIMITER)

            for row in reader:
                path = row["path"]

                if row["index"] == "-1":
                    self.index_dict.pop(path, None)
                else:
                    self.index_dict[path] = TreeEntry(**row)

    def _get_path(self):
        return self.config.dir_path
    
    def _get_file_path(self, file_path: str) -> Path:
        absolute_path = Path(self._get_path()) / file_path

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

    def _compute_object_hash(self, object: bytes):
        return hashlib.sha1(object).hexdigest()
    
    def _get_directory(self) -> Path:
        absolute_path = self._get_path()

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

                for row in reader:
                    if row["path"] == file_path:
                        print(row)

        except PermissionError:
            raise FilePermissionError(str(self.config.index))
        except OSError as exc:
            raise OperationalSystemError(str(exc))
    
    def _get_local_now(self):
        return datetime.now(self.config.timezone)
    
    def _get_file_size(self, path: Path):
        return path.stat().st_size
    
    def _index_ends_with_newline(self) -> bool:
        with self.config.index.open("rb") as file:
            try:
                file.seek(-1, 2)
            except OSError:
                return True
            return file.read(1) in (b"\n", b"\r")

    def _write_index(self, entry: TreeEntry) -> None:
        try:
            file_exists = self.config.index.exists()
            is_empty = not file_exists or self.config.index.stat().st_size == 0
            needs_newline = not is_empty and not self._index_ends_with_newline()

            with self.config.index.open(mode="a",encoding=self.config.INDEX_ENCODING,newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "id",
                        "sha",
                        "index",
                        "path",
                        "timestamp",
                        "size",
                    ],
                    delimiter=self.config.INDEX_FILE_CSV_DELIMITER,
                )

                if is_empty:
                    writer.writeheader()
                elif needs_newline:
                    file.write("\r\n")

                writer.writerow(asdict(entry))

        except PermissionError:
            raise FilePermissionError(str(self.config.index))
        except OSError as exc:
            raise OperationalSystemError(str(exc))

    def status(self):
        if self.index_dict is None:
            raise IndexDictNotLoaded()

        root = self._get_directory()

        for file in root.rglob('*'):
            if not file.is_file():
                continue

            relative_path = file.relative_to(root).as_posix()
            index_entry = self.index_dict.get(str(file.resolve()))

            if index_entry is None:
                print(f"file - {relative_path} is Untracked")
            else:
                file_hash = self._compute_file_hash(str(file))

                if file_hash != index_entry.sha:
                    print(f"file - {relative_path} has changed")

    def add(self, path: str):
        file_path = self._get_file_path(path)
        timestamp = self._get_local_now()
        file_size = self._get_file_size(file_path)

        previous_entry = self.index_dict.get(file_path)
        entry_index = int(previous_entry.index) + 1 if previous_entry else 0

        entry_uuid = uuid.uuid4()

        with open(file_path, "rb") as file:
                content_blob = file.read()

        size = len(content_blob)
        object_header = f"blob {size}".encode("utf-8") + b"\x00"
        blob_object = object_header + content_blob
        object_hash = self._compute_object_hash(blob_object)

        object_path = Path(self.config.objects_path)
        object_path_specific = object_path / object_hash[:2]
        object_file_path = object_path_specific / object_hash[2:]

        object_path_specific.mkdir(parents=True, exist_ok=True)

        if not object_file_path.exists():
            with open(object_file_path, "wb") as object_file:
                object_file.write(blob_object)

        entry = TreeEntry(
            id=entry_uuid,
            sha=object_hash,
            index=entry_index,
            path=file_path,
            timestamp=timestamp,
            size=file_size,
        )

        self._write_index(entry)
        self.index_dict[file_path] = entry

        print(f"file - {file_path} added to index")

    def commit(self, message: str):
        # loop through index to identify files that have changed since the last commit
        # recreate the directory structure
        # store root directory hash
        # check for last commit if it exists point that commit as the parent of the new commit else create a new commit with no parent
        # store useful information like name, email, timestamp, and commit message
        # create commit file and generate a unique commit hash
        # update the commit reference with the new commit hash
        raise MethodNotImplemented()

    def diff(self, path: str):
        raise MethodNotImplemented()

    def stash(self):
        raise MethodNotImplemented()
