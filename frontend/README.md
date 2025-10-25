# Recipe Meal Planner - Frontend

Vue.js/Quasar frontend application for the Recipe Meal Planner.

## 🏗️ Technology Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Quasar Framework** - Vue.js based framework
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client

## 📁 Project Structure

```
src/
├── components/          # Reusable Vue components
├── layouts/            # Page layouts
├── pages/              # Page components
├── router/             # Vue Router configuration
├── stores/             # Pinia stores
├── services/           # API services
├── utils/              # Utility functions
├── boot/               # Quasar boot files
└── css/                # Global styles
```

## 🚀 Development Setup

### 1. Install Dependencies
```bash
npm install
# or
yarn install
```

### 2. Environment Configuration
Create `.env.local`:
```env
VUE_APP_API_BASE_URL=http://localhost:8000/api
VUE_APP_ENVIRONMENT=development
```

### 3. Start Development Server
```bash
npm run dev
# or
yarn dev
```

### 4. Build for Production
```bash
npm run build
# or
yarn build
```

## 📱 Features

### Core Pages
- **Home** - Dashboard with meal planning overview
- **Recipes** - Recipe management (personal/family views)
- **Meal Plans** - Weekly meal planning
- **Shopping Lists** - Generated and custom shopping lists
- **Settings** - User and family management

### Components
- **RecipeCard** - Recipe display component
- **MealPlanCalendar** - Weekly meal planning interface
- **ShoppingListItem** - Interactive shopping list items
- **FamilyMemberCard** - Family member management
- **ImageUpload** - Recipe image upload component

### Stores (Pinia)
- **recipes** - Recipe data management
- **mealPlanning** - Meal plans and shopping lists
- **families** - Family and member management
- **auth** - Authentication state

## 🎨 UI/UX Features

- **Responsive Design** - Mobile-first approach
- **Dark/Light Mode** - Theme switching
- **Offline Support** - PWA capabilities
- **Touch Gestures** - Mobile-friendly interactions
- **Loading States** - Smooth user experience

## 🧪 Testing

```bash
# Unit tests
npm run test:unit

# E2E tests
npm run test:e2e

# Linting
npm run lint

# Type checking
npm run type-check
```

## 📦 Build & Deployment

### Development Build
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🔧 Configuration

### Quasar Configuration
See `quasar.config.js` for:
- Build configuration
- Plugin setup
- PWA settings
- Electron configuration (if needed)

### Router Configuration
See `src/router/routes.js` for:
- Route definitions
- Navigation guards
- Meta information

## 📱 PWA Features

- **Offline Caching** - Works without internet
- **Install Prompt** - Add to home screen
- **Push Notifications** - Meal reminders
- **Background Sync** - Sync when online

## 🎯 Performance Optimization

- **Code Splitting** - Lazy-loaded routes
- **Image Optimization** - WebP format support
- **Bundle Analysis** - Webpack bundle analyzer
- **Caching Strategy** - Service worker caching