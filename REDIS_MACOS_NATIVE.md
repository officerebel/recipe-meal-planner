# Redis op macOS - Native (Zonder Docker Desktop)

## Optie 1: Homebrew (Aanbevolen - Simpelst)

### Installatie
```bash
# Installeer Redis
brew install redis

# Start Redis als service (draait altijd op achtergrond)
brew services start redis

# Of: Start Redis handmatig (stopt bij terminal sluiten)
redis-server /opt/homebrew/etc/redis.conf
```

### Check of het werkt
```bash
# Test connectie
redis-cli ping
# Output: PONG

# Set/Get test
redis-cli set test "Hello from macOS"
redis-cli get test
```

### Backend starten
```bash
# Redis draait al op localhost:6379
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh
```

### Stoppen
```bash
# Stop Redis service
brew services stop redis

# Of kill handmatig
pkill redis-server
```

---

## Optie 2: Podman (Docker Desktop alternatief)

### Setup Podman
```bash
# Installeer Podman
brew install podman

# Initialiseer Podman machine
podman machine init
podman machine start

# Check status
podman machine list
```

### Redis starten met Podman
```bash
# Start Redis container
podman run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Check status
podman ps

# Logs bekijken
podman logs redis

# Stoppen
podman stop redis
podman rm redis
```

### Podman Compose
```bash
# Installeer podman-compose
brew install podman-compose

# Gebruik docker-compose.yml
podman-compose up -d redis

# Stoppen
podman-compose down
```

---

## Optie 3: Colima (Docker Desktop alternatief)

### Setup Colima
```bash
# Installeer Colima
brew install colima docker

# Start Colima
colima start

# Check status
colima status
```

### Redis starten met Colima
```bash
# Nu werkt docker command gewoon!
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Of met docker-compose
docker-compose up -d redis
```

---

## Vergelijking

| Methode | Voordelen | Nadelen |
|---------|-----------|---------|
| **Homebrew** | ✅ Simpelst<br>✅ Native performance<br>✅ Geen containers | ❌ Alleen Redis<br>❌ Geen PostgreSQL |
| **Podman** | ✅ Gratis<br>✅ Rootless<br>✅ Docker compatible | ⚠️ Iets langzamer opstarten |
| **Colima** | ✅ Gratis<br>✅ 100% Docker compatible<br>✅ Lightweight | ⚠️ Extra VM layer |

## Mijn Aanbeveling voor jou

**Development:** Homebrew Redis (simpelst)
```bash
brew install redis
brew services start redis
```

**Als je ook PostgreSQL wilt:** Colima
```bash
brew install colima docker
colima start
docker-compose up -d
```

## Test je setup

```bash
# 1. Check Redis draait
redis-cli ping

# 2. Start backend
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh

# 3. Je ziet:
# ✅ Redis cache configured: redis://localhost:6379/0
```

## Troubleshooting

### "Connection refused"
```bash
# Check of Redis draait
brew services list | grep redis

# Of
ps aux | grep redis

# Herstart
brew services restart redis
```

### "redis-cli not found"
```bash
# Installeer Redis CLI
brew install redis
```

### Poort al in gebruik
```bash
# Check wat op poort 6379 draait
lsof -i :6379

# Kill process
kill -9 <PID>
```

## Performance

**Homebrew Redis (Native):**
- Snelste optie
- Geen VM overhead
- Direct op macOS

**Podman/Colima:**
- Iets langzamer (VM layer)
- Maar nog steeds snel genoeg voor development

## Wat ik zou doen

```bash
# Simpel en snel:
brew install redis
brew services start redis

# Backend starten
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh

# Done! 🚀
```
