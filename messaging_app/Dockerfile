FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# System dependencies for MySQL client/builds and netcat for health/wait scripts
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		build-essential \
		default-libmysqlclient-dev \
		pkg-config \
		netcat-traditional \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy project files
COPY . /app/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
