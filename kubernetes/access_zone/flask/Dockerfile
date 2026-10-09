# Kubernetes image of the REST API (Flask), built from access_zone/flask by kubernetes/start.sh.
# Differences with access_zone/flask/Dockerfile.flask (kept for Compose) :
#  - only the code is copied : no .env baked in the image, the config comes from the ConfigMap / Secret
#  - fixed numeric UID : runAsUser of the pod
FROM python:3.12.12-alpine

RUN adduser -D -u 55556 flask

WORKDIR /home/app

# dependencies first : the layer is reused as long as requirements.txt does not change
COPY requirements.txt .
RUN python -m venv /home/app/venv && \
    /home/app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /home/app/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/home/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY app.py wsgi.py ./
COPY datalake_authclient/ datalake_authclient/
COPY datalake_objectstoreclient/ datalake_objectstoreclient/

USER 55556:55556
EXPOSE 5000

CMD ["gunicorn", "-w", "3", "-t", "60", "-b", "0.0.0.0:5000", "app:app"]
