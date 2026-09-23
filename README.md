# The Family Center

Django development project using Python 3.14.7 and PostgreSQL in Docker Compose.

## Run with Docker

```sh
docker compose up --build
```

Open <http://localhost:8000>. Compose starts PostgreSQL, waits until it is
healthy, applies Django migrations, and starts the development server. The
database is stored in the `postgres_data` Docker volume.

Create a Django admin account in another terminal:

```sh
docker compose exec web python manage.py createsuperuser
```

Stop the services with `Ctrl+C` or `docker compose down`.

## Run Django directly

The local `.venv` is created with Python 3.14.7. Activate it and run Django
against the default local SQLite database:

```sh
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

The project pins Python in `.python-version`. The system-provided `pyenv` on
this machine does not include the `pyenv local` subcommand, so that file is
maintained directly.
