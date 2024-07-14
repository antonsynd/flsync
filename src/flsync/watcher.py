from pathlib import Path
from typing import Iterable, Optional

from flsync.gdrive import UploadClient

from watchdog.observers import Observer
from watchdog.events import (
    FileMovedEvent,
    FileSystemEvent,
    FileModifiedEvent,
    FileCreatedEvent,
    PatternMatchingEventHandler,
)


class UploadProjectHandler(PatternMatchingEventHandler):
    def __init__(self, upload_client: UploadClient):
        super().__init__(
            patterns=[r"*.flp"], ignore_directories=True, case_sensitive=False
        )

        self._upload_client: UploadClient = upload_client
        self._ignore_folders: Optional[Iterable[Path]] = None

    def ignore_folders(
        self, v: Optional[Iterable[Path]] = None
    ) -> Optional[Iterable[Path]]:
        if v:
            self._ignore_folders: Iterable[Path] = v

        return self._ignore_folders

    def upload_if_not_in_ignore_folders(self, file_path: Path) -> None:
        for ignore_folder in self._ignore_folders:
            if file_path.is_relative_to(ignore_folder):
                return

        self._upload_client.upload(file_path=file_path)

    def on_created(self, event: FileCreatedEvent) -> None:
        self.upload_if_not_in_ignore_folders(file_path=Path(event.src_path))

    def on_modified(self, event: FileModifiedEvent) -> None:
        self.upload_if_not_in_ignore_folders(file_path=Path(event.src_path))

    def on_moved(self, event: FileMovedEvent) -> None:
        self.upload_if_not_in_ignore_folders(file_path=Path(event.src_path))


class Watcher:
    def __init__(
        self,
        watch_folders: Iterable[Path],
        ignore_folders: Iterable[Path],
        upload_handler: UploadProjectHandler,
    ):
        self._watch_folders: Iterable[Path] = watch_folders
        self._ignore_folders: Iterable[Path] = ignore_folders
        self._observer = Observer()
        self._upload_handler: UploadProjectHandler = upload_handler
        self._upload_handler.ignore_folders(ignore_folders)

    def run(self):
        for watch_folder in self._watch_folders:
            self._observer.schedule(self._upload_handler, watch_folder, recursive=True)

        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()
