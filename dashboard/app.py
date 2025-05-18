from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def get_logs():
    logs = ["Step 1: Node 0 attacked", "Step 2: Node 2 defended"]
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)