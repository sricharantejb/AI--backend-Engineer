from flask import Flask, request
import sqlite3

app = Flask(__name__)

DATABASE = "tasks.db"


# Database Connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create Database and Table
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done BOOLEAN NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
        INSERT INTO tasks (title, done)
        VALUES (?, ?)
        """, [
            ("Learn Flask", False),
            ("Build CRUD API", False),
            ("Practice Python", True)
        ])

    conn.commit()
    conn.close()


initialize_database()


# Home Route
@app.route("/")
def home():
    return {
        "message": "Welcome to Task Manager API"
    }


# GET All Tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        })

    return tasks


# GET Task By ID
@app.route("/tasks/<int:id>", methods=["GET"])
def get_task(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {"error": "Task not found"}, 404

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# CREATE Task
@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    if not data or "title" not in data:
        return {"error": "Title is required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (data["title"], False)
    )

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return {
        "id": new_id,
        "title": data["title"],
        "done": False
    }, 201


# UPDATE Task
@app.route("/tasks/<int:id>", methods=["PUT"])
def update_task(id):

    data = request.get_json()

    if not data:
        return {"error": "No data provided"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return {"error": "Task not found"}, 404

    title = data.get("title", task["title"])
    done = data.get("done", bool(task["done"]))

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, done, id)
    )

    conn.commit()
    conn.close()

    return {
        "id": id,
        "title": title,
        "done": done
    }


# DELETE Task
@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = cursor.fetchone()

    if task is None:
        conn.close()
        return {"error": "Task not found"}, 404

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return {
        "message": "Task deleted successfully"
    }


if __name__ == "__main__":
    app.run(debug=True)