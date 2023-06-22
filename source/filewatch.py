import asyncio
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NewFileEventHandler(FileSystemEventHandler):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.event = asyncio.Event()

    def on_created(self, event):
        if not event.is_directory and event.src_path.startswith(self.directory):
            self.event.set()


async def await_new_file(directory):
    event_handler = NewFileEventHandler(directory)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    try:
        while True:
            await event_handler.event.wait()
            event_handler.event.clear()
            # Do something with the new file
            print("New file added!")
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


# Example usage
# directory_to_watch = '/path/to/directory'
# asyncio.run(await_new_file(directory_to_watch))
