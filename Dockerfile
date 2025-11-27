FROM python:3.12.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY . .

RUN pip install poetry
RUN poetry install --no-interaction --no-ansi --without dev
RUN chmod +x entrypoint.sh

EXPOSE 8000