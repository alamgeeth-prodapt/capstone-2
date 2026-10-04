from detector import PIIDetector
from pseudonymizer import Pseudonymizer
from create2 import PIIRepository


class PIIService:

    def __init__(self):
        self.repository = PIIRepository()
        self.repository.create_table()

        self.detector = PIIDetector()
        self.pseudonymizer = Pseudonymizer(self.repository)

    def sanitize(self, text: str) -> str:

        matches = self.detector.detect(text)

        if not matches:
            return text

        sanitized_text = text

        # Replace from right to left so the original
        # character positions remain valid.
        for match in reversed(matches):

            token = self.pseudonymizer.pseudonymize(
                match.pii_type,
                match.value,
            )

            sanitized_text = (
                sanitized_text[:match.start]
                + token
                + sanitized_text[match.end:]
            )

        return sanitized_text

    def resolve(self, token: str) -> str:

        return self.pseudonymizer.resolve(token)

    def restore(self, text: str) -> str:

        restored_text = text

        mappings = self.repository.get_all_mappings()

        mappings.sort(
            key=lambda mapping: len(mapping[0]),
            reverse=True,
        )

        for token, original_value in mappings:

            restored_text = restored_text.replace(
                token,
                original_value,
            )

        return restored_text