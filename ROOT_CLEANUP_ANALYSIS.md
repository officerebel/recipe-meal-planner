# Root Directory Cleanup Analysis

## Files to KEEP (Useful)

### Essential
- ✅ `README.md` - Main project documentation
- ✅ `manage.py` - Django management (backend)
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` - Git ignore rules
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Docker configuration
- ✅ `railway.json` - Railway deployment config

### Development Scripts (Keep)
- ✅ `start_backend_local.sh` - Start backend locally
- ✅ `start_frontend_local.sh` - Start frontend locally
- ✅ `start_local_dev.sh` - Start both servers
- ✅ `start_servers_instructions.md` - Dev server instructions

### Deployment (Keep)
- ✅ `start.sh` - Production start script

## Files to ARCHIVE (Old/Test)

### Test Scripts (Old - superseded by proper tests)
- ❌ `test_api_import.py` - Old API test
- ❌ `test_auth_final.py` - Old auth test
- ❌ `test_auth_simple.py` - Old auth test
- ❌ `test_duplicates.py` - Old duplicate test
- ❌ `test_image_processing.py` - Old image test
- ❌ `test_import_endpoint.py` - Old import test
- ❌ `test_ocr_functionality.py` - Old OCR test
- ❌ `test_password_change.py` - Old password test
- ❌ `test_password_reset.py` - Old password test
- ❌ `test_production_password_reset.py` - Old test
- ❌ `test_recipe_sharing.py` - Old sharing test
- ❌ `test_recipe_update.py` - Old update test

**Reason:** These are superseded by proper Django tests in `backend/*/tests.py`

### Documentation (Old)
- ❌ `test_frontend_integration.md` - Old integration doc

**Reason:** Superseded by docs/TECHNICAL_DESIGN.md

### Other Files
- ❌ `generate-version.js` - Duplicate (exists in frontend/)
- ❌ `schema.yml` - Old schema file
- ❌ `nixpacks.toml` - Old build config
- ❌ `Procfile` - Old Heroku config

## Recommended Actions

### 1. Archive Test Scripts
```bash
mkdir -p archive_old_files/tests
mv test_*.py archive_old_files/tests/
mv test_*.md archive_old_files/tests/
```

### 2. Archive Old Configs
```bash
mv schema.yml nixpacks.toml Procfile archive_old_files/ 2>/dev/null || true
```

### 3. Remove Duplicates
```bash
# generate-version.js exists in frontend/
rm generate-version.js 2>/dev/null || true
```

## Final Root Structure

```
food_app/
├── README.md                      # Main docs
├── .env.example                   # Config template
├── .gitignore                     # Git ignore
├── requirements.txt               # Python deps
├── manage.py                      # Django CLI
├── Dockerfile                     # Docker config
├── railway.json                   # Railway config
├── start.sh                       # Production start
├── start_backend_local.sh         # Dev: backend
├── start_frontend_local.sh        # Dev: frontend
├── start_local_dev.sh            # Dev: both
├── start_servers_instructions.md  # Dev instructions
├── backend/                       # Django backend
├── frontend/                      # Quasar frontend
├── docs/                          # Documentation
└── archive_old_files/            # Archived files
    ├── tests/                    # Old test scripts
    └── [other old files]
```

## Benefits

- **Cleaner root** - Only essential files
- **Clear purpose** - Each file has a role
- **Easy onboarding** - New devs see what matters
- **History preserved** - Old files archived
