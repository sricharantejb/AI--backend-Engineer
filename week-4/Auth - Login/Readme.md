# BE-03 Authentication API

Backend AI Engineering - Week 4 Assignment

## Description

This project demonstrates authentication using FastAPI and Supabase Authentication.

Users can:

- Sign Up
- Login
- Logout
- Access Public APIs
- Access Protected APIs using JWT Authentication

---

## Technologies Used

- Python
- FastAPI
- Supabase
- Swagger UI
- Uvicorn
- python-dotenv

---

## Installation

Clone the repository

```bash
git clone <your-github-repository>
```

Create Virtual Environment

```bash
python3 -m venv venv
```

Activate

Mac/Linux

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install Requirements

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file

```env
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

---

## Run Project

```bash
uvicorn app:app --reload
```

Open

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Protected |
|---------|----------|-----------|
| GET | / | No |
| GET | /public/info | No |
| POST | /auth/signup | No |
| POST | /auth/login | No |
| POST | /auth/logout | Yes |
| GET | /protected/profile | Yes |
| GET | /protected/dashboard | Yes |

---

## Authentication

This project uses Supabase Authentication.

Protected APIs require

```
Authorization: Bearer <access_token>
```

---

## Swagger

FastAPI automatically generates Swagger UI.

Open

```
http://127.0.0.1:8000/docs
```

Use the **Authorize** button and paste your Access Token.

---

## Author

Sri Charan Tej