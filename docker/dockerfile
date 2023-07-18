FROM python:3.11-alpine
WORKDIR my_salary
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LOGGING__LEVEL="INFO"
ENV HOST="0.0.0.0"
ENV PORT="8003"

ENV UVICORN_WORKERS=1
ENV UVICORN_ARGS "main:app --host $HOST --port $PORT --workers $UVICORN_WORKERS"

ENV POSTGRES__DB=""
ENV POSTGRES__USER=""
ENV POSTGRES__PASSWORD=""
ENV POSTGRES__HOST="host.docker.internal"
ENV POSTGRES__PORT=5432

RUN pip install --upgrade pip  --no-cache-dir
RUN pip install "poetry"
COPY poetry.lock pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install

COPY app .
CMD uvicorn $UVICORN_ARGS