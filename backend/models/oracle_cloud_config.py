from typing import Literal
from pydantic import BaseModel


class FlexShape(BaseModel):
    shape: Literal["VM.Standard3.Flex"] = "VM.Standard3.Flex"
    ocpus: float
    memory_gb: int


class OCIVars(BaseModel):
    flex_shape: FlexShape
    ocpus: float
    memory_gb: int
    tenancy_ocid: str
    user_ocid: str
    fingerprint: str
    region: str
    compartment_ocid: str
