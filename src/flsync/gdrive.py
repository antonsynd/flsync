from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class UploadClient:
    def __init__(
        self, service_client_json_file_path: Path, destination_folder_id: str
    ) -> None:
        self._destination_folder_id: str = destination_folder_id

        settings: "dict[str, str]" = {
            "client_config_backend": "service",
            "service_config": {
                "client_json_file_path": str(service_client_json_file_path),
            },
        }

        self._gauth = GoogleAuth(settings=settings)
        self._gauth.ServiceAuth()
        self._drive = GoogleDrive(self._gauth)

    def upload(self, file_path: Path):
        print(f"Uploading {file_path}", flush=True)
        file_name = Path(file_path).name
        file_metadata = {
            "title": file_name,
            "parents": [{"id": self._destination_folder_id}],
        }
        file_drive = self._drive.CreateFile(file_metadata)
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
