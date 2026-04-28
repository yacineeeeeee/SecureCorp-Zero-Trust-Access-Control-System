from flask import Flask, request, jsonify
import json

app = Flask(__name__)

with open("policies.json") as f:
    policies = json.load(f)


def check(cond, req):
    for key, val in cond.items():
        parts = key.split(".")
        data = req

        for p in parts:
            data = data.get(p, None)
            if data is None:
                return False

        if data != val:
            return False

    return True


def evaluate(req):
    decision = "DENY"

    for p in policies:
        if check(p["condition"], req):

            if p["effect"].lower() == "deny":
                return "DENY"   # priorité deny

            elif p["effect"].lower() == "allow":
                decision = "ALLOW"

    return decision
@app.route("/evaluate", methods=["POST"])
def eval():
    data = request.json
    print("\n=== PDP DEBUG ===")
    print(data)
    print("DECISION:", evaluate(data))
    print("=================\n")
    return jsonify({"decision": evaluate(data)})

@app.route("/evaluate", methods=["POST"])
def evaluate_route():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    print("\n=== PDP DEBUG ===")
    print("DATA:", data)

    decision = evaluate(data)

    print("DECISION:", decision)
    print("=================\n")

    return jsonify({"decision": decision})

if __name__ == "__main__":
    app.run(port=5001)