"""File system monitoring functionality for audio files."""

import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler

from .core import AudioYamlGenerator


class AudioFileHandler(FileSystemEventHandler):
    def __init__(
        self, generator: AudioYamlGenerator, cleanup_callback: Optional[Callable] = None
    ):
        self.generator = generator
        self.cleanup_callback = cleanup_callback
        super().__init__()

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            file_path = Path(str(event.src_path))
            if self.generator.is_audio_file(file_path):
                try:
                    rel_file_path = file_path.relative_to(self.generator.base_dir)
                except ValueError:
                    rel_file_path = file_path
                print(f"New audio file detected: {rel_file_path}")
                time.sleep(0.2)
                self.generator.process_file(file_path)

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory:
            dest_path = Path(str(event.dest_path))
            if self.generator.is_audio_file(dest_path):
                try:
                    rel_src_path = Path(str(event.src_path)).relative_to(
                        self.generator.base_dir
                    )
                except ValueError:
                    rel_src_path = Path(str(event.src_path))
                try:
                    rel_dest_path = dest_path.relative_to(self.generator.base_dir)
                except ValueError:
                    rel_dest_path = dest_path
                print(f"Audio file moved/renamed: {rel_src_path} -> {rel_dest_path}")
                time.sleep(0.2)
                self.generator.process_file(dest_path)

            if self.cleanup_callback:
                print("File moved/renamed, running cleanup...")
                self.cleanup_callback()

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            if self.cleanup_callback:
                try:
                    rel_file_path = Path(str(event.src_path)).relative_to(
                        self.generator.base_dir
                    )
                except ValueError:
                    rel_file_path = Path(str(event.src_path))
                print(f"File deleted: {rel_file_path}, running cleanup...")
                self.cleanup_callback()
