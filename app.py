import sqlite3
import random
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "dileep_energy_secret"

DATABASE = "energy.db"


# ----------------------------
# DATABASE SETUP
# ----------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS energy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consumption INTEGER,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()


init_db()


# ----------------------------
# REGISTER
# ----------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = data["password"]

    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User Registered"}), 201
    except:
        return jsonify({"error": "User already exists"}), 400


# ----------------------------
# LOGIN + JWT
# ----------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        token = jwt.encode({
            "user_id": user[0],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid Credentials"}), 401


# ----------------------------
# LIVE ENERGY
# ----------------------------
@app.route("/api/energy/live", methods=["GET"])
def energy_live():
    consumption = random.randint(100, 600)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO energy (consumption, timestamp) VALUES (?, ?)",
              (consumption, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"consumption": consumption})


# ----------------------------
# ALERTS
# ----------------------------
@app.route("/api/alerts", methods=["GET"])
def alerts():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT consumption FROM energy ORDER BY id DESC LIMIT 1")
    data = c.fetchone()
    conn.close()

    if data and data[0] > 500:
        return jsonify({"alert": "High Energy Usage"})
    return jsonify({"alert": "Normal"})


# ----------------------------
# ROOT CHECK
# ----------------------------
@app.route("/")
def home():
    return "Energy Backend Running Successfully"


# ----------------------------
# RENDER COMPATIBLE RUN
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
