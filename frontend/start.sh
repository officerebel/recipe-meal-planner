#!/bin/sh
# Start script for Railway deployment
# Railway automatically sets PORT, but we'll default to 3000 if not set
export PORT=${PORT:-3000}
echo "Starting serve on port $PORT"
exec serve dist/spa -s -l $PORT
