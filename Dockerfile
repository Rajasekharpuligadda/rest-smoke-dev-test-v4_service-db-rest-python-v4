FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    ([ -f kafka/requirements.txt ] && pip install -r kafka/requirements.txt || true)

EXPOSE 5000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "run:app"]