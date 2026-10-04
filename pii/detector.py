import re

from models import PIIMatch, PIIType


CUSTOMER_ID_PATTERN = re.compile(
    r"\bCUST-\d{4,8}\b",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+1[\s.-]?)?"
    r"(?:\(?\d{3}\)?[\s.-]?)"
    r"\d{3}[\s.-]?\d{4}(?!\d)"
)

# Conservative name detection.
# We only treat a name as PII when it follows an explicit label.
NAME_PATTERN = re.compile(
   r"\b(?:customer\s+name|name)"
    r"\s*(?:is\s+|:\s*|-\s*)"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
)


class PIIDetector:

    def detect(self, text: str) -> list[PIIMatch]:
        matches = []

        matches.extend(self._find_customer_ids(text))
        matches.extend(self._find_emails(text))
        matches.extend(self._find_phones(text))
        matches.extend(self._find_names(text))

        matches.sort(key=lambda match: (match.start, match.end))

        return self._remove_overlaps(matches)

    def _find_customer_ids(self, text: str) -> list[PIIMatch]:
        matches = []

        for match in CUSTOMER_ID_PATTERN.finditer(text):
            matches.append(
                PIIMatch(
                    pii_type=PIIType.CUSTOMER_ID,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                )
            )

        return matches

    def _find_emails(self, text: str) -> list[PIIMatch]:
        matches = []

        for match in EMAIL_PATTERN.finditer(text):
            matches.append(
                PIIMatch(
                    pii_type=PIIType.EMAIL,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                )
            )

        return matches

    def _find_phones(self, text: str) -> list[PIIMatch]:
        matches = []

        for match in PHONE_PATTERN.finditer(text):
            matches.append(
                PIIMatch(
                    pii_type=PIIType.PHONE,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                )
            )

        return matches

    def _find_names(self, text: str) -> list[PIIMatch]:
        matches = []

        for match in NAME_PATTERN.finditer(text):
            # group(1) contains only the actual name,
            # not the "customer" or "name" label.
            name = match.group(1)

            start = match.start(1)
            end = match.end(1)

            matches.append(
                PIIMatch(
                    pii_type=PIIType.CUSTOMER_NAME,
                    value=name,
                    start=start,
                    end=end,
                )
            )

        return matches

    def _remove_overlaps(
        self,
        matches: list[PIIMatch],
    ) -> list[PIIMatch]:

        accepted = []

        for current in matches:
            overlaps = False

            for previous in accepted:
                if current.start < previous.end and current.end > previous.start:
                    overlaps = True
                    break

            if not overlaps:
                accepted.append(current)

        return accepted