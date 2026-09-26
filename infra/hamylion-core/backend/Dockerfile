FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY backend/worker.py ./worker.py
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
