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
        content = file_path.read_text().strip()

        if (
            "-----BEGIN PRIVATE KEY-----" in content
            and "-----END PRIVATE KEY-----" in content
        ):
            end_marker = "-----END PRIVATE KEY-----"
            end_index = content.find(end_marker) + len(end_marker)
            content = content[:end_index]

        return content
    except FileNotFoundError:
        return f"# SSH key content from {file_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to read key content from {file_path}: {e}")
