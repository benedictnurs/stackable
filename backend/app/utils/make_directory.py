from pathlib import Path
import tempfile, uuid


def make_directory() -> Path:
    directory_uuid = uuid().uuid4()
    return Path(tempfile.mkdtemp(prefix=f"tfjob-{directory_uuid}-"))
