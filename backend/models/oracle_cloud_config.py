from pydantic import BaseModel


class OCIVars(BaseModel):
    tenancy_ocid: str
    user_ocid: str
    fingerprint: str
    region: str
    compartment_ocid: str
