# pip install stellar-sdk requests
from stellar_sdk import xdr as stellar_xdr
import base64
import json
import requests

# === 1. Fetch XDR from Pi Network API ===
hurl = "https://api.testnet.minepi.com/liquidity_pools/1838e29e36a35b82f1dfbe9d1d00471616eb5a08fdf14b2899b159061d5212b4"
url = f"{hurl}/transactions"
resp = requests.get(url).json()
result_meta_xdr = resp['_embedded']['records'][0]['result_meta_xdr']

# === 2. Decode Base64 XDR to bytes ===
xdr_bytes = base64.b64decode(result_meta_xdr)
print(xdr_bytes)

# === 3. Parse as TransactionMeta ===
tx_meta = stellar_xdr.transaction_meta.TransactionMeta.from_xdr_bytes(xdr_bytes)
print(f"type(tx_meta): {type(tx_meta)}")
print(f"tx_meta: {tx_meta}")
exit()

# === 4. Recursive converter for nested XDR objects ===
def xdr_to_dict(obj):
    if obj is None:
        return None
    elif isinstance(obj, list):
        return [xdr_to_dict(x) for x in obj]
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode()
    elif hasattr(obj, "__dataclass_fields__"):
        return {k: xdr_to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    elif hasattr(obj, "__dict__"):
        return {k: xdr_to_dict(v) for k, v in obj.__dict__.items()}
    else:
        return str(obj)

# === 5. Try to get v4 data from __dict__ ===
tx_meta_dict = tx_meta.__dict__
v4_data = tx_meta_dict.get("v4")
if v4_data is None:
    print("No v4 data found in TransactionMeta. Keys found:", list(tx_meta_dict.keys()))
    exit()

# === 6. Convert v4 data to dict ===
decoded = xdr_to_dict(v4_data)

# === 7. Output to JSON file ===
with open("decoded_result_meta.json", "w", encoding="utf-8") as f:
    json.dump(decoded, f, indent=2, ensure_ascii=False)

print("### Successfully saved full decoded structure to decoded_result_meta.json")
