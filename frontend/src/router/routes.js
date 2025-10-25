const routes = [
  // Auth routes (no layout)
  {
    path: '/login',
    name: 'login',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('pages/RegisterPage.vue'),
  },
  {
    path: '/password-reset',
    name: 'password-reset',
    component: () => import('pages/PasswordResetPage.vue'),
  },
  // Main app routes (with layout)
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('pages/IndexPage.vue'),
        beforeEnter: (to, from, next) => {
          // Check if user is a child and redirect to child dashboard
          const user = JSON.parse(localStorage.getItem('user') || '{}')
          const familyMembers = JSON.parse(localStorage.getItem('familyMembers') || '[]')
          const currentMember = familyMembers.find(m => m.user.id === user.id)

          if (currentMember?.role === 'child') {
            next({ name: 'child-dashboard' })
          } else {
            next()
          }
        }
      },
      {
        path: 'recipes',
        name: 'recipes',
        component: () => import('pages/RecipesPage.vue'),
      },
      {
        path: 'recipes/new',
        name: 'recipe-create',
        component: () => import('pages/RecipeFormPage.vue'),
      },
      {
        path: 'recipes/import',
        name: 'recipe-import',
        component: () => import('pages/RecipeImportPage.vue'),
      },
      {
        path: 'recipes/:id',
        name: 'recipe-detail',
        component: () => import('pages/RecipeDetailPage.vue'),
        props: true,
      },
      {
        path: 'recipes/:id/edit',
        name: 'recipe-edit',
        component: () => import('pages/RecipeFormPage.vue'),
        props: true,
      },
      {
        path: 'meal-plans',
        name: 'meal-plans',
        component: () => import('pages/MealPlansPage.vue'),
      },
      {
        path: 'meal-plans/new',
        name: 'meal-plan-create',
        component: () => import('pages/MealPlanFormPage.vue'),
      },
      {
        path: 'meal-plans/:id',
        name: 'meal-plan-detail',
        component: () => import('pages/MealPlanDetailPage.vue'),
        props: true,
      },
      {
        path: 'meal-plans/:id/edit',
        name: 'meal-plan-edit',
        component: () => import('pages/MealPlanFormPage.vue'),
        props: true,
      },
      {
        path: 'shopping-lists',
        name: 'shopping-lists',
        component: () => import('pages/ShoppingListsPage.vue'),
      },
      {
        path: 'shopping-lists/:id',
        name: 'shopping-list-detail',
        component: () => import('pages/ShoppingListDetailPage.vue'),
        props: true,
      },
      {
        path: 'meal-prep',
        name: 'meal-prep',
        component: () => import('pages/MealPrepPage.vue'),
      },
      {
        path: 'categories',
        name: 'categories',
        component: () => import('pages/CategoriesPage.vue'),
      },
      {
        path: 'family-management',
        name: 'family-management',
        component: () => import('pages/FamilyManagementPage.vue'),
      },
      {
        path: 'family-dashboard',
        name: 'family-dashboard',
        component: () => import('pages/FamilyDashboardPage.vue'),
      },
      {
        path: 'child-dashboard',
        name: 'child-dashboard',
        component: () => import('pages/ChildDashboardPage.vue'),
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('pages/SettingsPage.vue'),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
