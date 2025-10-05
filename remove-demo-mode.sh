#!/bin/bash

# Remove Demo Mode Script
# This script removes all demo mode functionality for production deployment

set -e

echo "🔧 Removing Demo Mode for Production"
echo "===================================="

# List of files that contain demo mode functionality
FILES=(
    "quasar-project/src/pages/IndexPage.vue"
    "quasar-project/src/pages/MealPlanDetailPage.vue"
    "quasar-project/src/pages/MealPlansPage.vue"
    "quasar-project/src/pages/RecipeImportPage.vue"
    "quasar-project/src/pages/ShoppingListsPage.vue"
    "quasar-project/src/layouts/MainLayout.vue"
)

echo "📝 Files to update:"
for file in "${FILES[@]}"; do
    echo "   - $file"
done

echo ""
read -p "Continue with removing demo mode? (y/N): " confirm

if [[ $confirm != [yY] ]]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "🔄 Processing files..."

# Create backup directory
BACKUP_DIR="demo-mode-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📄 Processing $file..."
        
        # Create backup
        cp "$file" "$BACKUP_DIR/$(basename $file)"
        
        # Remove demo mode lines (this is a simplified approach)
        # In practice, you'd want to manually edit these files
        echo "   ⚠️  Manual edit required for $file"
    else
        echo "   ❌ File not found: $file"
    fi
done

echo ""
echo "✅ Demo mode removal preparation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Manually edit the files to remove 'Enable Test Mode' buttons"
echo "   2. Remove setTestToken imports and functions"
echo "   3. Test the application without demo mode"
echo "   4. Deploy to Railway"
echo ""
echo "💾 Backups saved to: $BACKUP_DIR"
echo ""