#!/usr/bin/env python3
# syntax=docker/dockerfile:1

FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scripts/demo_github_org_client.py"]
