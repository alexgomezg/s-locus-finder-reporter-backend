from io import BytesIO

import time

import tarfile
import argparse
import os
import requests
import shutil
import tempfile
from waitress import serve
from watchdog.observers import Observer

from s_locus_finder_reporter_backend.DatabaseMonitor import DatabaseMonitor
from s_locus_finder_reporter_backend.app import dir_path, configure_app


def serve_app():
    parser = argparse.ArgumentParser(description='Backend for the S-Locus Finder Reporter')
    parser.add_argument('--database-path', type=dir_path, default='slf-database', help='path to the SLF database')
    parser.add_argument('--port', type=str, default='5000', help='backend port')
    parser.add_argument('--host', type=str, default='localhost', help='backend host')
    parser.add_argument('--watch-db', action='store_true', help='watch the database directory for updates')
    parser.add_argument('--with-web', action='store_true', help='serve also the frontend')
    parser.add_argument('--web-path', type=dir_path, help='frontend directory')

    args = parser.parse_args()

    if args.with_web:
        if args.web_path:
            app = configure_app(args.database_path, report_directory=args.web_path)
        else:
            origin_url = 'https://static.sing-group.org/slfinder/s-locus-finder-reporter-frontend.1.0.0-alpha.23.tar.gz'
            tmp_dir = tempfile.mkdtemp()
            download_frontend(origin_url, tmp_dir)
            for file in os.listdir(tmp_dir):
                if file.startswith('main.') and file.endswith('.js'):
                    with open(os.path.join(tmp_dir, file), 'r') as main_file:
                        data = main_file.read()
                        data = data.replace('SLF_BACKEND_HOST', args.host)
                        data = data.replace('SLF_BACKEND_PORT', args.port)

                    with open(os.path.join(tmp_dir, file), 'w') as main_file:
                        main_file.write(data)
            app = configure_app(args.database_path, report_directory=tmp_dir)
    else:
        app = configure_app(args.database_path)

    if args.watch_db:
        event_handler = DatabaseMonitor(app, args.database_path, static_server=True, host=args.host, port=args.port)
        time.sleep(3)
        observer = Observer()
        observer.schedule(event_handler, args.database_path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()
    else:
        serve(app, host=args.host, port=args.port)

    try:
        shutil.rmtree(tmp_dir)
    except OSError as e:
        print(f'Error deleting temporal directory {dir_path}: {e.strerror}')


def download_frontend(url: str, dest_dir: str):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    response = requests.get(url, allow_redirects=True)
    if response.ok:
        with tarfile.open(fileobj=BytesIO(response.content)) as file:
            file.extractall(dest_dir)
    else:
        print('Download failed: status code {}\n{}'.format(response.status_code, response.text))


if __name__ == '__main__':
    serve_app()
