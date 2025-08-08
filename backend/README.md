## Development Setup

### Code Quality Tools
We use [pre-commit](https://pre-commit.com/) hooks to enforce code quality standards and ensure consistent formatting. Our hooks include [Black](https://black.readthedocs.io/), the uncompromising Python code formatter.

### Environment Management
This project uses [pipenv](https://pipenv.pypa.io/) for dependency management. Always activate the virtual environment before working on the project:
To set up your environment correctly, first identify your virtual environment path:

```bash
pipenv --venv
```

Then configure your IDE/editor to use this path for the Python interpreter. This ensures your editor has access to all installed packages.

Once configured, activate the environment with:
```bash
pipenv shell
```

This ensures you're using the correct dependencies and Python version for development.