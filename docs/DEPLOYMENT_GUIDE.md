# Recipe Meal Planner - Deployment Guide

## 🚀 Deployment Overview

This guide covers deploying the Recipe Meal Planner application in various environments, from development to production.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.9+ 
- **Node.js**: 16+ with npm
- **Database**: SQLite (development) / PostgreSQL (production)
- **Web Server**: Nginx (production)
- **Process Manager**: Gunicorn (production)

### Development Tools
- Git
- Docker (optional)
- Virtual environment (venv/virtualenv)

## 🛠️ Development Setup

### Backend Setup (Django)

1. **Clone Repository**
```bash
git clone <repository-url>
cd recipe-meal-planner
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

5. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser
python create_sample_data.py  # Optional: Create sample data
```

6. **Run Development Server**
```bash
python manage.py runserver
```

### Frontend Setup (Vue.js + Quasar)

1. **Navigate to Frontend Directory**
```bash
cd quasar-project
```

2. **Install Dependencies**
```bash
npm install
```

3. **Configure Environment**
```bash
# Create .env file
cp .env.example .env

# Edit .env with API URL
VUE_APP_API_URL=http://localhost:8000/api
```

4. **Run Development Server**
```bash
npm run dev
```

### Development URLs
- **Frontend**: http://localhost:9006
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## 🐳 Docker Development Setup

### Using Docker Compose

1. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=sqlite:///db.sqlite3
    volumes:
      - .:/app
    command: python manage.py runserver 0.0.0.0:8000

  frontend:
    build: ./quasar-project
    ports:
      - "9006:9006"
    volumes:
      - ./quasar-project:/app
    command: npm run dev

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

2. **Run with Docker**
```bash
docker-compose up -d
```

## 🏭 Production Deployment

### Server Setup (Ubuntu/Debian)

1. **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install Dependencies**
```bash
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

3. **Create Application User**
```bash
sudo adduser --system --group recipeapp
sudo mkdir -p /var/www/recipe-meal-planner
sudo chown recipeapp:recipeapp /var/www/recipe-meal-planner
```

### Database Setup (PostgreSQL)

1. **Create Database and User**
```bash
sudo -u postgres psql

CREATE DATABASE recipe_meal_planner;
CREATE USER recipeapp WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE recipe_meal_planner TO recipeapp;
\q
```

2. **Configure PostgreSQL**
```bash
# Edit /etc/postgresql/*/main/pg_hba.conf
# Add line: local recipe_meal_planner recipeapp md5
sudo systemctl restart postgresql
```

### Backend Deployment

1. **Deploy Code**
```bash
sudo -u recipeapp git clone <repository-url> /var/www/recipe-meal-planner
cd /var/www/recipe-meal-planner
sudo -u recipeapp python3 -m venv venv
sudo -u recipeapp venv/bin/pip install -r requirements.txt
```

2. **Production Environment**
```bash
# Create /var/www/recipe-meal-planner/.env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://recipeapp:secure_password_here@localhost/recipe_meal_planner
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

3. **Database Migration**
```bash
sudo -u recipeapp venv/bin/python manage.py migrate
sudo -u recipeapp venv/bin/python manage.py collectstatic --noinput
sudo -u recipeapp venv/bin/python manage.py createsuperuser
```

4. **Gunicorn Configuration**
```bash
# Create /etc/systemd/system/recipe-meal-planner.service
[Unit]
Description=Recipe Meal Planner Django App
After=network.target

[Service]
User=recipeapp
Group=recipeapp
WorkingDirectory=/var/www/recipe-meal-planner
Environment="PATH=/var/www/recipe-meal-planner/venv/bin"
ExecStart=/var/www/recipe-meal-planner/venv/bin/gunicorn --workers 3 --bind unix:/var/www/recipe-meal-planner/recipe_meal_planner.sock recipe_meal_planner.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start Services**
```bash
sudo systemctl daemon-reload
sudo systemctl start recipe-meal-planner
sudo systemctl enable recipe-meal-planner
```

### Frontend Deployment

1. **Build Frontend**
```bash
cd /var/www/recipe-meal-planner/quasar-project
sudo -u recipeapp npm install
sudo -u recipeapp npm run build
```

2. **Configure Production Environment**
```bash
# Edit quasar-project/.env.production
VUE_APP_API_URL=https://yourdomain.com/api
```

### Nginx Configuration

1. **Create Nginx Config**
```nginx
# /etc/nginx/sites-available/recipe-meal-planner
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend (Vue.js)
    location / {
        root /var/www/recipe-meal-planner/quasar-project/dist/spa;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://unix:/var/www/recipe-meal-planner/recipe_meal_planner.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://unix:/var/www/recipe-meal-planner/recipe_meal_planner.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/recipe-meal-planner/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /var/www/recipe-meal-planner/media/;
    }
}
```

2. **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/recipe-meal-planner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Configuration (Let's Encrypt)

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Obtain SSL Certificate**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-renewal**
```bash
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

## ☁️ Cloud Deployment Options

### AWS Deployment

#### Using Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize Application**
```bash
eb init recipe-meal-planner
eb create production
```

3. **Deploy**
```bash
eb deploy
```

#### Using EC2 + RDS

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Configure security groups (HTTP, HTTPS, SSH)
   - Launch with key pair

2. **Setup RDS Database**
   - Create PostgreSQL instance
   - Configure security groups
   - Note connection details

3. **Deploy Application**
   - Follow production deployment steps above
   - Use RDS connection string in environment

### Digital Ocean Deployment

#### Using App Platform

1. **Create App**
   - Connect GitHub repository
   - Configure build settings
   - Set environment variables

2. **Database Setup**
   - Create managed PostgreSQL database
   - Configure connection

#### Using Droplets

1. **Create Droplet**
   - Choose Ubuntu 20.04
   - Configure SSH keys
   - Setup firewall

2. **Deploy Application**
   - Follow production deployment steps
   - Configure domain and SSL

### Heroku Deployment

1. **Install Heroku CLI**
```bash
# Install from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Prepare Application**
```bash
# Create Procfile
echo "web: gunicorn recipe_meal_planner.wsgi" > Procfile

# Create runtime.txt
echo "python-3.9.7" > runtime.txt
```

3. **Deploy**
```bash
heroku create recipe-meal-planner-app
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
```

## 🔧 Configuration Management

### Environment Variables

#### Backend (.env)
```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Storage (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

#### Frontend (.env.production)
```bash
VUE_APP_API_URL=https://yourdomain.com/api
VUE_APP_ENVIRONMENT=production
```

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable SSL/HTTPS
- [ ] Set secure headers
- [ ] Configure firewall
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs

## 📊 Monitoring and Maintenance

### Log Management

1. **Django Logs**
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/recipe-meal-planner/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

2. **Nginx Logs**
```bash
# Monitor access logs
sudo tail -f /var/log/nginx/access.log

# Monitor error logs
sudo tail -f /var/log/nginx/error.log
```

### Performance Monitoring

1. **Database Performance**
```bash
# Monitor PostgreSQL
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

2. **System Resources**
```bash
# Monitor system resources
htop
df -h
free -m
```

### Backup Strategy

1. **Database Backup**
```bash
# Create backup script
#!/bin/bash
pg_dump recipe_meal_planner > /backups/db_$(date +%Y%m%d_%H%M%S).sql
```

2. **File Backup**
```bash
# Backup media files
rsync -av /var/www/recipe-meal-planner/media/ /backups/media/
```

### Update Procedure

1. **Backup Current Version**
```bash
sudo -u recipeapp git stash
sudo systemctl stop recipe-meal-planner
```

2. **Deploy Updates**
```bash
sudo -u recipeapp git pull origin main
sudo -u recipeapp venv/bin/pip install -r requirements.txt
sudo -u recipeapp venv/bin/python manage.py migrate
sudo -u recipeapp venv/bin/python manage.py collectstatic --noinput
```

3. **Restart Services**
```bash
sudo systemctl start recipe-meal-planner
sudo systemctl reload nginx
```

## 🔍 Troubleshooting

### Common Issues

#### 502 Bad Gateway
- Check Gunicorn service status
- Verify socket file permissions
- Check Nginx configuration

#### Database Connection Errors
- Verify database credentials
- Check PostgreSQL service status
- Confirm network connectivity

#### Static Files Not Loading
- Run `collectstatic` command
- Check Nginx static file configuration
- Verify file permissions

#### SSL Certificate Issues
- Renew certificates with Certbot
- Check certificate expiration
- Verify domain configuration

### Debug Commands

```bash
# Check service status
sudo systemctl status recipe-meal-planner
sudo systemctl status nginx
sudo systemctl status postgresql

# View logs
sudo journalctl -u recipe-meal-planner -f
sudo tail -f /var/log/nginx/error.log

# Test configuration
sudo nginx -t
sudo -u recipeapp venv/bin/python manage.py check --deploy
```

---

## 📞 Support

For deployment issues:
- Check logs first
- Review configuration files
- Verify environment variables
- Test individual components

**Deployment Guide Version**: 1.0  
**Last Updated**: January 2025  
**Tested Environments**: Ubuntu 20.04, CentOS 8, AWS, Digital Ocean, Heroku