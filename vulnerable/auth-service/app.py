from flask import Flask, request, jsonify
import json, time, base64

app = Flask(__name__)

# ❌ mot de passe en clair
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "manager": {"password": "manager123", "role": "manager"},
    "employee": {"password": "employee123", "role": "employee"}
}

def encode(data):
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode(data):
    return json.loads(base64.b64decode(data).decode())


# 🔑 LOGIN → TGT
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users.get(data["username"])

    if user and user["password"] == data["password"]:
        tgt = {
            "user": data["username"],
            "role": user["role"],
            "location": "external",   # utilisé pour ABAC
            "timestamp": time.time()  # ❌ pas vérifié ensuite
        }
        return jsonify({"TGT": encode(tgt)})

    return jsonify({"error": "Invalid credentials"}), 401


# 🎫 TGT → SERVICE TICKET
@app.route("/request-ticket", methods=["POST"])
def ticket():
    tgt = request.json.get("TGT")

    try:
        data = decode(tgt)
        # ❌ aucune vérification (signature, expiration…)
        return jsonify({"service_ticket": encode(data)})
    except:
        return jsonify({"error": "Invalid TGT"}), 403


if __name__ == "__main__":
    app.run(port=5000)