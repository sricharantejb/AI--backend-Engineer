# Embeddable Widget & Lead-Capture Platform

Backend capstone implementing authenticated multi-tenant widget CRUD, embed snippet generation, cached public config, versioned widget delivery, CORS submissions, boundary validation, rate limiting, honeypot spam protection, geo fallback, safe side effects, and dashboard APIs.

## Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs

Demo bearer token: `demo-token`

Serve `test_site` separately with `python3 -m http.server 5500`, replacing `REPLACE_WIDGET_ID` with the seed ID.

## API

| Method | Endpoint | Auth |
|---|---|---|
| POST | /widgets | Yes |
| GET | /widgets | Yes |
| GET/PATCH/DELETE | /widgets/{id} | Yes |
| GET | /widgets/{id}/embed | Yes |
| GET | /widgets/{id}/config | Public |
| GET | /widget.v1.js?id={id} | Public |
| POST | /submissions?widget_id={id} | Public/CORS |
| GET | /dashboard/submissions | Yes |
| GET | /dashboard/stats | Yes |

## Architecture

Owner -> authenticated widget API -> tenant-isolated DB -> embed snippet.
Customer site -> cached config/widget JS -> public CORS submission -> validation -> rate limit/honeypot -> geo A/B fallback -> persistence -> non-critical side effect -> owner dashboard.

## Limitations
SQLite and a local demo bearer token keep this project zero-setup. Replace them with PostgreSQL and a real identity provider for production. Geo providers are external free services; failures degrade to no geo.

See `EVIDENCE.md` for acceptance proof and `BUILDLOG.md` for AI usage.
