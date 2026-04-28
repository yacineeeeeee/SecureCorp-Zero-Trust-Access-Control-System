from flask import Flask, request, jsonify
import requests
from security import verify_ticket

app = Flask(__name__)

PDP = "http://policy-service:5001/evaluate"
used_nonces = set()

@app.route("/resource/<rid>", methods=["GET"])
def resource(rid):
    ticket = request.headers.get("Authorization")

    if not ticket:
        return jsonify({"error": "No ticket"}), 401

    user = verify_ticket(ticket)
    if not user:
        return jsonify({"error": "Invalid or expired ticket"}), 403

    if user["nonce"] in used_nonces:
        return jsonify({"error": "Replay detected"}), 403
    used_nonces.add(user["nonce"])

    if user.get("service") != "resource-service":
        return jsonify({"error": "Wrong service"}), 403

    resource = {
        "id": rid,
        "classification": "secret" if rid == "1" else "public"
    }

    payload = {"user": user, "resource": resource, "action": "read"}

    try:
        res = requests.post(PDP, json=payload)
        res.raise_for_status()
        decision = res.json().get("decision", "DENY")
    except Exception as e:
        print("PDP ERROR:", e)
        return jsonify({"error": "PDP failure"}), 500

    if decision == "ALLOW":
        return jsonify({"msg": "ACCESS GRANTED", "resource": resource})
    else:
        return jsonify({"error": "DENIED"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)