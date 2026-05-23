import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("halls.db")

conn.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)""")

conn.execute("""CREATE TABLE IF NOT EXISTS halls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    capacity INTEGER
)""")

conn.execute("""CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    hall_id INTEGER,
    date TEXT,
    time_slot TEXT,
    status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(hall_id) REFERENCES halls(id)
)""")

# Insert sample halls
conn.execute("INSERT OR IGNORE INTO halls (id, name, capacity) VALUES (1, 'ICT Hall 1', 100)")
conn.execute("INSERT OR IGNORE INTO halls (id, name, capacity) VALUES (2, 'ICT Hall 2', 150)")
conn.execute("INSERT OR IGNORE INTO halls (id, name, capacity) VALUES (3, 'ICT Hall 3', 200)")

# Create admin account
password = generate_password_hash("admin123")
conn.execute("INSERT OR IGNORE INTO users (id, name, email, password, role) VALUES (1, 'Admin', 'admin@ict.com', ?, 'admin')", (password,))

conn.commit()
conn.close()

print("Database initialized successfully!")
