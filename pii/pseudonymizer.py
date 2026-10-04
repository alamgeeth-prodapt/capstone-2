import hashlib
import secrets

from models import PIIType
from create2 import PIIRepository


class Pseudonymizer:

    def __init__(self, repository: PIIRepository):
        self.repository = repository
        self.secret = secrets.token_hex(32)

    def _generate_token(
        self,
        pii_type: PIIType,
        value: str,
    ) -> str:

        raw_value = f"{pii_type.value}:{value}"

        digest = hashlib.sha256(
            (self.secret + raw_value).encode()
        ).hexdigest()

        prefix = {
            PIIType.CUSTOMER_ID: "CUSTOMER",
            PIIType.CUSTOMER_NAME: "CUSTOMER_NAME",
            PIIType.PHONE: "PHONE",
            PIIType.EMAIL: "EMAIL",
        }[pii_type]

        return f"{prefix}_{digest[:8].upper()}"

    def pseudonymize(
        self,
        pii_type: PIIType,
        value: str,
    ) -> str:

        existing_token = self.repository.get_token(
            pii_type.value,
            value,
        )

        if existing_token:
            return existing_token

        token = self._generate_token(
            pii_type,
            value,
        )

        self.repository.save_mapping(
            token=token,
            pii_type=pii_type.value,
            original_value=value,
        )

        return token

    def resolve(self, token: str) -> str:

        original_value = self.repository.get_original_value(token)

        if original_value is None:
            raise KeyError(
                f"Unknown pseudonym: {token}"
            )

        return original_value