FROM python:3.10-slim-bullseye

ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/home/flaskapp

RUN useradd --create-home --home-dir /home/flaskapp flaskapp
WORKDIR /home/flaskapp

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev pkg-config libpango-1.0-0 libharfbuzz0b \
    libfontconfig1 libpangoft2-1.0-0 locales \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i -e 's/# es_AR.UTF-8 UTF-8/es_AR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
ENV LANG es_AR.UTF-8

COPY requirements.txt .
RUN pip install --no-cache-dir "setuptools<58.0.0"
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

COPY . ./app

USER root
RUN mkdir -p /home/flaskapp/app/uploads/comprobantes && \
    chown -R flaskapp:flaskapp /home/flaskapp/app/uploads
USER flaskapp

EXPOSE 5000

ENTRYPOINT [ "python", "app/main.py" ]