import argparse
import logging

from flsync.watcher import Watcher, UploadProjectHandler
from flsync.config import Config
from flsync.gdrive import UploadClient

from pathlib import Path
from typing import Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

DEFAULT_CONFIG_PATH: Path = Path("~/.flsync_config.json").expanduser()


def main():
    args: argparse.Namespace = parse_args()
    config_path: Optional[Path] = args.config_path

    if not config_path:
        config_path = DEFAULT_CONFIG_PATH

    config: Config = Config.read_from_json(input_path=config_path)

    upload_client = UploadClient(destination_folder_id=config.destination_folder_id())
    upload_handler = UploadProjectHandler(upload_client=upload_client)

    watcher = Watcher(config.watch_folders(), upload_handler=upload_handler)
    watcher.run()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers: argparse._SubParsersAction = parser.add_subparsers("command")

    run_subparser = subparsers.add_parser("run")

    return parser.parse_args()


if __name__ == "__main__":
    main()
