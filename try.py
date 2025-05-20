import hmac
import hashlib

API_SECRET = "c7da852ce81739784934dea29a6a4a763a698ecc3c035d24c31acf52d2dceb6d123bc0841aa1bddee054854d636334b2cd2fe953122935b8e49eecd1eadc468f365e7e7c4d4c33b8acd02277d28610f22be5e8233dee8a6553a5bb22ea35be3c46a31a5f"
ENDPOINT = "/ver1/accounts"

signature = hmac.new(
    API_SECRET.encode(),
    ENDPOINT.encode(),
    hashlib.sha256
).hexdigest()

print(signature)
