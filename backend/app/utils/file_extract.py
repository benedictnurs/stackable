from pathlib import Path
import subprocess
import os


def decode_file(file_path: Path) -> str:
    """
    Generate public key from private key file using ssh-keygen
    """
    try:
        # First, set proper permissions on the private key file
        os.chmod(file_path, 0o600)

        # Generate public key from private key using ssh-keygen
        result = subprocess.run(
            ["ssh-keygen", "-y", "-f", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except FileNotFoundError:
        return f"# SSH key content from {file_path}"
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to generate public key from {file_path}: {e.stderr}"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to process key file {file_path}: {e}")


def read_file(file_path: Path) -> str:
    try:
        return file_path.read_text().strip()
    except FileNotFoundError:
        return f"# SSH key content from {file_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to read key content from {file_path}: {e}")
