import multiprocessing
import socket
import sys
import time

from flsync.config import Config
from flsync.gdrive import UploadClient
from flsync.watcher import Watcher, UploadProjectHandler


def worker_main(socket_port: int, config: Config):
    print(
        f"Starting flsync worker process on port {socket_port}...",
        flush=True,
        file=sys.stdout,
    )

    watcher: Watcher = create_watcher(config=config)
    watcher.run()

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", socket_port))
        server_socket.listen(1)

        listen_for_connections(server_socket=server_socket, socket_port=socket_port)
    finally:
        server_socket.close()
        watcher.stop()

        print(
            f"Terminating flsync worker process on {socket_port}",
            flush=True,
            file=sys.stdout,
        )


def listen_for_connections(server_socket, socket_port: int) -> None:
    while True:
        try:
            conn, addr = server_socket.accept()
            print(f"Received connection from {addr}", flush=True, file=sys.stdout)

            handle_messages(conn=conn, socket_port=socket_port)

            time.sleep(1)
        finally:
            print(f"Closing connection from {addr}...", flush=True, file=sys.stdout)
            conn.close()


def handle_messages(conn, socket_port: int) -> bool:
    while True:
        data = conn.recv(1024).decode()

        # Maybe use protobuf?
        if data == "flsync::quit":
            print(
                f"flsync worker process on {socket_port} received quit signal.",
                flush=True,
                file=sys.stdout,
            )
        else:
            print(
                f"flsync worker process on {socket_port} received unknown signal: {data}",
                flush=True,
                file=sys.stdout,
            )

        time.sleep(1)


def create_watcher(config: Config) -> Watcher:
    upload_client = UploadClient(
        service_client_json_file_path=config.service_account_client_json_file_path(),
        owner_email=config.owner_email(),
        destination_folder_id=config.destination_folder_id(),
    )
    upload_handler = UploadProjectHandler(upload_client=upload_client)

    return Watcher(
        config.watch_folders(),
        ignore_folders=config.ignore_folders(),
        upload_handler=upload_handler,
    )


def start_worker(socket_port: int, config: Config) -> None:
    print(f"Starting worker on {socket_port}...", flush=True, file=sys.stdout)
    p = multiprocessing.Process(
        name=f"flsync_worker_{socket_port}",
        target=worker_main,
        args=(socket_port, config),
        daemon=True,
    )
    p.start()


def send_message_to_worker(socket_port: int, message: str) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", socket_port))
    client_socket.sendall(message.encode())
    client_socket.close()


def stop_worker(socket_port: int, config: Config) -> None:
    print(f"Stopping worker on {socket_port}...", flush=True, file=sys.stdout)
    send_message_to_worker(socket_port=socket_port, message="flsync::quit")
