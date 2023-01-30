import time
import argparse
import json
import os
import sys
from flask import Flask, Response, send_file, send_from_directory
from flask_compress import Compress
from flask_cors import CORS
from typing import Optional
from watchdog.observers import Observer

from s_locus_finder_reporter.parser.SLFDatabaseParser import SLFDatabaseParser
from s_locus_finder_reporter_backend.DatabaseMonitor import DatabaseMonitor
from s_locus_finder_reporter_backend.mapper.SLFDatabaseMapper import SLFDatabaseMapper

app: Flask = Flask(__name__)
Compress(app)
CORS(app)


@app.route('/database', methods=['GET'])
def get_database() -> Response:
    database_mapper = app.config['SLF_DATABASE_MAPPER']
    return Response(json.dumps(database_mapper.get_database()), mimetype='application/json')


@app.route('/files/<path:path>', methods=['GET'])
def get_files(path):
    database_path = app.config['SLF_DATABASE_PATH']

    file_path = os.path.abspath(os.path.join(database_path, *path.split('/')))

    return send_file(file_path, download_name=os.path.basename(file_path), as_attachment=True)


def get_web_file(path: Optional[str]):
    report_dir = app.config['SLF_REPORT_DIR']

    if path is not None and os.path.isfile(os.path.join(report_dir, path)):
        return send_from_directory(report_dir, path)
    else:
        return send_from_directory(report_dir, 'index.html')


def go_to_index():
    return get_web_file(None)


def dir_path(path: str) -> str:
    if os.path.isdir(path):
        return path
    else:
        raise NotADirectoryError(path)


def configure_app(database_path: str, report_directory=None) -> Flask:
    if not os.path.isdir(database_path):
        print(f'Missing database directory ({database_path})')
        sys.exit(1)

    if report_directory:
        if not os.path.isdir(report_directory):
            print(f'Missing report directory ({report_directory})')
            sys.exit(1)

        app.config['SLF_REPORT_DIR'] = report_directory
        app.add_url_rule('/', view_func=go_to_index, methods=['GET'])
        app.add_url_rule('/report/', view_func=go_to_index, methods=['GET'])
        app.add_url_rule('/report/<path:path>', view_func=get_web_file, methods=['GET'])

    database_parser = SLFDatabaseParser()
    database = database_parser.parse(database_path)
    database.relativize_paths(database_path)

    app.config['SLF_DATABASE_PATH'] = database_path
    app.config['SLF_DATABASE_MAPPER'] = SLFDatabaseMapper(database)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backend for the S-Locus Finder Reporter')
    parser.add_argument('--auto-reload', type=bool, default=False, help='Automatic reload of the application')
    parser.add_argument('--database-path', type=dir_path, default="slf-database", help='Path to the SLF database')
    parser.add_argument('--enable-web', type=bool, default=False, help='Enable the web interface')
    parser.add_argument('--watch-db', action='store_true', help='Backend host')
    args = parser.parse_args()
    report_directory = os.path.join(os.getcwd(), 'report') if args.enable_web else None
    app = configure_app(args.database_path, report_directory)

    if args.watch_db:
        event_handler = DatabaseMonitor(app, args.database_path)
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
        app.run(use_reloader=args.auto_reload, debug=args.auto_reload)
