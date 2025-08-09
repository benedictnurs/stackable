from app.service import DeploymentService
from app.models.payload import Payload
from app.models.oracle_cloud_config import OCIVars, FlexShape
from app.models.cloudflare_vars import CloudflareVars
from app.models.github_vars import GithubVars
from pathlib import Path


# cd "/Users/benedictnursalim/Documents/Github Projects/stackable/backend" && python -m app.handler
def run_job():
    deployment_service = DeploymentService(directory=Path("temp_deployment"))

    # Create proper Pydantic payloads
    payload = Payload(
        oracle_cloud=OCIVars(
            tenancy_ocid="ocid1.tenancy.oc1..tenancy",
            user_ocid="ocid1.user.oc1..user",
            fingerprint="aa:bb:cc:dd:ee",
            region="us-phoenix-1",
            compartment_ocid="ocid1.compartment.oc1..compartment",
            flex_shape=FlexShape(shape="VM.Standard3.Flex", ocpus=1, memory_gb=1),
        ),
        cloudflare=CloudflareVars(
            cf_api_token="cf_token_example", cf_account_id="cf_account_example"
        ),
        github=GithubVars(
            github_token="gh_token_example",
            github_owner="testuser",
            repo_name="testrepo",
            docker_image="ghcr.io/testuser/testrepo:latest",
        ),
    )

    private_key_path = Path("id_rsa")
    public_key_path = Path("id_rsa.pub")

    rendered_template = deployment_service.set_payload(
        payload, private_key_path, public_key_path
    )
    print("Rendered template:")
    print(rendered_template)
    deployment_service.generate_tf_files()


if __name__ == "__main__":
    run_job()
