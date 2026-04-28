from flask import Flask, request, jsonify
import json
import datetime

app = Flask(__name__)

# Charger les politiques
with open("policies.json") as f:
    policies = json.load(f)


# 🔐 Fonction de vérification des conditions (ABAC)
def check(condition, data):
    for key, value in condition.items():
        tmp = data

        # Navigation dans JSON imbriqué (ex: user.role)
        for part in key.split("."):
            if isinstance(tmp, dict) and part in tmp:
                tmp = tmp[part]
            else:
                return False

        if tmp != value:
            return False

    return True


# 🧠 Moteur de décision (PDP)
def evaluate(data):
    # ABAC : contrainte temporelle
    hour = datetime.datetime.now().hour
    if hour < 8 or hour > 18:
        return "DENY"

    decision = "DENY"  # par défaut (Zero Trust)

    for policy in policies:
        if check(policy["condition"], data):

            # priorité au DENY
            if policy["effect"].lower() == "deny":
                return "DENY"

            elif policy["effect"].lower() == "allow":
                decision = "ALLOW"

    return decision


# 🌐 Endpoint PDP
@app.route("/evaluate", methods=["POST"])
def eval_route():
    data = request.json

    # DEBUG (utile pour ton rapport)
    print("\n=== PDP DEBUG ===")
    print("INPUT DATA:", data)
    print("POLICIES:", policies)

    decision = evaluate(data)

    print("DECISION:", decision)
    print("=================\n")

    return jsonify({"decision": decision})


# 🚀 Lancement du service
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)