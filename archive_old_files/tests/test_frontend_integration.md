# 🧪 Frontend Recipe Sharing Integration Test

## ✅ **What's Been Added:**

### **1. Backend API Endpoints:**
- `POST /api/recipes/{id}/share-with-family/` - Share/unshare recipe
- Recipe serializers now include `is_shared_with_family` field
- Proper personal vs family recipe filtering

### **2. Frontend Service:**
- `recipeService.shareWithFamily(id, share)` - Share/unshare recipe
- `recipeService.toggleFamilySharing(id)` - Toggle sharing status
- Error handling and mobile API integration

### **3. Frontend Components:**
- `RecipeSharing.vue` - Reusable sharing component
- Integrated into `RecipeDetailPage.vue`
- Sharing button with loading states and tooltips
- Status indicators (chips)

## 🧪 **How to Test:**

### **1. Start Both Servers:**
```bash
# Terminal 1 - Backend
./start_backend_local.sh

# Terminal 2 - Frontend  
./start_frontend_local.sh
```

### **2. Test Recipe Sharing:**

1. **Navigate to a recipe detail page**
   - Go to http://localhost:9000
   - Click on "RECIPES" tab
   - Click on any recipe to view details

2. **Test sharing functionality**
   - Look for the sharing button in the header (next to Edit/Delete)
   - Click "Delen met familie" to share
   - Button should change to "Gedeeld met familie" (green)
   - Status chip should show "Gedeeld met familie"

3. **Test unsharing**
   - Click the button again to unshare
   - Button should change back to "Delen met familie" (secondary color)
   - Status chip should show "Persoonlijk recept"

4. **Test family recipes view**
   - Go to "FAMILY RECIPES" tab
   - Should show only shared recipes
   - Go to "MY RECIPES" tab
   - Should show all your recipes (shared and unshared)

### **3. Test Different User Roles:**

1. **As recipe owner:**
   - Should see sharing button
   - Should be able to toggle sharing

2. **As family member:**
   - Should see shared recipes in "FAMILY RECIPES"
   - Should NOT see sharing button on other's recipes

## 🎯 **Expected Behavior:**

### **Personal Recipes Tab:**
- Shows ALL your recipes (shared + unshared)
- Sharing button visible on your recipes
- Status indicators show sharing state

### **Family Recipes Tab:**
- Shows ONLY recipes shared by family members
- No sharing button (you can't share others' recipes)
- Only shows recipes with `is_shared_with_family: true`

### **Sharing Button States:**
- **Unshared**: "Delen met familie" (secondary color, person icon)
- **Shared**: "Gedeeld met familie" (green color, family icon)
- **Loading**: Button disabled with spinner

### **Notifications:**
- Success: "Recept gedeeld met familie" / "Recept niet meer gedeeld met familie"
- Error: Appropriate error messages for permissions, etc.

## 🔧 **API Testing:**

You can also test the API directly:

```bash
# Get auth token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Share recipe (replace TOKEN and RECIPE_ID)
curl -X POST http://localhost:8000/api/recipes/RECIPE_ID/share-with-family/ \
  -H "Authorization: Token TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"share": true}'

# Check family recipes
curl -H "Authorization: Token TOKEN" \
  "http://localhost:8000/api/recipes/?scope=family"

# Check personal recipes  
curl -H "Authorization: Token TOKEN" \
  "http://localhost:8000/api/recipes/?scope=personal"
```

## 🎉 **Success Criteria:**

- ✅ Sharing button appears on recipe detail page
- ✅ Clicking button toggles sharing state
- ✅ Success/error notifications appear
- ✅ Personal recipes show all user's recipes
- ✅ Family recipes show only shared recipes
- ✅ Status indicators update correctly
- ✅ API calls work without errors

The recipe sharing functionality is now fully integrated between backend and frontend! 🚀