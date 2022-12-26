FROM python:3.11-alpine

WORKDIR /app

COPY backend/requirements.txt .
COPY backend/main.py .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
