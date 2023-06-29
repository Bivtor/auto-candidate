import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileCreatedHandler(FileSystemEventHandler):
    def __init__(self, directory):
        self.directory = directory
        self.file_created = False

    def on_created(self, event):
        if not event.is_directory:
            self.file_created = True

    def wait_for_file_creation(self):
        observer = Observer()
        observer.schedule(self, self.directory, recursive=False)
        observer.start()

        while not self.file_created:
            time.sleep(1)

        observer.stop()
        observer.join()
