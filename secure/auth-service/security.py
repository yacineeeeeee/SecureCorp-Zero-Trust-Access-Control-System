import json, base64, hmac, hashlib, time, uuid

SECRET = b"super_secret_key"

def encode(d): return base64.b64encode(json.dumps(d).encode()).decode()
def decode(d): return json.loads(base64.b64decode(d.encode()).decode())

def sign(data):
    return hmac.new(SECRET, data.encode(), hashlib.sha256).hexdigest()

def create_ticket(payload, service=None):
    payload["exp"] = int(time.time()) + 300
    payload["nonce"] = str(uuid.uuid4())
    if service:
        payload["service"] = service
    data = encode(payload)
    return f"{data}.{sign(data)}"

def verify_ticket(ticket):
    try:
        data, sig = ticket.split(".")
        if not hmac.compare_digest(sign(data), sig):
            return None
        payload = decode(data)
        if payload["exp"] < int(time.time()):
            return None
        return payload
    except:
        return None