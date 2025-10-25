<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Header -->
      <div class="login-header">
        <q-icon name="restaurant" size="64px" color="primary" />
        <h1 class="text-h4 text-primary q-mt-sm">Recipe Meal Planner</h1>
        <p class="text-subtitle1 text-grey-7">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <q-card class="login-card">
        <q-card-section class="q-pa-lg">
          <q-form @submit.prevent="handleLogin" class="q-gutter-md">
            <!-- Email Field -->
            <q-input
              v-model="email"
              type="email"
              label="Email Address"
              outlined
              required
            >
              <template v-slot:prepend>
                <q-icon name="email" />
              </template>
            </q-input>

            <!-- Password Field -->
            <q-input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              outlined
              required
            >
              <template v-slot:prepend>
                <q-icon name="lock" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="showPassword = !showPassword"
                />
              </template>
            </q-input>

            <!-- Remember Me -->
            <q-checkbox
              v-model="rememberMe"
              label="Remember me"
              color="primary"
            />

            <!-- Error Message -->
            <q-banner v-if="error" class="bg-negative text-white">
              <template v-slot:avatar>
                <q-icon name="error" />
              </template>
              {{ error }}
            </q-banner>

            <!-- Submit Button -->
            <q-btn
              type="submit"
              color="primary"
              label="Sign In"
              class="full-width q-mt-md"
              size="lg"
              :loading="loading"
            />

            <!-- Demo Login Button (Development Only) -->
            <q-btn
              v-if="isDevelopment"
              color="secondary"
              label="Demo Login"
              class="full-width q-mt-sm"
              size="md"
              outline
              @click="demoLogin"
              :loading="loading"
            />

            <!-- Forgot Password Link -->
            <div class="text-center q-mt-md">
              <q-btn
                flat
                color="grey-7"
                label="Forgot Password?"
                @click="goToPasswordReset"
                size="sm"
              />
            </div>

            <!-- Register Link -->
            <div class="text-center q-mt-md">
              <p class="text-body2 text-grey-7">
                Don't have an account?
              </p>
              <q-btn
                flat
                color="primary"
                label="Create Account"
                @click="goToRegister"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Development flag
const isDevelopment = process.env.NODE_ENV === 'development'

// Form state
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Simple notification function
const showMessage = (message) => {
  console.log(message)
  // Simple alert for now - can be replaced with better notification system
  setTimeout(() => alert(message), 100)
}

// Methods
const handleLogin = async () => {
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }

  loading.value = true
  error.value = ''

  try {
    console.log('Starting login process...')

    // Use the configured API base URL
    const baseURL = process.env.NODE_ENV === 'production'
      ? 'https://proud-mercy-production.up.railway.app/api'
      : 'http://localhost:8000/api'

    const response = await fetch(`${baseURL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      console.log('Login successful:', data)

      // Store the token
      localStorage.setItem('auth_token', data.token)

      showMessage('Welcome back!')

      // Redirect to home or intended page
      const redirectTo = router.currentRoute.value.query.redirect || '/'
      router.push(redirectTo)

    } else {
      const data = await response.json()
      console.error('Login failed:', data)

      if (data.errors && data.errors.non_field_errors) {
        error.value = data.errors.non_field_errors[0]
      } else {
        error.value = 'Invalid email or password'
      }
    }

  } catch (loginError) {
    console.error('Login error:', loginError)

    // Show proper error message instead of demo mode
    if (loginError.name === 'TypeError' && loginError.message.includes('fetch')) {
      error.value = 'Unable to connect to server. Please check your internet connection and try again.'
    } else {
      error.value = 'Login failed. Please check your credentials and try again.'
    }

  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push({ name: 'register' })
}

const goToPasswordReset = () => {
  router.push({ name: 'password-reset' })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cursor-pointer {
  cursor: pointer;
}

h1 {
  margin: 0.5rem 0;
}

p {
  margin: 0;
}
</style>
