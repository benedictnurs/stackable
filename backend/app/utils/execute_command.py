import subprocess
import logging
from pathlib import Path


def execute_command(
    command: str, cwd: Path, timeout: int = 600
) -> tuple[str, str, int]:
    """
    Execute a command in the terminal.

    Args:
        command (str): The command to execute
        cwd (Optional[Path]): The current working directory to execute the command in
        timeout (int): Timeout in seconds (default: 600 seconds / 10 minutes)

    Returns:
        tuple[str, str, int]: A tuple containing (stdout, stderr, return_code)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        logging.error(f"Command timed out after {timeout} seconds: {command}")
        return "", f"Command timed out after {timeout} seconds", 1
    except Exception as e:
        logging.error(f"Error executing command '{command}': {str(e)}")
        return "", str(e), 1
