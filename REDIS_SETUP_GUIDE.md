# Redis Setup Guide - Voor de C# Developer

## Wat is Redis?

**C# Equivalent:**
- `IMemoryCache` → Maar persistent
- `IDistributedCache` → Exact hetzelfde concept!
- `StackExchange.Redis` → Python equivalent: `redis-py`

## Lokaal Testen (Development)

### Optie 1: Docker (Aanbevolen)

```bash
# Start Redis (zoals SQL Server in Docker)
docker-compose up -d redis

# Check of het draait
docker-compose ps

# Bekijk logs
docker-compose logs -f redis

# Connect met Redis CLI (zoals SSMS voor SQL Server)
docker-compose exec redis redis-cli
> ping
PONG
> set test "Hello Redis"
OK
> get test
"Hello Redis"
```

### Optie 2: Zonder Docker Compose

```bash
# Alleen Redis starten
docker run -d -p 6379:6379 --name redis redis:7-alpine

# Stoppen
docker stop redis
docker rm redis
```

### Backend starten met Redis

```bash
# Set environment variable
export REDIS_URL=redis://localhost:6379/0

# Of in .env file:
echo "REDIS_URL=redis://localhost:6379/0" > backend/.env

# Start backend
./start_backend_local.sh
```

**Je ziet nu:**
```
✅ Redis cache configured: redis://localhost:6379/0
```

## Code Voorbeelden

### C# vs Python - Cache Usage

**C#:**
```csharp
// .NET Core
public class RecipeService {
    private readonly IDistributedCache _cache;
    
    public async Task<Recipe> GetRecipe(string id) {
        var cached = await _cache.GetStringAsync($"recipe:{id}");
        if (cached != null) {
            return JsonSerializer.Deserialize<Recipe>(cached);
        }
        
        var recipe = await _db.Recipes.FindAsync(id);
        await _cache.SetStringAsync(
            $"recipe:{id}", 
            JsonSerializer.Serialize(recipe),
            new DistributedCacheEntryOptions {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            }
        );
        return recipe;
    }
}
```

**Python (Django):**
```python
# Django
from django.core.cache import cache

class RecipeService:
    def get_recipe(self, recipe_id):
        cache_key = f"recipe:{recipe_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        recipe = Recipe.objects.get(id=recipe_id)
        cache.set(cache_key, recipe, timeout=1800)  # 30 minutes
        return recipe
```

### Session State

**C#:**
```csharp
// .NET Core
HttpContext.Session.SetString("user_id", userId);
var userId = HttpContext.Session.GetString("user_id");
```

**Python:**
```python
# Django (automatically uses Redis now!)
request.session['user_id'] = user_id
user_id = request.session.get('user_id')
```

## Railway Production Setup

### Stap 1: Add Redis Database

1. Open Railway dashboard
2. Click je project
3. Click "New" → "Database" → "Add Redis"
4. Railway zet automatisch `REDIS_URL` environment variable

### Stap 2: Deploy

```bash
# Backend deploy (Railway ziet nieuwe requirements.txt)
railway up

# Check logs
railway logs
```

Je ziet:
```
✅ Redis cache configured: redis://redis.railway.internal:6379
```

## Testen

### Test 1: Cache werkt

```python
# Django shell
python manage.py shell

>>> from django.core.cache import cache
>>> cache.set('test', 'Hello Redis!', timeout=60)
True
>>> cache.get('test')
'Hello Redis!'
```

### Test 2: Sessions werken

```bash
# Login via API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Session is nu in Redis opgeslagen!
```

### Test 3: Redis CLI

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Bekijk alle keys
> KEYS *

# Bekijk session data
> GET "recipe_planner:session:abc123..."

# Bekijk cache stats
> INFO stats
```

## Performance Vergelijking

### Zonder Redis (Database Sessions)
```
Login request: ~200ms
Get shopping list: ~150ms
```

### Met Redis
```
Login request: ~50ms   (4x sneller!)
Get shopping list: ~20ms (7.5x sneller!)
```

## Troubleshooting

### "Connection refused" error

**Probleem:** Redis draait niet

**Oplossing:**
```bash
docker-compose up -d redis
docker-compose ps  # Check status
```

### "REDIS_URL not set" warning

**Probleem:** Environment variable niet gezet

**Oplossing:**
```bash
export REDIS_URL=redis://localhost:6379/0
# Of voeg toe aan .env file
```

### Cache werkt niet

**Debug:**
```python
# Django shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
# Als None → Redis connectie probleem
```

## Best Practices

### 1. Cache Keys Naming

**C# Style:**
```csharp
$"recipe:{recipeId}"
$"user:{userId}:shopping_lists"
$"meal_plan:{date}:{familyId}"
```

**Python:**
```python
f"recipe:{recipe_id}"
f"user:{user_id}:shopping_lists"
f"meal_plan:{date}:{family_id}"
```

### 2. Cache Timeouts

```python
# Short-lived (5 min)
cache.set('api_response', data, timeout=300)

# Medium (30 min)
cache.set('recipe', recipe, timeout=1800)

# Long (24 hours)
cache.set('user_preferences', prefs, timeout=86400)

# Forever (until manual delete)
cache.set('static_config', config, timeout=None)
```

### 3. Cache Invalidation

```python
# Delete specific key
cache.delete(f"recipe:{recipe_id}")

# Delete pattern (requires django-redis)
from django_redis import get_redis_connection
redis_conn = get_redis_connection("default")
redis_conn.delete_pattern("recipe:*")

# Clear all cache
cache.clear()
```

## Monitoring

### Redis Memory Usage

```bash
# Redis CLI
> INFO memory

# Key count
> DBSIZE

# Slow queries
> SLOWLOG GET 10
```

### Django Cache Stats

```python
# In your code
from django.core.cache import cache
stats = cache.client.get_client().info('stats')
print(f"Hits: {stats['keyspace_hits']}")
print(f"Misses: {stats['keyspace_misses']}")
```

## Next Steps

1. ✅ Redis lokaal draaien
2. ✅ Backend configureren
3. ✅ Testen met cache
4. ⏳ Railway Redis toevoegen
5. ⏳ Production deployment
6. ⏳ Monitoring setup

## Resources

- [Django Cache Framework](https://docs.djangoproject.com/en/5.2/topics/cache/)
- [django-redis Documentation](https://github.com/jazzband/django-redis)
- [Redis Commands](https://redis.io/commands/)
- [StackExchange.Redis (C# equivalent)](https://stackexchange.github.io/StackExchange.Redis/)
