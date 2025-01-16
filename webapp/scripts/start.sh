#! /usr/bin/env bash

set -e
set -x

# Run migrations
alembic upgrade head

python3 app/prestart.py

fastapi dev app/main.py --host 0.0.0.0 --port 80
