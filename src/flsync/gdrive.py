from pathlib import Path
from typing import Mapping, Optional

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class UploadClient:
    def __init__(
        self,
        service_client_json_file_path: Path,
        owner_email: str,
        destination_folder_id: str,
    ) -> None:
        self._destination_folder_id: str = destination_folder_id

        settings: Mapping[str, str] = {
            "client_config_backend": "service",
            "service_config": {
                "client_json_file_path": str(service_client_json_file_path),
            },
        }

        self._gauth = GoogleAuth(settings=settings)
        self._gauth.ServiceAuth()
        self._drive = GoogleDrive(self._gauth)

    def try_get_file_id_for_file_name(self, file_name: str) -> Optional[str]:
        file_list = self._drive.ListFile(
            {"q": f"title = '{file_name}' and trashed=false"}
        ).GetList()

        if file_list:
            file = file_list[0]
            return file["id"]
        else:
            return None

    def upload(self, file_path: Path):
        print(f"Uploading {file_path}", flush=True)
        file_name = Path(file_path).name
        file_metadata = {
            "title": file_name,
            "parents": [{"id": self._destination_folder_id}],
        }

        file_id: Optional[str] = self.try_get_file_id_for_file_name(file_name=file_name)

        if file_id:
            file_metadata["id"] = file_id

        file_drive = self._drive.CreateFile(file_metadata)
        file_drive.SetContentFile(file_path)
        file_drive.Upload()
        file_drive.FetchMetadata(fields="id")
