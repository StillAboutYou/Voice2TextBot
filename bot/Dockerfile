FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry
RUN python3 -m poetry config virtualenvs.create false && python3 -m poetry install --no-root

COPY . .

CMD ["python", "-m", "bot.bot"]
