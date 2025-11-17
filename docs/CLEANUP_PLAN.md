# Documentation Cleanup Plan

## Current Status
- **40 markdown files** in docs/ directory
- Many duplicate/outdated files
- Confusing structure

## Files to KEEP

### Core Documentation (Keep)
- ✅ `INDEX.md` - Main documentation index
- ✅ `TECHNICAL_DESIGN.md` - Technical specification
- ✅ `ENVIRONMENT_VARIABLES.md` - Config reference
- ✅ `12_FACTOR_APP.md` - Architecture
- ✅ `api/README.md` - API documentation
- ✅ `api/postman-collection.json` - Postman collection

### Optional (Keep if useful)
- `USER_GUIDE.md` - User documentation
- `DEPLOYMENT_GUIDE.md` - Deployment instructions

## Files to ARCHIVE/DELETE

### Deployment Status Files (Outdated)
- `BACKEND_DEPLOYMENT_ISSUE.md`
- `BACKEND_DEPLOYMENT_STATUS.md`
- `CRITICAL_FIXES_DEPLOYED.md`
- `DATABASE_PERSISTENCE_ISSUE.md`
- `DEPLOYMENT_BREAKTHROUGH.md`
- `DEPLOYMENT_CHECKLIST.md`
- `DEPLOYMENT_DEBUG.md`
- `DEPLOYMENT_NEXT_STEPS.md`
- `DEPLOYMENT_STATUS_UPDATE.md`
- `DEPLOYMENT_SUCCESS.md`
- `DEPLOYMENT.md`
- `FINAL_BACKEND_STATUS.md`
- `FINAL_PROJECT_STATUS.md`
- `FINAL_STATUS_MOBILE_FIXES.md`
- `PRODUCTION_DEPLOY.md`
- `RAILWAY_DEPLOYMENT.md`

### Fix/Debug Files (Outdated)
- `check-deployment.md`
- `DEBUG_INSTRUCTIONS.md`
- `DEPLOY_NOW.md`
- `FIXES_SUMMARY.md`
- `GIT_COMMIT_SUMMARY.md`
- `LATEST_CHANGES_SUMMARY.md`
- `MOBILE_PDF_FIXES.md`
- `QUICK_FIX_GUIDE.md`
- `QUICK_FIX.md`
- `RECENT_FIXES.md`
- `SHOPPING_LIST_FIXES.md`
- `STORE_DEBUG.md`

### Feature-Specific (Consolidate into TECHNICAL_DESIGN.md)
- `FAMILY_ROLE_MANAGEMENT_GUIDE.md`
- `IMAGES_AND_FAMILY_FEATURES.md`
- `IMPLEMENTATION.md`
- `PROJECT_SUMMARY.md`

### Duplicate (Remove)
- `API_DOCUMENTATION.md` (duplicate of api/README.md)
- `README.md` (duplicate of INDEX.md)

## Proposed New Structure

```
docs/
├── INDEX.md                      # Main index
├── TECHNICAL_DESIGN.md           # Complete tech spec
├── ENVIRONMENT_VARIABLES.md      # Config reference
├── 12_FACTOR_APP.md             # Architecture
├── USER_GUIDE.md                # User documentation
├── DEPLOYMENT_GUIDE.md          # Deployment instructions
├── api/
│   ├── README.md                # API docs
│   └── postman-collection.json  # Postman collection
└── archive/                     # Old docs (for reference)
    └── [old files]
```

## Action Items

1. ✅ Create INDEX.md (done)
2. ✅ Create TECHNICAL_DESIGN.md (done)
3. ✅ Create ENVIRONMENT_VARIABLES.md (done)
4. ⏳ Move old files to archive/
5. ⏳ Update INDEX.md with final structure
6. ⏳ Clean up empty directories

## Benefits

- **Clarity**: Easy to find documentation
- **Maintainability**: Less duplication
- **Onboarding**: Clear starting point (INDEX.md)
- **History**: Old docs archived, not deleted
