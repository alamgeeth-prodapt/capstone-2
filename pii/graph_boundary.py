from pathlib import Path
import sys

PII_DIR = Path(__file__).resolve().parent

if str(PII_DIR) not in sys.path:
    sys.path.insert(0, str(PII_DIR))

from detector import PIIDetector
from pseudonymizer import Pseudonymizer
from create2 import PIIRepository


class GraphPIIBoundary:
    def __init__(self):
        self.repository = PIIRepository()
        self.repository.create_table()

        self.detector = PIIDetector()
        self.pseudonymizer = Pseudonymizer(self.repository)

    def sanitize(self, text: str) -> str:
        matches = self.detector.detect(text)

        sanitized = text

        for match in reversed(matches):
            token = self.pseudonymizer.pseudonymize(
                pii_type=match.pii_type,
                value=match.value,
            )

            sanitized = (
                sanitized[:match.start]
                + token
                + sanitized[match.end:]
            )

        return sanitized

    def restore(self, text: str) -> str:
        import re

        token_pattern = re.compile(
            r"\b(?:CUSTOMER|CUSTOMER_NAME|PHONE|EMAIL)_[A-F0-9]{8}\b"
        )

        def replace(match):
            token = match.group(0)

            try:
                return self.pseudonymizer.resolve(token)
            except KeyError:
                return token

        return token_pattern.sub(replace, text)