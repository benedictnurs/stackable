import json
from pathlib import Path
import time

from app.service import DeploymentService
from app.models.payload import Payload
from app.utils.make_directory import make_directory


# cd "/Users/benedictnursalim/Documents/Github Projects/stackable/backend" && python -m app.handler
def run_job(
    private_key_path: Path, public_key_path: Path, payload_path: Path, provider: str
):
    deployment_service = DeploymentService(directory=make_directory())

    with open(payload_path, "r") as f:
        payload_data = json.load(f)

    payload = Payload(**payload_data)

    templates = deployment_service.set_payload(
        payload, private_key_path, public_key_path, provider=provider
    )

    rendered_template = templates[0]
    provider_template = templates[1]

    deployment_service.generate_tf_files(
        rendered_template, private_key_path, file_name="main.tf"
    )
    deployment_service.generate_tf_files(
        provider_template, private_key_path, file_name="provider.tf"
    )

    print("Generated Terraform files successfully!")
    print("Starting deployment process...")
    deployment_service.deploy()
    return deployment_service


if __name__ == "__main__":
    build_job = None
    try:
        build_job = run_job(
            Path("test_files/benedictnursalim@gmail.com-2025-08-15T19_04_27.768Z.pem"),
            Path(
                "test_files/benedictnursalim@gmail.com-2025-08-15T19_04_28.902Z_public.pem"
            ),
            Path("test_files/payload.json"),
            "oracle",
        )
        print(f"Terraform files generated in: {build_job.directory}")
        print("Deployment completed successfully!")

    except Exception as e:
        print(f"Deployment failed with error: {e}")
        if build_job:
            print(f"Files were generated in: {build_job.directory}")

    finally:
        if build_job:
            print("Waiting 10 seconds before cleanup...")
            time.sleep(10)
            build_job.cleanup()
            print("Cleanup completed.")
        else:
            print("No cleanup needed - deployment service was not created.")
