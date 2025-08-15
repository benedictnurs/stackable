from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def build_template(provider_name: str = None) -> Environment:
    """Builds the template."""
    if provider_name:
        template = f"providers/{provider_name}_template.tf.j2"
    else:
        template = "main.tf.j2"
    return Environment(
        loader=FileSystemLoader(Path(__file__).parents[2] / "terraform_templates"),
        autoescape=False,
    ).get_template(template)
