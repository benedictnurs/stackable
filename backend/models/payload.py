from pydantic import BaseModel
from typing import Optional
from .github_vars import GithubVars
from .cloudflare_vars import CloudflareVars
from .oracle_cloud_config import OCIVars


class Payload(BaseModel):
    oracle_cloud: Optional[OCIVars] = None
    cloudflare: CloudflareVars
    github: GithubVars
    instance_name: str = "backend-vm"
    vm_username: str = "user"
    vm_password: str = "password"
