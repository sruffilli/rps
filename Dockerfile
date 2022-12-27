FROM python:3.11-alpine

WORKDIR /app

COPY . .
RUN pip install -r backend/requirements.txt

CMD ["python3", "backend/app.py"]
