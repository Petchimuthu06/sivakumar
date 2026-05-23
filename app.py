from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# Database connection helper
def get_db():
    conn = sqlite3.connect("halls.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                    (name, email, password, "user"))
        conn.commit()
        conn.close()
        flash("Registration successful! Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT b.id, h.name as hall_name, b.date, b.time_slot, b.status                  FROM bookings b JOIN halls h ON b.hall_id = h.id                  WHERE b.user_id = ?", (session["user_id"],))
    bookings = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", bookings=bookings)

@app.route("/book", methods=["GET", "POST"])
def book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM halls")
    halls = cur.fetchall()

    if request.method == "POST":
        hall_id = request.form["hall_id"]
        date = request.form["date"]
        time_slot = request.form["time_slot"]

        cur.execute("INSERT INTO bookings (user_id, hall_id, date, time_slot, status) VALUES (?, ?, ?, ?, ?)",
                    (session["user_id"], hall_id, date, time_slot, "Pending"))
        conn.commit()
        flash("Booking request submitted!")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("booking.html", halls=halls)

@app.route("/admin")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT b.id, u.name, h.name as hall_name, b.date, b.time_slot, b.status                  FROM bookings b JOIN users u ON b.user_id = u.id                  JOIN halls h ON b.hall_id = h.id")
    bookings = cur.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", bookings=bookings)

@app.route("/update_status/<int:booking_id>/<status>")
def update_status(booking_id, status):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
