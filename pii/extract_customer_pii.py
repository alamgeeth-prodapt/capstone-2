from create2 import PIIRepository
from pseudonymizer import Pseudonymizer
from models import PIIType
import sqlite3
from pathlib import Path


# Project root: D:\Project_2
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Operational database
TELECOM_DB = PROJECT_ROOT / "telecom_ops.db"


def ingest_customer_pii():

    # Connect to our persistent PII mapping database
    repository = PIIRepository()
    repository.create_table()

    # Create pseudonymizer
    pseudonymizer = Pseudonymizer(repository)

    # Connect to the operational telecom database
    connection = sqlite3.connect(TELECOM_DB)

    rows = connection.execute("""
        SELECT customer_id, customer_name
        FROM customer_subscriptions
        ORDER BY customer_id
    """).fetchall()

    connection.close()

    # Create/reuse pseudonyms
    for customer_id, customer_name in rows:

        pseudonymizer.pseudonymize(
            pii_type=PIIType.CUSTOMER_ID,
            value=customer_id,
        )

        pseudonymizer.pseudonymize(
            pii_type=PIIType.CUSTOMER_NAME,
            value=customer_name,
        )

    print(f"Customers processed: {len(rows)}")
    print(f"PII mappings stored: {len(rows) * 2}")


if __name__ == "__main__":
    ingest_customer_pii()