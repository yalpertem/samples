"""Core functionality for audio YAML metadata generation."""

from pathlib import Path
from typing import List, Optional

import yaml

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".flac",
    ".aiff",
    ".aif",
    ".m4a",
    ".ogg",
    ".wma",
}


class AudioYamlGenerator:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = Path(base_dir).resolve() if base_dir else Path.cwd().resolve()

    def is_audio_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS

    def cleanup_orphaned_yaml(self, directory: Optional[Path] = None) -> int:
        if directory is None:
            directory = self.base_dir

        print(f"Cleaning up orphaned YAML files in: {directory}")

        removed_count = 0

        for yaml_file in directory.rglob("*.yml"):
            base_path = yaml_file.with_suffix("")
            audio_found = False

            for ext in SUPPORTED_AUDIO_EXTENSIONS:
                if (base_path.with_suffix(ext)).exists() or (
                    base_path.with_suffix(ext.upper())
                ).exists():
                    audio_found = True
                    break

            if not audio_found:
                try:
                    rel_yaml_path = yaml_file.relative_to(self.base_dir)
                except ValueError:
                    rel_yaml_path = yaml_file
                print(f"Removing orphaned YAML: {rel_yaml_path}")
                yaml_file.unlink()
                removed_count += 1

        print(f"Cleanup complete. Removed {removed_count} orphaned files.")
        return removed_count

    def process_file(self, file_path: Path) -> bool:
        if self.is_audio_file(file_path) and file_path.exists():
            return self._create_yaml(file_path)
        return False

    def batch_process(self, directory: Optional[Path] = None) -> int:
        if directory is None:
            directory = self.base_dir

        print(f"Processing audio files in: {directory}")

        created_count = 0

        for ext in SUPPORTED_AUDIO_EXTENSIONS:
            pattern = f"**/*{ext}"
            for audio_file in directory.glob(pattern):
                if self._create_yaml(audio_file):
                    created_count += 1

            # Also check uppercase extensions
            pattern = f"**/*{ext.upper()}"
            for audio_file in directory.glob(pattern):
                if self._create_yaml(audio_file):
                    created_count += 1

        print(f"Batch processing complete. Created {created_count} YAML files.")
        return created_count

    def _get_yaml_path(self, audio_path: Path) -> Path:
        return audio_path.with_suffix(".yml")

    def _create_yaml(self, audio_file: Path) -> bool:
        yaml_file = self._get_yaml_path(audio_file)

        if yaml_file.exists():
            try:
                rel_yaml_path = yaml_file.relative_to(self.base_dir)
            except ValueError:
                rel_yaml_path = yaml_file
            print(f"YAML file already exists: {rel_yaml_path}")
            return False

        # Ensure audio_file is absolute and resolve it
        audio_file_resolved = audio_file.resolve()

        try:
            rel_path = audio_file_resolved.relative_to(self.base_dir)
        except ValueError:
            # If we can't make it relative, fall back to the filename
            rel_path = audio_file.name

        instrument = (
            audio_file.parent.name if audio_file.parent.name != "." else "unknown"
        )

        yaml_content = {
            "path": str(rel_path),
            "tags": {"instrument": instrument, "genre": "", "mood": ""},
            "bpm": 0,
            "key": None,
            "length_beats": "",
            "notes": "",
        }

        with open(yaml_file, "w") as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)

        try:
            rel_yaml_path = yaml_file.relative_to(self.base_dir)
        except ValueError:
            rel_yaml_path = yaml_file

        print(f"Created YAML file: {rel_yaml_path} (instrument: {instrument})")
        return True

    def _find_audio_files(self, directory: Optional[Path] = None) -> List[Path]:
        if directory is None:
            directory = self.base_dir

        audio_files = []

        for ext in SUPPORTED_AUDIO_EXTENSIONS:
            for pattern in [f"**/*{ext}", f"**/*{ext.upper()}"]:
                audio_files.extend(directory.glob(pattern))

        return sorted(set(audio_files))
