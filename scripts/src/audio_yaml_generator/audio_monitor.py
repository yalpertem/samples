"""File system monitoring functionality for audio files."""

import time
from pathlib import Path

from watchdog.observers import Observer

from .audio_file_handler import AudioFileHandler
from .core import AudioYamlGenerator


class AudioMonitor:
    def __init__(self, directory: Path, generator: AudioYamlGenerator):
        self.directory = directory
        self.generator = generator
        self.observer = Observer()

        def cleanup_callback():
            self.generator.cleanup_orphaned_yaml(self.directory)

        self.handler = AudioFileHandler(generator, cleanup_callback)

    def start_monitoring(self):
        print(f"Monitoring directory: {self.directory}")
        print("Press Ctrl+C to stop...")

        print("Processing existing files...")
        self.generator.batch_process(self.directory)

        print("Watching for new files...")

        self.observer.schedule(self.handler, str(self.directory), recursive=True)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            self.observer.stop()

        self.observer.join()
        print("Monitor stopped.")

    def _stop_monitoring(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
