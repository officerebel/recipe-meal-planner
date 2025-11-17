#!/bin/sh
# Start script for Railway deployment
echo "Starting serve on port ${PORT:-8080}"
exec serve dist/spa -s --listen tcp://0.0.0.0:${PORT:-8080}
