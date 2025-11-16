# Use Node.js 20 Alpine image (required for Quasar)
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git python3 make g++

# Copy all files
COPY . .

# Install dependencies (ignore package-lock for now)
RUN rm -f package-lock.json
RUN npm install

# Build the Quasar application
RUN npm run build

# Install serve globally for serving static files
RUN npm install -g serve

# Expose the port that Railway will provide
EXPOSE $PORT

# Start the application
CMD ["sh", "-c", "serve dist/spa -s --listen tcp://0.0.0.0:${PORT:-8080}"]