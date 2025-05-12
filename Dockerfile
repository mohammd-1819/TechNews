FROM python:3.11
WORKDIR /TechNews
COPY requirements.txt /TechNews/

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

COPY . /TechNews/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "TechNews.wsgi:application"]
