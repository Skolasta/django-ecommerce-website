#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# The "exec" command is important for ensuring that the container
# receives signals properly (like a stop signal from docker-compose down).
# "$@" passes all arguments from the Docker command to this script.
exec "$@"
