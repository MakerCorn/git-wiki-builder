FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY docs/ ./docs/

EXPOSE 8000

CMD ["python", "src/main.py"]
