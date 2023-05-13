#!/bin/bash

alembic upgrade head

cd /app/src

uvicorn main:app --host 0.0.0.0 --port 8000
