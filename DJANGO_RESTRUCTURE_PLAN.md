# Django Restructure Plan

## Current Situation (WRONG)

```
food_app/
├── recipe_meal_planner/     ← Django project (root)
├── recipes/                 ← Django app (root)
├── meal_planning/           ← Django app (root)
├── families/                ← Django app (root)
├── authentication/          ← Django app (root)
├── manage.py                ← Django CLI (root)
├── db.sqlite3               ← Database (root)
├── media/                   ← Media files (root)
├── static/                  ← Static files (root)
└── backend/                 ← Has DUPLICATES!
    ├── recipe_meal_planner/
    ├── recipes/
    ├── meal_planning/
    ├── families/
    ├── authentication/
    └── manage.py
```

## Target Structure (CORRECT)

```
food_app/
├── manage.py                ← Symlink to backend/manage.py
├── backend/
│   ├── recipe_meal_planner/ ← Django project
│   ├── recipes/             ← Django app
│   ├── meal_planning/       ← Django app
│   ├── families/            ← Django app
│   ├── authentication/      ← Django app
│   ├── manage.py            ← Django CLI
│   ├── db.sqlite3           ← Database
│   ├── media/               ← Media files
│   ├── static/              ← Static files
│   └── requirements.txt     ← Python deps
├── frontend/
└── docs/
```

## Action Plan

### Step 1: Check which is the "real" version
- Compare backend/ vs root versions
- Identify which has latest code

### Step 2: Move everything to backend/
```bash
# If root has latest code:
mv recipe_meal_planner backend/
mv recipes backend/
mv meal_planning backend/
mv families backend/
mv authentication backend/
mv db.sqlite3 backend/
mv media backend/
mv static backend/
```

### Step 3: Update paths
- Update manage.py paths
- Update settings.py paths
- Update imports

### Step 4: Create symlink for convenience
```bash
ln -s backend/manage.py manage.py
```

### Step 5: Clean up
- Remove old duplicates
- Update .gitignore
- Test everything works

## Risks

- ⚠️ Breaking imports
- ⚠️ Database path changes
- ⚠️ Media file paths
- ⚠️ Railway deployment config

## Testing Checklist

- [ ] Backend starts: `python backend/manage.py runserver`
- [ ] Tests pass: `python backend/manage.py test`
- [ ] Admin works: http://localhost:8000/admin
- [ ] API works: http://localhost:8000/api/
- [ ] Media files accessible
- [ ] Frontend connects to backend
