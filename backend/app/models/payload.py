from pydantic import BaseModel
from typing import Optional
from .github_vars import GithubVars
from .cloudflare_vars import CloudflareVars
from .oracle_cloud_config import OCIVars


class Payload(BaseModel):
    """
    Payload model for the stackable service.
    Contains configuration details for Oracle Cloud, Cloudflare, GitHub, and VM settings.

    Attributes:
        oracle_cloud: Optional settings for Oracle Cloud Infrastructure
        cloudflare: Configuration for Cloudflare DNS
        github: GitHub repository information
        instance_name: Name of the VM instance (default: "backend-vm")
        vm_username: Username for VM access (default: "user")
        vm_password: Password for VM access (default: "password")
    """

    oracle_cloud: Optional[OCIVars] = None
    cloudflare: CloudflareVars
    github: GithubVars
    instance_name: str = "backend-vm"
    vm_username: str = "user"
    vm_password: str = "password"
