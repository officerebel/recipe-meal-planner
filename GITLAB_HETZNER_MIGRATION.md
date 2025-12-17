<!-- # GitLab + Hetzner Migration Guide

## Overview
Migrate from GitHub/Railway to GitLab/Hetzner with separate Docker containers for frontend and backend.

## Benefits
- ✅ **Cost**: Hetzner ~€5-10/month vs Railway ~$20-30/month
- ✅ **Control**: Full server access, custom configurations
- ✅ **Performance**: Dedicated resources, no cold starts
- ✅ **GitLab CI/CD**: Powerful pipeline system
- ✅ **Docker**: Consistent environments, easy scaling

## Architecture

```
┌─────────────────────────────────────────┐
│           GitLab Repository             │
│         (Source Code + CI/CD)           │
└─────────────────┬───────────────────────┘
                  │ git push triggers
                  ▼
┌─────────────────────────────────────────┐
│          GitLab CI/CD Pipeline          │
│    (Build Docker Images + Deploy)       │
└─────────────────┬───────────────────────┘
                  │ deploys to
                  ▼
┌─────────────────────────────────────────┐
│           Hetzner Cloud Server          │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │  Frontend   │  │    Backend      │   │
│  │  Container  │  │   Container     │   │
│  │ (Nginx +    │  │ (Django +       │   │
│  │  Vue/Quasar)│  │  Gunicorn)      │   │
│  │   Port 80   │  │   Port 8000     │   │
│  └─────────────┘  └─────────────────┘   │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │ PostgreSQL  │  │     Redis       │   │
│  │ Container   │  │   Container     │   │
│  │  Port 5432  │  │   Port 6379     │   │
│  └─────────────┘  └─────────────────┘   │
│                                         │
│         Docker Compose Network          │
└─────────────────────────────────────────┘
```

## Step 1: Create GitLab Repository

### 1.1 Create GitLab Account & Project
```bash
# Go to gitlab.com and create account
# Create new project: recipe-meal-planner
```

### 1.2 Add GitLab Remote
```bash
# Add GitLab as new remote
git remote add gitlab https://gitlab.com/yourusername/recipe-meal-planner.git

# Or rename origin to github and add gitlab as origin
git remote rename origin github
git remote add origin https://gitlab.com/yourusername/recipe-meal-planner.git

# Push to GitLab
git push -u origin main
```

## Step 2: Docker Configuration

### 2.1 Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist/spa /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 2.2 Backend Dockerfile (already exists, but optimize)
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set Django settings module
ENV DJANGO_SETTINGS_MODULE=recipe_meal_planner.settings

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Start command
CMD ["gunicorn", "recipe_meal_planner.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### 2.3 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://backend:8000/api
    networks:
      - app-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/recipe_planner
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=localhost,yourdomain.com
    volumes:
      - media_volume:/app/media
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=recipe_planner
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    networks:
      - app-network

volumes:
  postgres_data:
  media_volume:

networks:
  app-network:
    driver: bridge
```

## Step 3: GitLab CI/CD Pipeline

### 3.1 GitLab CI Configuration
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

services:
  - docker:20.10.16-dind

before_script:
  - docker info

# Test stage
test-backend:
  stage: test
  image: python:3.12
  script:
    - cd backend
    - pip install -r requirements.txt
    - python manage.py test
  only:
    - main
    - merge_requests

test-frontend:
  stage: test
  image: node:18
  script:
    - cd frontend
    - npm ci
    - npm run test:unit
  only:
    - main
    - merge_requests

# Build stage
build:
  stage: build
  image: docker:20.10.16
  script:
    - docker build -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA ./frontend
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA ./backend
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
  only:
    - main

# Deploy stage
deploy:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan $SERVER_HOST >> ~/.ssh/known_hosts
  script:
    - ssh $SERVER_USER@$SERVER_HOST "
        cd /opt/recipe-meal-planner &&
        docker-compose pull &&
        docker-compose up -d --remove-orphans &&
        docker system prune -f
      "
  only:
    - main
  when: manual
```

## Step 4: Hetzner Cloud Setup

### 4.1 Create Hetzner Cloud Server
```bash
# Server specs recommendation:
# - CPX21: 3 vCPU, 4GB RAM, 80GB SSD (~€8.90/month)
# - Ubuntu 22.04 LTS
# - Add SSH key
# - Enable backups (optional, +20%)
```

### 4.2 Server Initial Setup
```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Create app directory
mkdir -p /opt/recipe-meal-planner
cd /opt/recipe-meal-planner

# Create non-root user
adduser deploy
usermod -aG docker deploy
usermod -aG sudo deploy

# Setup SSH for deploy user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### 4.3 Environment Configuration
```bash
# Create .env file on server
cat > /opt/recipe-meal-planner/.env << EOF
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,your-server-ip
DATABASE_URL=postgresql://postgres:password@db:5432/recipe_planner
REDIS_URL=redis://redis:6379/0
EOF

# Set proper permissions
chown deploy:deploy .env
chmod 600 .env
```

## Step 5: Domain & SSL Setup

### 5.1 Domain Configuration
```bash
# Point your domain to Hetzner server IP
# A record: yourdomain.com -> your-server-ip
# A record: www.yourdomain.com -> your-server-ip
```

### 5.2 SSL with Let's Encrypt
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already setup by certbot)
systemctl status certbot.timer
```

### 5.3 Nginx Configuration
```nginx
# /etc/nginx/sites-available/recipe-meal-planner
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        proxy_pass http://localhost:8000;
    }

    # Media files
    location /media/ {
        proxy_pass http://localhost:8000;
    }
}
```

## Step 6: GitLab Variables Setup

### 6.1 CI/CD Variables (GitLab Project Settings > CI/CD > Variables)
```
CI_REGISTRY_IMAGE: registry.gitlab.com/yourusername/recipe-meal-planner
CI_REGISTRY_USER: your-gitlab-username
CI_REGISTRY_PASSWORD: your-gitlab-access-token
SSH_PRIVATE_KEY: your-private-ssh-key
SERVER_HOST: your-server-ip
SERVER_USER: deploy
SECRET_KEY: your-django-secret-key
```

## Step 7: Migration Steps

### 7.1 Data Migration
```bash
# Export data from Railway
railway connect
pg_dump $DATABASE_URL > railway_backup.sql

# Import to Hetzner
scp railway_backup.sql deploy@your-server:/opt/recipe-meal-planner/
ssh deploy@your-server
cd /opt/recipe-meal-planner
docker-compose exec db psql -U postgres -d recipe_planner < railway_backup.sql
```

### 7.2 Media Files Migration
```bash
# Download media from Railway
railway volumes

# Upload to Hetzner
scp -r media/ deploy@your-server:/opt/recipe-meal-planner/
```

## Step 8: Monitoring & Maintenance

### 8.1 Docker Health Checks
```yaml
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 8.2 Backup Script
```bash
#!/bin/bash
# /opt/recipe-meal-planner/backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres recipe_planner > backup_$DATE.sql
tar -czf backup_$DATE.tar.gz backup_$DATE.sql media/
rm backup_$DATE.sql

# Keep only last 7 backups
ls -t backup_*.tar.gz | tail -n +8 | xargs rm -f
```

### 8.3 Cron Jobs
```bash
# Add to crontab
0 2 * * * /opt/recipe-meal-planner/backup.sh
0 3 * * 0 docker system prune -f
```

## Cost Comparison

| Service | Railway | Hetzner |
|---------|---------|---------|
| **Server** | $20-30/month | €8.90/month |
| **Database** | Included | Included |
| **Storage** | Limited | 80GB SSD |
| **Bandwidth** | Limited | 20TB |
| **Total** | ~$25/month | ~€9/month |

## Benefits Summary

✅ **Cost Savings**: ~70% cheaper
✅ **Full Control**: Root access, custom configs
✅ **Better Performance**: Dedicated resources
✅ **No Vendor Lock-in**: Standard Docker setup
✅ **GitLab CI/CD**: Powerful pipeline system
✅ **European Data**: GDPR compliant (if needed)

## Next Steps

1. Create GitLab repository
2. Setup Hetzner server
3. Configure Docker files
4. Setup GitLab CI/CD
5. Migrate data
6. Update DNS
7. Test everything
8. Decommission Railway

Would you like me to start with any specific step? -->

# GitHub/Railway → GitLab/Hetzner Migration (SAFE VERSION)

## Doel
Migratie van een Django + Quasar applicatie van GitHub/Railway naar GitLab + Hetzner,
met Docker containers, gescheiden frontend/backend en veilige deploys.

Deze guide is **gefaseerd** opgezet om risico’s te beperken.

---

## Stack
- Backend: Django + Gunicorn
- Frontend: Vue.js (Quasar) → static build
- Database: PostgreSQL (Docker volume)
- Hosting: Hetzner Cloud VM (Ubuntu 22.04)
- CI/CD: GitLab CI
- Containers: Docker + Docker Compose
- Reverse proxy: Nginx (op host)

---

## Architectuur (hoog niveau)

GitLab repo  
→ GitLab CI (build images)  
→ GitLab Container Registry  
→ Hetzner VM  
→ docker compose pull + up  

Op de VM:
- Nginx (host) → frontend container
- Nginx (host) → backend container (/api)
- Postgres draait in Docker (geen exposed ports)

---

## FASE 1 — GitLab repository (fundament)

### 1.1 Project aanmaken
- Maak **blank project** aan op GitLab
- Geen README / .gitignore / license
- Noteer de **SSH clone URL**

### 1.2 Code pushen
```bash
git remote add gitlab git@gitlab.com:GROUP/PROJECT.git
git push -u gitlab main
