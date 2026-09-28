# The Family Center

Django and Wagtail development project using Python 3.14.7, Django 5.2, and PostgreSQL in Docker Compose. The public homepage is a custom Django view/template; Wagtail manages event pages and informational content.

## Project documentation

- [Project Commander's Intent](COMMANDERS_INTENT.md) — approved durable purpose and guiding direction for the project.
- [Project map](PROJECT_MAP.md) — current repository structure and where responsibilities live.
- [Technical decision log](DECISION_LOG.md) — agreed and proposed architecture decisions.

## Run with Docker

```sh
docker compose up --build
```

Open <http://localhost:8000>. Wagtail admin is at `/admin/`; developer Django
admin is at `/django-admin/`. Compose starts PostgreSQL, waits until it is
healthy, applies Django migrations, and starts the development server. The
database is stored in the `postgres_data_wagtail` Docker volume. The earlier
`postgres_data` volume is left untouched.

If port 8000 is already in use, start Compose with `WEB_PORT=8001 docker compose up --build` and open <http://localhost:8001>.

Create a Django admin account in another terminal:

```sh
docker compose exec web python manage.py createsuperuser
```

Stop the services with `Ctrl+C` or `docker compose down`.

Local media files live in the git-ignored `media/` directory. Django serves
them under `/media/` during development; production media should use a
configured Django storage backend such as the planned Linode Object Storage.

## Search visibility

Local and demo environments stay out of search by default: `robots.txt`
disallows crawling, the homepage is marked `noindex`, and the sitemap is
disabled. For the public site, configure `DJANGO_DEBUG=0`,
`DJANGO_SITE_INDEXABLE=1`, and `PUBLIC_SITE_URL=https://thefamilycenternc.org`
in the server environment. Set the Wagtail Site hostname to
`thefamilycenternc.org` as well so its sitemap uses the canonical domain.

## Run Django directly

The local `.venv` is created with Python 3.14.7. Activate it and run Django
against the Wagtail-ready local SQLite database:

```sh
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Direct local development uses `db-wagtail.sqlite3` (or the path in
`SQLITE_DB_PATH`) so the pre-Wagtail scaffold database remains untouched.

To populate either local database with the existing-site snapshot for CEO review,
run `python manage.py seed_local_preview --confirm-local-preview` (or add
`docker compose exec web` in front of the command for the Compose database).
This command is DEBUG-only, marks the imported copy/events for review, and never
imports legacy photos.

The project pins Python in `.python-version`. The system-provided `pyenv` on
this machine does not include the `pyenv local` subcommand, so that file is
maintained directly.
