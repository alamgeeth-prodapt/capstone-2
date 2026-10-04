from pii.create2 import PIIRepository


repository = PIIRepository()

repository.create_table()

repository.save_mapping(
    token="CUSTOMER_TEST123",
    pii_type="customer_id",
    original_value="CUST-10002",
)

print(
    "Token:",
    repository.get_token(
        "customer_id",
        "CUST-10002",
    ),
)

print(
    "Original:",
    repository.get_original_value(
        "CUSTOMER_TEST123",
    ),
)