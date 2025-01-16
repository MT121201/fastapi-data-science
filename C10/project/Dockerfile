FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy your application code last to ensure rebuilds when code changes
COPY ./ /app

ENV PYTHONPATH=/app
ENV APP_MODULE=project.app:app
