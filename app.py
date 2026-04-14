from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from parse_data import parse_prices, get_product_list, get_latest_prices
from functools import wraps

app = Flask(__name__)
app.secret_key = "fertitrack-secret-2024"

# Simple password protection
PASSWORD = "fertitrack2024"

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
    data = parse_prices()
    latest = get_latest_prices(data)
    products = get_product_list(data)
    return render_template("index.html", latest=latest, products=products)

@app.route("/api/data")
@login_required
def api_data():
    data = parse_prices()
    return jsonify(data)

@app.route("/api/latest")
@login_required
def api_latest():
    data = parse_prices()
    latest = get_latest_prices(data)
    return jsonify(latest)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
