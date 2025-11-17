# Store Debug Instructions

## 🔍 Debug Store State

### In Browser Console, run these commands:

1. **Check current store state:**
```javascript
// Access the store (you might need to find the right way to access it)
console.log('Shopping lists in store:', window.__VUE_DEVTOOLS_GLOBAL_HOOK__)
```

2. **Check if shopping lists are reactive:**
```javascript
// In the shopping lists page, check the computed property
console.log('Computed shopping lists:', this.shoppingLists)
```

3. **Manual store update test:**
```javascript
// Try manually updating a shopping list title
const store = /* get store reference */
store.updateShoppingListTitle('your-shopping-list-id', 'Test Title')
```

## 🎯 Expected Behavior:

1. **Title update in detail page** ✅ Working
2. **Store gets updated** ❓ Need to verify
3. **Overview page reflects change** ❌ Not working
4. **Change persists on refresh** ❓ Need to test

## 🔧 Possible Issues:

1. **Type mismatch** - Shopping list ID might be string vs number
2. **Store not found** - Shopping list might not exist in store
3. **Reactivity issue** - Overview page not watching store changes
4. **Cache issue** - Old data being cached somewhere

## 🚀 Quick Test:

1. Open browser console
2. Edit shopping list title
3. Look for these logs:
   ```
   Updating shopping list title: {shoppingListId: "...", newTitle: "..."}
   Available shopping lists: [{id: "...", name: "..."}, ...]
   Shopping list ID type: string
   Store shopping list IDs: [{id: "...", type: "string"}, ...]
   Found shopping list, updating title from: "..." to: "..."
   ```
4. Check if "Found shopping list" appears or "Shopping list not found"