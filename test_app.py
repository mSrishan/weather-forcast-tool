import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

raw_key = os.getenv("GROQ_API_KEY", "")
cleaned_key = raw_key.strip().strip('"').strip("'")

print(f"Key detected: {bool(cleaned_key)}")
print(f"Key starts with 'gsk_': {cleaned_key.startswith('gsk_')}")
print(f"Key length: {len(cleaned_key)}")

client = Groq(api_key=cleaned_key)

try:
    models = client.models.list()
    print("\nModels accessible to this key:")
    for item in models.data:
        print(f" - {item.id}")
except Exception as exc:
    print(f"\nFailed to retrieve models: {exc}")