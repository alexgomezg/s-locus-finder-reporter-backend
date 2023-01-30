import threading
from flask import request, Flask
from waitress import serve

from watchdog.events import FileSystemEventHandler

from s_locus_finder_reporter.parser.SLFDatabaseParser import SLFDatabaseParser
from s_locus_finder_reporter_backend.mapper.SLFDatabaseMapper import SLFDatabaseMapper


class DatabaseMonitor(FileSystemEventHandler):
    database_path: str = ""
    app: Flask = None
    static_server: bool = False
    host: str = ""
    port: str = ""

    def __init__(self, app, database_path, static_server=None, host=None, port=None):
        self.database_path = database_path
        self.app = app
        if static_server:
            self.static_server = static_server
        if host:
            self.host = host
        if port:
            self.port = port
        self.reconfigure_app()

    def on_created(self, event):
        print(event.src_path, event.event_type)
        self.shutdown_server()

    def on_modified(self, event):
        print(event.src_path, event.event_type)
        self.shutdown_server()

    def on_deleted(self, event):
        print(event.src_path, event.event_type)
        self.shutdown_server()

    def reconfigure_app(self):
        t = threading.Thread(target=self.restart_app)
        t.start()

    def shutdown_server(self):
        try:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
        except:
            self.reconfigure_app()

    def restart_app(self):
        database_parser = SLFDatabaseParser()
        database = database_parser.parse(self.database_path)
        database.relativize_paths(self.database_path)
        self.app.config['SLF_DATABASE_MAPPER'] = SLFDatabaseMapper(database)
        if self.static_server:
            serve(self.app, host=self.host, port=self.port)
        else:
            self.app.run()
