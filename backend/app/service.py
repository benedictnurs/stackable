import shutil
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
        # Logic to set the payload based on the directory
        self.payload = payload
        context_data = {
            "tenancy_ocid": payload.oci.tenancy_ocid,
            "user_ocid": payload.oci.user_ocid,
            "fingerprint": payload.oci.fingerprint,
            "private_pem_path": str(private_key_path),
            "public_pem_path": str(public_key_path),
            "region": payload.oci.region,
            "flex": payload.flex,
        }
        rendered_template = TEMPLATE.render(**context_data)
        return rendered_template

    def deploy(self):
        # Logic to deploy using the provided variables
        pass

    def cleanup(self):
        # Logic to clean up after deployment
        shutil.rmtree(self.directory, ignore_errors=True)
