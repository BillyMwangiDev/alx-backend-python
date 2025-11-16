# ADR 0001: Initial Architecture

## Context
We need a minimal messaging backend with users, conversations, and messages. Requirements include REST API, custom user model, tests, CI, and Docker.

## Decision
- Use Django 4.x and Django REST Framework.
- Custom user model in `chats.User` using UUID primary key and role field.
- Conversations have many-to-many participants; messages belong to a conversation and have a sender.
- Use `python-decouple` for configuration via `.env`.
- Default DB is SQLite for local; provide Docker compose for Postgres in dev.
- CI via GitHub Actions: lint, tests, security (pip-audit).

## Consequences
- Must set `AUTH_USER_MODEL="chats.User"`.
- Migrations must run from scratch; commit migration files.
- API base path `/api/v1/` for future versioning.


