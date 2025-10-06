# 👥 Family Role Management Guide

## How to Upgrade or Downgrade Family Members

### 🔑 **Prerequisites**
- You must be logged in as an **Admin** user
- Only admins can change other members' roles

### 📍 **Where to Find Role Management**
1. **Click on "Settings" in the navigation menu** (gear icon)
2. **Select the "Family" tab** (family icon)
3. **You'll see all family members listed**

### ✏️ **How to Change a Member's Role**

#### **Step 1: Locate the Member**
- Find the family member you want to upgrade/downgrade
- You'll see their name, current role, and action buttons

#### **Step 2: Click the Edit Button**
- Click the **✏️ (edit)** button next to their name
- A dialog will open showing role options

#### **Step 3: Select New Role**
- Click on the desired role from the list:
  - **🔴 Admin**: Full access, can manage family
  - **🔵 Member**: Can create recipes and meal plans  
  - **🟢 Child**: Limited access, can view and suggest
  - **⚪ Viewer**: Read-only access

#### **Step 4: Confirm Change**
- The role change happens immediately when you click
- You'll see a success message
- The member's role badge will update

### 🎯 **Role Hierarchy (Upgrade/Downgrade)**

**Upgrade Path** ⬆️:
```
Viewer → Child → Member → Admin
```

**Downgrade Path** ⬇️:
```
Admin → Member → Child → Viewer
```

### 🛡️ **Role Permissions**

| Role | Create Recipes | Meal Planning | Family Management | Shopping Lists |
|------|---------------|---------------|-------------------|----------------|
| **Admin** | ✅ | ✅ | ✅ | ✅ |
| **Member** | ✅ | ✅ | ❌ | ✅ |
| **Child** | ❌ | View Only | ❌ | View Only |
| **Viewer** | ❌ | View Only | ❌ | View Only |

### 🚫 **Restrictions**
- **You cannot edit your own role**
- **Cannot remove the last admin** (family must have at least one admin)
- **Child users get a special simplified interface**

### 📱 **Mobile Experience**
- **Child users** are automatically redirected to a kid-friendly dashboard
- **Different navigation** based on role
- **Touch-friendly** role selection on mobile

### 🔄 **Common Use Cases**

#### **Promote a Member to Admin**
1. Go to Settings → Family
2. Find the member with "Member" role
3. Click ✏️ edit button
4. Select "Admin" role
5. ✅ They now have full family management access

#### **Create a Child Account**
1. Go to Settings → Family  
2. Click "Add Member" button
3. Fill in child's details
4. Select "Child" role
5. ✅ Child gets simplified, safe interface

#### **Demote an Admin to Member**
1. Go to Settings → Family
2. Find the admin you want to demote
3. Click ✏️ edit button  
4. Select "Member" role
5. ✅ They lose family management access but keep recipe/meal planning

### 💡 **Pro Tips**
- **Test roles** by logging in as different family members
- **Child accounts** are perfect for kids who want to suggest meals
- **Viewer accounts** are great for grandparents or guests
- **Multiple admins** are recommended for shared family management

### 🆘 **Troubleshooting**
- **Don't see edit buttons?** → You're not an admin
- **Can't change someone's role?** → Check if you're trying to edit yourself
- **Role not updating?** → Refresh the page or check your internet connection

---

**🎉 Your family role management is now fully functional!**