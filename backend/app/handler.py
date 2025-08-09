from service import DeploymentService
from pathlib import Path


def run_job():
    deployment_service = DeploymentService(directory=Path("path/to/directory"))
    payload = {
        "oci": {
            "tenancy_ocid": "ocid1.tenancy.oc1..tenancy",
            "user_ocid": "ocid1.user.oc1..user",
            "fingerprint": "aa:bb:cc",
            "region": "us-phoenix-1",
        },
        "flex": {"shape": "VM.Standard3.Flex", "ocpus": 1, "memory_in_gbs": 1},
    }
    private_key_path = Path("private_id_rsa.pub")
    public_key_path = Path("id_rsa.pub")

    rendered_template = deployment_service.set_payload(
        payload, private_key_path, public_key_path
    )
    print(rendered_template)
    deployment_service.generate_tf_files()
