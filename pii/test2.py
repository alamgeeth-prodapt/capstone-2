from service import PIIService

service = PIIService()

original_text = (
    "Please investigate customer CUST-10002. "
    "The customer name is Alex Romero. "
    "Email: alex@example.com. "
    "Phone: +1 512-555-0198."
)

print("ORIGINAL:")
print(original_text)

# 1. Hide PII
sanitized_text = service.sanitize(original_text)

print("\nSANITIZED:")
print(sanitized_text)

# 2. Simulate something happening with the sanitized text
agent_response = (
    f"I found the account associated with {sanitized_text}"
)

print("\nAGENT RESPONSE:")
print(agent_response)

# 3. Restore PII at the controlled output boundary
restored_text = service.restore(agent_response)

print("\nRESTORED:")
print(restored_text)