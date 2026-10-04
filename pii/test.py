from service import PIIService

service = PIIService()

token = "CUSTOMER_DBB5A8C5"

print("Token:")
print(token)

original = service.resolve(token)

print("\nResolved value:")
print(original)