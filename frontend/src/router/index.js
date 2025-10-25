import { defineRouter } from '#q-app/wrappers'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router'
import routes from './routes'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  // Navigation guard for authentication
  Router.beforeEach((to, from, next) => {
    console.log('=== ROUTER GUARD START ===')

    const token = localStorage.getItem('auth_token')
    const isAuthRoute = ['login', 'register'].includes(to.name)

    console.log('Router guard details:', {
      to: to.name,
      toPath: to.fullPath,
      from: from.name,
      token: token ? `exists (${token.substring(0, 10)}...)` : 'none',
      isAuthRoute,
      redirect: to.query.redirect,
    })

    console.log('Raw localStorage auth_token:', localStorage.getItem('auth_token'))
    console.log('Route name check:', to.name, 'isAuthRoute:', isAuthRoute)

    // If user is not authenticated and trying to access protected route
    if (!token && !isAuthRoute) {
      console.log('Redirecting to login - no token')

      // Allow access to family-management for testing
      if (to.name === 'family-management') {
        console.log('Allowing access to family-management for testing')
        next()
        return
      }

      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }

    // If user is authenticated and trying to access auth routes
    if (token && isAuthRoute) {
      console.log('User already authenticated, checking redirect...')

      // If there's a redirect query, use it
      if (to.query.redirect) {
        console.log('Redirecting to:', to.query.redirect)
        next(to.query.redirect)
        return
      }

      // Otherwise redirect to home
      console.log('Redirecting to home')
      next({ name: 'home' })
      return
    }

    console.log('Allowing navigation to:', to.name)
    console.log('=== ROUTER GUARD END ===')
    next()
  })

  return Router
})
