from dataclasses import dataclass
from enum import Enum


class PIIType(str, Enum):
    CUSTOMER_ID = "customer_id"
    CUSTOMER_NAME = "customer_name"
    PHONE = "phone"
    EMAIL = "email"


@dataclass(frozen=True)
class PIIMatch:
    pii_type: PIIType
    value: str
    start: int
    end: int


@dataclass(frozen=True)
class PIIMapEntry:
    token: str
    pii_type: PIIType
    original_value: str