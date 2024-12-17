FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

RUN pip install --no-cache-dir --use-pep517 llvmlite==0.43.0

RUN python3 -m poetry config virtualenvs.create false && python3 -m poetry install --no-root

RUN pip3 install --index-url=https://download.pytorch.org/whl/cpu torch==2.3.0 torchaudio==2.3.0 torchvision==0.18.0
RUN pip3 install openai-whisper==20231117

COPY . .

CMD ["python3", "-m", "core.consumer"]
