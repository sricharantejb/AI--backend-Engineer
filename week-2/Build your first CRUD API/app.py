from flask import Flask, request

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Learn Flask", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Practice Python", "done": True}
]

@app.route("/")
def home():
    return {"message": "Welcome to Task Manager API"}

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return tasks

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "done": False
    }

    tasks.append(new_task)

    return new_task, 201

if __name__ == "__main__":
    app.run(debug=True)