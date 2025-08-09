from pathlib import Path


def decode_file(file_path: Path) -> str:
    try:
        return file_path.read_text().strip()
    except FileNotFoundError:
        return f"# SSH key content from {file_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to read key content from {file_path}: {e}")


def read_file(file_path: Path) -> str:
    try:
        return file_path.read_text().strip()
    except FileNotFoundError:
        return f"# SSH key content from {file_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to read key content from {file_path}: {e}")
