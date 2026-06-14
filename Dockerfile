FROM python:3.12-slim

WORKDIR /app

# Dependencies install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Project files
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]