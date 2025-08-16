from pathlib import Path
import uuid


def make_directory() -> Path:
    directory_uuid = uuid.uuid4()
    parent_dir = Path(__file__).parents[2]
    temp_dir = parent_dir / "temp_templates" / f"tfjob-{directory_uuid}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir
