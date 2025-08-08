from pydantic import BaseModel


class GithubVars(BaseModel):
    github_token: str
    github_owner: str
    repo_name: str
    docker_image: str
