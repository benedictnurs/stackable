## Development Setup

### Code Quality Tools
We use [pre-commit](https://pre-commit.com/) hooks to enforce code quality standards and ensure consistent formatting. Our hooks include [Black](https://black.readthedocs.io/), the uncompromising Python code formatter.

### Environment Management
This project uses [pipenv](https://pipenv.pypa.io/) for dependency management. Always activate the virtual environment before working on the project:

```bash
pipenv shell
```

This ensures you're using the correct dependencies and Python version for development.