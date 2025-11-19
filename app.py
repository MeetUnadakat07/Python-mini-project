from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB = "expenses.db"


def db_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    conn = db_conn()
    conn.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()

    return render_template("index.html")


@app.route("/get_expenses")
def get_expenses():
    conn = db_conn()
    rows = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.get_json()
    amount = float(data["amount"])
    category = data["category"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = db_conn()
    conn.execute(
        "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
        (amount, category, date)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


@app.route("/delete_expense", methods=["POST"])
def delete_expense():
    row_id = request.json["id"]

    conn = db_conn()
    conn.execute("DELETE FROM expenses WHERE id=?", (row_id,))
    conn.commit()
    conn.close()

    return jsonify({"status": "deleted"})


@app.route("/pie_data")
def pie_data():
    conn = db_conn()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses GROUP BY category"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    print("🚀 Running on http://127.0.0.1:5000")
    app.run(debug=True)
