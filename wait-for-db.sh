#!/bin/sh

echo "Warte auf PostgreSQL..."

while ! nc -z db 5432; do
  echo "PostgreSQL nicht erreichbar, warte 1 Sekunde..."
  sleep 1
done

echo "PostgreSQL ist bereit."
exec "$@"
