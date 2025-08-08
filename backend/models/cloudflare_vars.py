from pydantic import BaseModel
from typing import Optional


class CloudflareVars(BaseModel):
    cf_api_token: str
    cf_account_id: str
    cf_zone_id: Optional[str] = ""
    domain: Optional[str] = ""
