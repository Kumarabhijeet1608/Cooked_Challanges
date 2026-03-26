FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create uploads directory and make entrypoint executable
RUN mkdir -p /app/data/uploads && chmod +x /app/entrypoint.sh

ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

# Entrypoint writes flags to temp files, scrubs env, then starts Flask
CMD ["/app/entrypoint.sh"]
