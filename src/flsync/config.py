import json

from pathlib import Path
from typing import Any, Optional


class Config:
    def __init__(
        self,
        service_account_client_json_file_path: Path,
        destination_folder_id: str,
        watch_folders: list[Path],
        ignore_folders: list[Path],
        sync_interval_seconds: float = 1,
    ) -> None:
        self._service_account_client_json_file_path: Path = (
            service_account_client_json_file_path
        )
        self._watch_folders: set[Path] = set(watch_folders)
        self._ignore_folders: set[Path] = set(ignore_folders)
        self._destination_folder_id: str = destination_folder_id
        self._sync_interval_seconds: float = sync_interval_seconds

    def watch_folders(self) -> list[Path]:
        return self._watch_folders

    def add_watch_folder(self, watch_folder: Path) -> None:
        self._watch_folders.add(watch_folder)
        self._ignore_folders.discard(watch_folder)

    def remove_watch_folder(self, watch_folder: Path) -> bool:
        try:
            self._watch_folders.remove(watch_folder)
            return True
        except KeyError:
            return False

    def ignore_folders(self) -> list[Path]:
        return self._ignore_folders

    def add_ignore_folder(self, ignore_folder: Path) -> None:
        self._ignore_folders.add(ignore_folder)
        self._watch_folders.discard(ignore_folder)

    def remove_ignore_folder(self, ignore_folder: Path) -> bool:
        try:
            self._ignore_folders.remove(ignore_folder)
            return True
        except KeyError:
            return False

    def service_account_client_json_file_path(
        self, v: Optional[Path] = None
    ) -> Optional[Path]:
        if not v:
            return self._service_account_client_json_file_path

        self._service_account_client_json_file_path: Path = v

    def destination_folder_id(self, v: Optional[str] = None) -> Optional[str]:
        if not v:
            return self._destination_folder_id

        self._destination_folder_id: str = v

    def sync_interval_seconds(self, v: Optional[float] = None) -> Optional[float]:
        if not v:
            return self._sync_interval_seconds

        self._sync_interval_seconds: float = v

    @classmethod
    def read_from_json(cls, input_path: Path) -> "Config":
        with open(input_path, mode="r", encoding="utf-8") as input_file:
            input_json: dict[str, Any] = json.load(input_file)

            destination_folder_id: str = input_json["destination_folder_id"]
            service_account_client_json_file_path: Path = Path(
                input_json["service_account_client_json_file_path"]
            )

            watch_folders: list[Path] = [
                Path(x) for x in input_json.get("watch_folders", [])
            ]
            ignore_folders: list[Path] = [
                Path(x) for x in input_json.get("ignore_folders", [])
            ]
            sync_interval_seconds: float = float(input_json["sync_interval_seconds"])

            return Config(
                service_account_client_json_file_path=service_account_client_json_file_path,
                destination_folder_id=destination_folder_id,
                watch_folders=watch_folders,
                ignore_folders=ignore_folders,
                sync_interval_seconds=sync_interval_seconds,
            )

    def write_to_json(self, output_path: Path) -> None:
        output_json: dict[str, Any] = {
            "service_account_client_json_file_path": str(
                self._service_account_client_json_file_path
            ),
            "destination_folder_id": self._destination_folder_id,
            "watch_folders": [str(x) for x in self._watch_folders],
            "ignore_folders": [str(x) for x in self._ignore_folders],
            "sync_interval_seconds": self._sync_interval_seconds,
        }

        with open(output_path, mode="w", encoding="utf-8") as output_file:
            json.dump(output_json, output_file)
