from flask import Flask, request, jsonify
import hashlib, uuid, time
from security import create_ticket, verify_ticket

app = Flask(__name__)

# =========================
# Utils
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# =========================
# Fake DB
# =========================

users = {
    "admin": {"password": hash_pw("admin123"), "role": "admin"},
    "manager": {"password": hash_pw("manager123"), "role": "manager"},
    "employee": {"password": hash_pw("employee123"), "role": "employee"}
}

# =========================
# LOGIN -> TGT
# =========================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)

    if user and user["password"] == hash_pw(password):

        payload = {
            "user": {
                "username": username,
                "role": user["role"],
                "location": "internal"
            },
            "nonce": str(uuid.uuid4()),
            "timestamp": time.time()
        }

        tgt = create_ticket(payload)

        return jsonify({"TGT": tgt})

    return jsonify({"error": "Invalid credentials"}), 401


# =========================
# TGT -> SERVICE TICKET
# =========================

@app.route("/request-ticket", methods=["POST"])
def request_ticket():
    tgt = request.json.get("TGT")
    decoded = verify_ticket(tgt)

    if not decoded:
        return jsonify({"error": "Invalid TGT"}), 403

    # Ajouter service + nouveau nonce
    payload = {
        "user": decoded["user"],  # déjà structuré correctement
        "service": "resource-service",
        "nonce": str(uuid.uuid4()),
        "timestamp": time.time()
    }

    ticket = create_ticket(payload)

    return jsonify({"service_ticket": ticket})


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)