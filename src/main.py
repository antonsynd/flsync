#!/usr/bin/env python3
import argparse
import logging
import sys

from pathlib import Path
from typing import Optional

from flsync.config import Config
from flsync.worker import start_worker, stop_worker

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

DEFAULT_CONFIG_PATH: Path = Path("~/.flsync_config.json").expanduser()


def main():
    parser: argparse.ArgumentParser = create_arg_parser()
    args: argparse.Namespace = parser.parse_args()
    config_path: Optional[Path] = args.config

    if not config_path:
        config_path = DEFAULT_CONFIG_PATH

    config: Config = Config.read_from_json(input_path=config_path)

    command: str = args.command

    if command == "start":
        socket_port: Optional[int] = args.socket_port

        start(socket_port=socket_port, config=config)
    elif command == "stop":
        socket_port: Optional[int] = args.socket_port

        stop(config=config, socket_port=socket_port)
    elif command == "help":
        parser.print_help()
    else:
        print(f"Unknown command {command}", flush=True, file=sys.stderr)
        sys.exit(1)


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    subparsers: argparse._SubParsersAction = parser.add_subparsers(dest="command")

    start_subparser = subparsers.add_parser("start")
    start_subparser.add_argument("--socket-port", type=int, default=None)

    stop_subparser = subparsers.add_parser("stop")
    stop_subparser.add_argument("--socket-port", type=int, default=None)

    subparsers.add_parser("help")

    return parser


def start(config: Config, socket_port: Optional[int]) -> None:
    socket_port: int = socket_port if socket_port else config.socket_port()

    start_worker(socket_port=socket_port, config=config)


def stop(config: Config, socket_port: Optional[int]) -> None:
    socket_port: int = socket_port if socket_port else config.socket_port()

    stop_worker(socket_port=socket_port, config=config)


if __name__ == "__main__":
    main()
