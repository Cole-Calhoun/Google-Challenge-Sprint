FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "-b", ":8080", "app:app"]
