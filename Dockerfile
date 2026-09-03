FROM python:3.12
LABEL authors="ipesotskiiy"
WORKDIR /app
COPY . /app
COPY --from=ghcr.io/astral-sh/uv:0.12.6 /uv /uvx /bin/
RUN uv sync --locked
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
