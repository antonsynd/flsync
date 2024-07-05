import time

from flsync.gdrive import UploadClient
from pathlib import Path

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
            regexes=[r"*.flp"], ignore_directories=True, case_sensitive=False
        )

        self._upload_client: UploadClient = upload_client

    def upload_to_google_drive(self, event: FileSystemEvent) -> None:
        event.src_path

    def on_created(self, event: FileCreatedEvent) -> None:
        self._upload_client.upload(file_path=Path(event.src_path))

    def on_modified(self, event: FileModifiedEvent) -> None:
        self._upload_client.upload(file_path=Path(event.src_path))

    def on_moved(self, event: FileMovedEvent) -> None:
        self._upload_client.upload(file_path=Path(event.dest_path))


class Watcher:
    def __init__(self, watch_folders: list[Path], upload_handler: UploadProjectHandler):
        self._watch_folders: list[Path] = watch_folders
        self._observer = Observer()
        self._upload_handler: UploadProjectHandler = upload_handler

    def run(self):
        for watch_folder in self._watch_folders:
            self._observer.schedule(self._upload_handler, watch_folder, recursive=True)

        self._observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self._observer.stop()

        self._observer.join()
