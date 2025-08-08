from pydantic import BaseModel, Field
from typing import Optional


class GithubVars(BaseModel):
    github_token: str
    github_owner: str
    repo_name: str
    docker_image: str
