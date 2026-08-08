FROM python:3.11-slim

WORKDIR /app

COPY ./services/service-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python", "-u", "-m", "uvicorn", "services.service-backend.app.main:app", "--host", "0.0.0.0", "--port", "80"]
