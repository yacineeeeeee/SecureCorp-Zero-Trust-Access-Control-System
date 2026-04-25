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
    for p in policies:
        if check(p["condition"], req):
            return p["effect"].upper()
    return "DENY"


@app.route("/evaluate", methods=["POST"])
def eval():
    return jsonify({"decision": evaluate(request.json)})


if __name__ == "__main__":
    app.run(port=5001)