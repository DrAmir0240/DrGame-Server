FROM python:3.12 AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update \
    && apt install -y \
        gcc \
        build-essential \
        libpq-dev \
        python3-dev \
        libglib2.0-dev \
        libjpeg-dev \
        zlib1g-dev \
        curl \
        tzdata \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /drgame_back

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

FROM base AS dev

CMD ["sh", "-c", \
     "python manage.py migrate && \
      python manage.py runserver 0.0.0.0:8000"]


FROM base AS prod

CMD ["sh", "-c", \
     "python manage.py migrate && \
      python manage.py collectstatic --noinput && \
      gunicorn DrGame.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --log-level info"]
