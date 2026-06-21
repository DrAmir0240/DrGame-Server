FROM repo.webteamwork.ir/library/python:3.12 AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN rm -rf /etc/apt/sources.list.d/* \
    && echo "deb [trusted=yes] https://repo.webteamwork.ir/repository/apt-trixie trixie main contrib non-free" \
       > /etc/apt/sources.list \
    && apt update \
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

RUN pip install --trusted-host repo.webteamwork.ir \
        --upgrade pip \
        --index-url https://repo.webteamwork.ir/repository/pip-package/simple/ \
    && pip install --trusted-host repo.webteamwork.ir \
        --no-cache-dir \
        --index-url https://repo.webteamwork.ir/repository/pip-package/simple/ \
        -r requirements.txt

COPY . .

EXPOSE 8000

FROM base AS dev

CMD ["sh", "-c", \
     "python manage.py migrate && \
      python manage.py runserver 0.0.0.0:8000"]


FROM base AS prod

# نکته: «config» رو با اسم واقعی پکیج settings جنگو پروژه‌تون جایگزین کنید (همون پوشه‌ای که wsgi.py توشه)
CMD ["sh", "-c", \
     "python manage.py migrate && \
      python manage.py collectstatic --noinput && \
      gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --log-level info"]
