from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class UploadClient:
    def __init__(self, destination_folder_id: str) -> None:
        self._destination_folder_id: str = destination_folder_id

        self._gauth = GoogleAuth()
        self._gauth.LocalWebserverAuth()
        self._drive = GoogleDrive(self._gauth)

    def upload(self, file_path: Path):
        file_name = Path(file_path).name
        file_metadata = {
            "title": file_name,
            "parents": [{"id": self._destination_folder_id}],
        }
        file_drive = self._drive.CreateFile(file_metadata)
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
