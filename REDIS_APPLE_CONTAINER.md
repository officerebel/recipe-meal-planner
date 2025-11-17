# Redis met Apple Container

## Apple Container Setup

Apple Container is de native container runtime voor macOS (geen Docker Desktop nodig).

### Check je setup

```bash
# Check of Apple Container werkt
container --version

# Of
which container
```

### Redis starten met Apple Container

```bash
# Pull Redis image
container pull redis:7-alpine

# Start Redis container
container run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Check status
container ps

# Logs bekijken
container logs redis

# Stop container
container stop redis
container rm redis
```

### Persistent data (optioneel)

```bash
# Met volume voor data persistence
container run -d \
  --name redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine redis-server --appendonly yes
```

### Backend starten

```bash
# Redis draait nu op localhost:6379
export REDIS_URL=redis://localhost:6379/0

# Start backend
./start_backend_local.sh

# Je ziet:
# ✅ Redis cache configured: redis://localhost:6379/0
```

### Redis CLI gebruiken

```bash
# Connect to Redis
container exec -it redis redis-cli

# Test commands
> ping
PONG
> set test "Hello from Apple Container"
OK
> get test
"Hello from Apple Container"
> exit
```

### Handige commands

```bash
# List running containers
container ps

# List all containers (including stopped)
container ps -a

# View logs
container logs redis
container logs -f redis  # Follow logs

# Stop and remove
container stop redis
container rm redis

# Remove image
container rmi redis:7-alpine
```

## Docker Compose equivalent

Als Apple Container `compose` ondersteunt:

```bash
# Check of compose werkt
container compose version

# Start services
container compose up -d redis

# Stop services
container compose down
```

**Note:** Apple Container is nog in development, compose support kan beperkt zijn.

## Alternatief: Homebrew Redis

Als Apple Container issues heeft, gebruik gewoon native Redis:

```bash
# Simpelste optie
brew install redis
brew services start redis

# Backend starten
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh
```

## Troubleshooting

### "container: command not found"

Apple Container is mogelijk niet geïnstalleerd of niet in PATH:

```bash
# Check installatie
ls -la /usr/local/bin/container
ls -la /opt/homebrew/bin/container

# Voeg toe aan PATH (in ~/.zshrc)
export PATH="/opt/homebrew/bin:$PATH"
```

### "Connection refused"

```bash
# Check of Redis container draait
container ps | grep redis

# Check logs
container logs redis

# Herstart container
container restart redis
```

### Poort conflict

```bash
# Check wat op poort 6379 draait
lsof -i :6379

# Stop conflicting process
kill -9 <PID>
```

## Performance

**Apple Container:**
- ✅ Native macOS integration
- ✅ Geen Docker Desktop overhead
- ✅ Optimized voor Apple Silicon
- ✅ Lightweight

**vs Docker Desktop:**
- Sneller opstarten
- Minder memory gebruik
- Betere battery life

## Mijn aanbeveling

**Als Apple Container werkt:**
```bash
container run -d --name redis -p 6379:6379 redis:7-alpine
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh
```

**Als Apple Container issues heeft:**
```bash
brew install redis
brew services start redis
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh
```

Beide werken perfect! 🚀

## Test je setup nu

```bash
# 1. Start Redis (kies één optie)
container run -d --name redis -p 6379:6379 redis:7-alpine
# OF
brew services start redis

# 2. Test Redis
redis-cli ping
# Output: PONG

# 3. Start backend
export REDIS_URL=redis://localhost:6379/0
./start_backend_local.sh

# 4. Check output
# ✅ Redis cache configured: redis://localhost:6379/0
```

Klaar! Redis draait nu op je Mac zonder Docker Desktop 🎉
