from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def build_template():
    """Load the template dynamically to avoid caching issues."""
    return Environment(
        loader=FileSystemLoader(Path(__file__).parents[2] / "terraform_templates"),
        autoescape=False,
    ).get_template("main.tf.j2")


def build_provider(provider_name: str):
    """Dynamically build provider configuration based on provider name."""
    return Environment(
        loader=FileSystemLoader(
            Path(__file__).parents[2] / "terraform_templates" / "providers"
        ),
        autoescape=False,
    ).get_template(f"{provider_name}_template.tf.j2")
