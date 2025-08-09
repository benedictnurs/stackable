import shutil
from .models.payload import Payload
from pathlib import Path
from .utils.file_extraction import decode_file, read_file
from .utils.build_terraform_templates import build_template, build_provider


class DeploymentService:
    def __init__(self, directory: Path):
        self.directory = directory
        self.payload = None

    def set_payload(
        self,
        payload: Payload,
        private_key_path: Path,
        public_key_path: Path,
        provider: str = None,
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
                "ssh_public_key": decode_file(private_key_path),
                "ssh_private_key": read_file(private_key_path),
            }
        )

        rendered_template = build_template().render(**context_data)
        provider_template = build_provider(provider).render(**context_data)

        return rendered_template, provider_template

    def generate_tf_files(
        self, template_content: str, private_key_path: Path, file_name: str
    ) -> Path:
        """Generate Terraform files in the deployment directory."""
        if not self.payload:
            raise ValueError(
                "Payload must be set before generating Terraform files. Call set_payload() first."
            )

        self.directory.mkdir(parents=True, exist_ok=True)
        deploy_private_key = self.directory / "id_rsa"
        deploy_public_key = self.directory / "id_rsa.pub"

        # Generate private key content and write it
        private_key_content = read_file(private_key_path)
        with open(deploy_private_key, "w") as f:
            f.write(private_key_content)

        # Generate public key content and write it
        public_key_content = decode_file(private_key_path)
        with open(deploy_public_key, "w") as f:
            f.write(public_key_content)

        # Set proper permissions on the private key
        deploy_private_key.chmod(0o600)
        deploy_public_key.chmod(0o644)

        # Generate the main Terraform configuration file
        tf_file_path = self.directory / file_name

        with open(tf_file_path, "w") as f:
            f.write(str(template_content))

        return tf_file_path

    def deploy(self):
        # Logic to deploy using the provided variables
        pass

    def cleanup(self):
        # Logic to clean up after deployment
        shutil.rmtree(self.directory, ignore_errors=True)
