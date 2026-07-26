# Flask SQLite CRUD API

A simple RESTful CRUD (Create, Read, Update, Delete) API built using **Python Flask** and **SQLite**. This project demonstrates how to perform database operations through HTTP requests and test them using Postman.

---

## 📌 Project Overview

This application manages a list of tasks using a SQLite database. It provides REST API endpoints to:

- Create a new task
- Retrieve all tasks
- Retrieve a task by ID
- Update an existing task
- Delete a task

The project is built with Flask and uses SQLite as the backend database.

---

## 🚀 Features

- RESTful API using Flask
- SQLite database integration
- CRUD operations
- JSON request and response format
- Tested using Postman

---

## 🛠️ Technologies Used

- Python 3
- Flask
- SQLite
- Postman

---

## 📁 Project Structure

```
Flask_SQLite_CRUD/
│
├── app.py
├── tasks.db
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Flask_SQLite_CRUD
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

The server will start at:

```
http://127.0.0.1:5000
```

---

## 📡 API Endpoints

### Home

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Welcome message |

---

### Get All Tasks

| Method | Endpoint |
|---------|----------|
| GET | `/tasks` |

---

### Get Task By ID

| Method | Endpoint |
|---------|----------|
| GET | `/tasks/<id>` |

Example:

```
GET /tasks/1
```

---

### Create Task

| Method | Endpoint |
|---------|----------|
| POST | `/tasks` |

Request Body

```json
{
    "title": "Learn SQLite"
}
```

---

### Update Task

| Method | Endpoint |
|---------|----------|
| PUT | `/tasks/<id>` |

Request Body

```json
{
    "title": "Learn Flask Updated",
    "done": true
}
```

---

### Delete Task

| Method | Endpoint |
|---------|----------|
| DELETE | `/tasks/<id>` |

Example

```
DELETE /tasks/1
```

---

## 🧪 Testing

All API endpoints were tested successfully using **Postman**.

The following operations were verified:

- ✅ GET All Tasks
- ✅ GET Task by ID
- ✅ POST Create Task
- ✅ PUT Update Task
- ✅ DELETE Task

---

## 📷 Screenshots

The project includes screenshots demonstrating:

- Flask server running
- GET All Tasks
- GET Task by ID
- POST Create Task
- PUT Update Task
- DELETE Task

---

## 🎯 Learning Outcomes

Through this project, I learned:

- Building REST APIs with Flask
- Working with SQLite databases
- Implementing CRUD operations
- Handling JSON requests and responses
- Testing APIs using Postman
- Managing database connections in Python

---

## 👨‍💻 Author

**Sri Charan Tej**
