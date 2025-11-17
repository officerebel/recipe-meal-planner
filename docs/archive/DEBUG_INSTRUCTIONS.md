# Debug Instructions

## 🔍 Title Change Issue

### Steps to Debug:
1. **Open browser console** (F12 → Console tab)
2. **Go to any shopping list detail page**
3. **Click edit icon** next to title
4. **Type new title** (e.g., "My Custom List")
5. **Press Enter** or click green checkmark
6. **Watch console for logs**:
   ```
   Updating shopping list title: {shoppingListId: "...", newTitle: "My Custom List"}
   Available shopping lists: [{id: "...", name: "..."}, ...]
   Found shopping list, updating title from: "old title" to: "My Custom List"
   Updated shopping list ... title to: My Custom List
   ```
7. **Navigate back** to shopping lists page
8. **Check if title is updated**

### If Title Not Updating:
- Check if console shows "Shopping list not found in store"
- Verify the shopping list ID matches
- Check if the store has the shopping list loaded

## 🔍 Preview Recipe Issue

### Steps to Debug:
1. **Open browser console** (F12 → Console tab)
2. **Go to Recipes → Import from PDF**
3. **Upload any file** (PDF, text, image - anything)
4. **Click "Preview Recipe" button**
5. **Watch console for logs**:
   ```
   Previewing recipe from PDF: filename.pdf
   Parsing mode: auto
   Expected language: nl
   Authentication token available: true/false
   PDF preview endpoint failed, using mock data: [error message]
   Recipe preview received: {title: "Klassieke Spaghetti Carbonara", ...}
   ```
6. **Should see preview section** appear below with Dutch recipe

### If Preview Not Working:
- Check if console shows any errors
- Verify mock recipe data is being returned
- Check if previewData.value is being set
- Look for validation errors

## 🎯 Quick Fixes to Try:

### For Title Issue:
1. **Refresh the page** and try again
2. **Enable Test Mode** (hamburger menu → user icon → Enable Test Mode)
3. **Check browser network tab** for API calls

### For Preview Issue:
1. **Enable Test Mode first** (hamburger menu → user icon → Enable Test Mode)
2. **Try different file types** (PDF, TXT, JPG)
3. **Check if preview section appears** below the upload area
4. **Look for validation warnings** in the preview

## 🚀 Expected Results:

### Title Change:
- ✅ Console shows update logs
- ✅ Success notification appears
- ✅ Title updates in detail page
- ✅ Title updates in overview page

### Preview Recipe:
- ✅ Console shows preview logs
- ✅ Mock Dutch recipe appears
- ✅ Validation section shows quality score
- ✅ Can save previewed recipe

If either feature still doesn't work after these steps, check the console for specific error messages and let me know what you see!