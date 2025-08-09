import shutil

try:
    from .models.payload import Payload
except ImportError:
    from models.payload import Payload
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


TEMPLATE = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "terraform"),
    autoescape=False,
).get_template("oracle_template.tf.j2")


class DeploymentService:
    def __init__(self, directory: Path):
        self.directory = directory
        self.payload = None

    def set_payload(
        self, payload: Payload, private_key_path: Path, public_key_path: Path
    ) -> str:
        self.payload = payload
        context_data = {}

        if payload.oracle_cloud:
            oracle_data = payload.oracle_cloud.model_dump()
            context_data.update(oracle_data)
            if payload.oracle_cloud.flex_shape:
                context_data["flex"] = payload.oracle_cloud.flex_shape.model_dump()
            else:
                context_data["flex"] = {
                    "shape": "VM.Standard.E2.1.Micro",
                    "ocpus": 1,
                    "memory_gb": 1,
                }

        cloudflare_data = payload.cloudflare.model_dump()
        context_data.update(cloudflare_data)

        github_data = payload.github.model_dump()
        context_data.update(github_data)

        context_data.update(
            {
                "instance_name": payload.instance_name,
                "vm_username": payload.vm_username,
                "vm_password": payload.vm_password,
            }
        )

        context_data.update(
            {
                "pem_path": str(private_key_path),
                "private_pem_path": str(private_key_path),
                "public_pem_path": str(public_key_path),
            }
        )

        rendered_template = TEMPLATE.render(**context_data)
        return rendered_template

    def generate_tf_files(self):
        # Logic to generate Terraform files
        pass

    def deploy(self):
        # Logic to deploy using the provided variables
        pass

    def cleanup(self):
        # Logic to clean up after deployment
        shutil.rmtree(self.directory, ignore_errors=True)
