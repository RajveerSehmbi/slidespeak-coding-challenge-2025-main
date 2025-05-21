FROM python:3.10-alpine

WORKDIR /app

RUN addgroup -S celerygroup && adduser -S celeryuser -G celerygroup

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app app
COPY make_celery.py .

RUN mkdir -p /tmp && chown -R celeryuser:celerygroup /tmp

USER celeryuser

CMD ["flask", "run", "--host=0.0.0.0"]