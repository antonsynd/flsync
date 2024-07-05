import json

from pathlib import Path
from typing import Any, Optional


class Config:
    def __init__(
        self, destination_folder_id: str, watch_folders: list[Path], interval: float = 1
    ) -> None:
        self._watch_folders: set[Path] = set(watch_folders)
        self._destination_folder_id: str = destination_folder_id
        self._interval: float = interval

    def watch_folders(self) -> list[Path]:
        return self._watch_folders

    def add_watch_folder(self, watch_folder: Path) -> None:
        self._watch_folders.add(watch_folder)

    def remove_watch_folder(self, watch_folder: Path) -> bool:
        try:
            self._watch_folders.remove(watch_folder)
            return True
        except KeyError:
            return False

    def destination_folder_id(self, v: Optional[str] = None) -> Optional[str]:
        if not v:
            return self._destination_folder_id

        self._destination_folder_id: str = v

    def interval(self, v: Optional[float] = None) -> Optional[float]:
        if not v:
            return self._interval

        self._interval: float = v

    @classmethod
    def read_from_json(cls, input_path: Path) -> "Config":
        with open(input_path, mode="r", encoding="utf-8") as input_file:
            input_json: dict[str, Any] = json.load(input_file)

            destination_folder_id: str = input_json["destintation_folder_id"]
            watch_folders: list[Path] = [Path(x) for x in input_json["watch_folders"]]
            interval: float = float(input_json["interval"])

            return Config(
                destination_folder_id=destination_folder_id,
                watch_folders=watch_folders,
                interval=interval,
            )

    def write_to_json(self, output_path: Path) -> None:
        output_json: dict[str, Any] = {
            "destination_folder_id": self._destination_folder_id,
            "watch_folders": [str(x) for x in self._watch_folders],
            "interval": self._interval,
        }

        with open(output_path, mode="w", encoding="utf-8") as output_file:
            json.dump(output_json, output_file)
