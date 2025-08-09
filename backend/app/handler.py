import json
from app.service import DeploymentService
from app.models.payload import Payload
from pathlib import Path


# cd "/Users/benedictnursalim/Documents/Github Projects/stackable/backend" && python -m app.handler
def run_job(private_key_path: Path, public_key_path: Path, payload_path: Path = None):
    deployment_service = DeploymentService(directory=Path("test_files"))

    if payload_path:
        with open(payload_path, "r") as f:
            payload_data = json.load(f)
        payload = Payload(**payload_data)

    rendered_template = deployment_service.set_payload(
        payload, private_key_path, public_key_path
    )
    deployment_service.generate_tf_files(rendered_template, private_key_path)


if __name__ == "__main__":
    run_job(
        Path("test_files/benedictnursalim@gmail.com-2025-06-27T06_04_12.763Z.pem"),
        Path(
            "test_files/benedictnursalim@gmail.com-2025-06-29T21_31_31.231Z_public.pem"
        ),
        Path("test_files/payload.json"),
    )
