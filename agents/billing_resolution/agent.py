import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is not configured.")


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "telecom_ops.db"


def lookup_billing_account(customer_id: str) -> dict:
    """
    Look up the customer's billing account information.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        account = connection.execute(
            """
            SELECT
                customer_id,
                customer_name,
                account_type,
                current_balance,
                currency,
                service_region,
                city,
                state,
                billing_cycle,
                auto_pay_enabled,
                account_status,
                last_updated
            FROM billing_accounts
            WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()

        if account is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": f"Billing account for {customer_id} was not found.",
            }

        return {
            "success": True,
            "account": dict(account),
        }

    finally:
        connection.close()


def check_duplicate_charges(customer_id: str) -> dict:
    """
    Check billing charges for duplicate charges associated
    with the customer.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        charges = connection.execute(
            """
            SELECT
                charge_id,
                customer_id,
                description,
                amount,
                billing_period,
                charge_date,
                charge_type,
                is_duplicate_flag,
                invoice_status
            FROM billing_charges
            WHERE customer_id = ?
            ORDER BY charge_date DESC
            """,
            (customer_id,),
        ).fetchall()

        if not charges:
            return {
                "success": True,
                "customer_id": customer_id,
                "total_charges": 0,
                "duplicate_count": 0,
                "duplicate_charges": [],
                "message": "No billing charges were found for this customer.",
            }

        duplicate_charges = [
            dict(charge)
            for charge in charges
            if charge["is_duplicate_flag"] == 1
        ]

        return {
            "success": True,
            "customer_id": customer_id,
            "total_charges": len(charges),
            "duplicate_count": len(duplicate_charges),
            "duplicate_charges": duplicate_charges,
        }

    finally:
        connection.close()

def apply_billing_credit(
    customer_id: str,
    amount: float,
    reason: str,
    related_charge_id: str | None = None,
) -> dict:
    """
    Apply a billing credit according to the project policy.

    Credits <= $50 are applied immediately and reduce the
    customer's current balance.

    Credits > $50 are recorded as PENDING_APPROVAL and do not
    change the customer's current balance.
    """

    if amount <= 0:
        return {
            "success": False,
            "customer_id": customer_id,
            "error": "Credit amount must be greater than zero.",
        }

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        # Verify the billing account exists.
        account = connection.execute(
            """
            SELECT customer_id, current_balance, currency
            FROM billing_accounts
            WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()

        if account is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": f"Billing account for {customer_id} was not found.",
            }

        if amount <= 50:
            status = "APPLIED"
        else:
            status = "PENDING_APPROVAL"

        connection.execute("BEGIN")

        cursor = connection.execute(
            """
            INSERT INTO billing_credits (
                customer_id,
                amount,
                reason,
                status,
                related_charge_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                amount,
                reason,
                status,
                related_charge_id,
            ),
        )

        credit_id = cursor.lastrowid

        new_balance = account["current_balance"]

        if status == "APPLIED":
            connection.execute(
                """
                UPDATE billing_accounts
                SET current_balance = current_balance - ?
                WHERE customer_id = ?
                """,
                (amount, customer_id),
            )

            new_balance = account["current_balance"] - amount

        connection.commit()

        return {
            "success": True,
            "customer_id": customer_id,
            "credit_id": credit_id,
            "amount": amount,
            "reason": reason,
            "status": status,
            "related_charge_id": related_charge_id,
            "previous_balance": account["current_balance"],
            "current_balance": new_balance,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

# if __name__ == "__main__":
#     print("=== BILLING ACCOUNT LOOKUP ===")
#     print(lookup_billing_account("CUST-10002"))

#     print("\n=== DUPLICATE CHARGE CHECK ===")
#     print(check_duplicate_charges("CUST-10002"))

#     print("\n=== APPLY $25 CREDIT ===")
#     print(
#         apply_billing_credit(
#             customer_id="CUST-10002",
#             amount=25.00,
#             reason="Duplicate charge correction",
#             related_charge_id="CHG-50022",
#         )
#     )

root_agent = Agent(
    name="billing_resolution_agent",
    model="gemini-3.8-flash",
    description=(
        "A billing resolution specialist that investigates "
        "customer billing accounts, duplicate charges, and "
        "billing credit requests."
    ),
    instruction="""
You are a Billing Resolution specialist.

Your job is to investigate and resolve telecom billing issues
using the SQL-backed tools provided to you.

Available tools:

1. lookup_billing_account
   - Use this to retrieve the customer's billing account,
     balance, account status, billing cycle, and related details.

2. check_duplicate_charges
   - Use this when investigating duplicate billing charges.
   - Check the SQL results rather than assuming a charge is a duplicate.

3. apply_billing_credit
   - Use this when a billing credit needs to be applied.
   - Credits of $50 or less are applied immediately.
   - Credits above $50 require approval and are recorded as
     PENDING_APPROVAL.
   - Do not claim that a pending credit has been applied.

Rules:
- Always use the SQL tools to obtain billing information.
- Do not invent customer accounts, charges, balances, or credits.
- If a customer does not exist, clearly report that.
- When investigating duplicate charges, use the duplicate flag
  returned by the database.
- Clearly distinguish between APPLIED and PENDING_APPROVAL credits.
- Give concise, operationally useful conclusions.
""",
    tools=[
        lookup_billing_account,
        check_duplicate_charges,
        apply_billing_credit,
    ],
)