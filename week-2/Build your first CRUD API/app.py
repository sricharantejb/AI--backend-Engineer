from flask import Flask, request

app = Flask(__name__)

# In-memory task list
tasks = [
    {"id": 1, "title": "Learn Flask", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Practice Python", "done": True}
]

# Home Route
@app.route("/")
def home():
    return {"message": "Welcome to Task Manager API"}

# GET all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return tasks

# GET task by ID
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return {"error": "Task not found"}, 404

# POST create task
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or "title" not in data:
        return {"error": "Title is required"}, 400

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "done": False
    }

    tasks.append(new_task)

    return new_task, 201

# PUT update task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    for task in tasks:
        if task["id"] == task_id:

            if "title" in data:
                task["title"] = data["title"]

            if "done" in data:
                task["done"] = data["done"]

            return task

    return {"error": "Task not found"}, 404

# DELETE task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {"message": "Task deleted successfully"}

    return {"error": "Task not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)
