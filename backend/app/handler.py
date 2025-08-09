import json
from pathlib import Path

from app.service import DeploymentService
from app.models.payload import Payload
from app.utils.make_directory import make_directory


# cd "/Users/benedictnursalim/Documents/Github Projects/stackable/backend" && python -m app.handler
def run_job(private_key_path: Path, public_key_path: Path, payload_path: Path = None):
    deployment_service = DeploymentService(directory=make_directory())

    if payload_path:
        with open(payload_path, "r") as f:
            payload_data = json.load(f)
        payload = Payload(**payload_data)

    templates = deployment_service.set_payload(
        payload, private_key_path, public_key_path, provider="oracle"
    )

    rendered_template = templates[0]
    provider_template = templates[1]

    deployment_service.generate_tf_files(
        rendered_template, private_key_path, file_name="main.tf"
    )
    deployment_service.generate_tf_files(
        provider_template, private_key_path, file_name="provider.tf"
    )

    return deployment_service


if __name__ == "__main__":
    build_job = run_job(
        Path("test_files/benedictnursalim@gmail.com-2025-06-27T06_04_12.763Z.pem"),
        Path(
            "test_files/benedictnursalim@gmail.com-2025-06-29T21_31_31.231Z_public.pem"
        ),
        Path("test_files/payload.json"),
    )
    print(f"Terraform files generated in: {build_job.directory}")
    # print("Waiting 5 seconds before cleanup...")
    # time.sleep(5)
    # build_job.cleanup()
    # print("Cleanup completed.")
