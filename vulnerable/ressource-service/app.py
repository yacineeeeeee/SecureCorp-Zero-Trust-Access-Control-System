from flask import Flask, request, jsonify
import base64, json, requests

app = Flask(__name__)

PDP = "http://localhost:5001/evaluate"

def decode(ticket):
    try:
        return json.loads(base64.b64decode(ticket).decode())
    except:
        return None


@app.route("/resource/<rid>", methods=["GET"])
def resource(rid):
    ticket = request.headers.get("Authorization")

    if not ticket:
        return jsonify({"error": "No ticket"}), 401

    user = decode(ticket)

    # ❌ validation faible
    if not user:
        return jsonify({"error": "Invalid ticket"}), 403

    resource = {
        "id": rid,
        "classification": "secret" if rid == "1" else "public"
    }

    req = {
        "user": user,
        "resource": resource,
        "action": "read"
    }

    try:
        res = requests.post(PDP, json=req)
        decision = res.json()["decision"]

        if decision == "ALLOW":
            return jsonify({
                "msg": "ACCESS GRANTED",
                "user": user,
                "resource": resource
            })
        else:
            return jsonify({"error": "DENIED"}), 403

    except:
        return jsonify({"error": "PDP error"}), 500


if __name__ == "__main__":
    app.run(port=5002)