FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# expõe a porta onde o Flask está.
EXPOSE 5000


CMD ["python", "app.py", "0.0.0.0:5000"]