ACTIVATE VENV:
>. ./activate.sh

NEW START:

Creates Postgres Docker container & exports DATABASE_URL
>. ./db_scripts/start.sh

Run alembic revision
>./db_scripts/revision.sh initial_db --autogenerate

Update alembic head
>./db_scripts/migrate.sh
