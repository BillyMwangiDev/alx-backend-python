## Messaging App (Django + DRF)

A minimal messaging backend with custom user model, conversations, and messages using Django and Django REST Framework.

### Setup

1) Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
# on macOS/Linux: source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Environment variables

Create a `.env` file in `messaging_app/` (same directory as `manage.py`) with:

```
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
CORS_ALLOW_ALL_ORIGINS=True
```

4) Run migrations and start server

```bash
cd messaging_app
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### API

Base path: `/api/v1/`

- Conversations:
  - `GET /api/v1/conversations/` list
  - `POST /api/v1/conversations/` create with participants `[user_id, ...]`
  - `POST /api/v1/conversations/{id}/send/` body: `{ "message_body": "Hello" }`
- Messages:
  - `GET /api/v1/messages/?conversation={conversation_id}`
  - `POST /api/v1/messages/` body: `{ "conversation": "<id>", "message_body": "..." }` (sender = current user)

Authentication: Session or Basic. Use admin to create users or `createsuperuser`.

### Testing

```bash
pytest -q
```

### Linting and Security

```bash
flake8
black --check .
pip-audit
```

### Docker (Dev)

```bash
docker-compose up --build
```

Services:
- `web`: Django app
- `db`: Postgres


