from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from parse_data import get_product_list, get_latest_prices
from functools import wraps

app = Flask(__name__)
app.secret_key = "fertitrack-secret-2024"

PASSWORD = "fertitrack2024"

# Load pre-generated JSON — fast, no Excel parsing needed at runtime
_data_path = os.path.join(os.path.dirname(__file__), "data", "prices.json")
with open(_data_path) as f:
    _cached_data = json.load(f)
print(f"Loaded {len(_cached_data)} price series from JSON.")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "Incorrect password. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    latest = get_latest_prices(_cached_data)
    products = get_product_list(_cached_data)
    return render_template("index.html", latest=latest, products=products)

@app.route("/api/data")
@login_required
def api_data():
    return jsonify(_cached_data)

@app.route("/api/latest")
@login_required
def api_latest():
    latest = get_latest_prices(_cached_data)
    return jsonify(latest)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
