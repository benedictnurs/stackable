from typing import Optional
from pydantic import BaseModel


class FlexShape(BaseModel):
    shape: Optional[str] = "VM.Standard.E2.1.Micro"
    ocpus: Optional[float] = 1
    memory_gb: Optional[int] = 1


class OCIVars(BaseModel):
    flex_shape: Optional[FlexShape] = None
    tenancy_ocid: str
    user_ocid: str
    fingerprint: str
    region: str
    compartment_ocid: str
