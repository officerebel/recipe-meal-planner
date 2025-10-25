<template>
  <div class="register-page">
    <div class="register-container">
      <!-- Header -->
      <div class="register-header">
        <q-icon name="restaurant" size="64px" color="primary" />
        <h1 class="text-h4 text-primary q-mt-sm">Recipe Meal Planner</h1>
        <p class="text-subtitle1 text-grey-7">Create your account</p>
      </div>

      <!-- Registration Form -->
      <q-card class="register-card">
        <q-card-section class="q-pa-lg">
          <q-form @submit.prevent="handleRegister" class="q-gutter-md">
            <!-- First Name -->
            <q-input
              v-model="firstName"
              label="First Name"
              outlined
              required
            >
              <template v-slot:prepend>
                <q-icon name="person" />
              </template>
            </q-input>

            <!-- Last Name -->
            <q-input
              v-model="lastName"
              label="Last Name"
              outlined
              required
            >
              <template v-slot:prepend>
                <q-icon name="person_outline" />
              </template>
            </q-input>

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

            <!-- Confirm Password Field -->
            <q-input
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              label="Confirm Password"
              outlined
              required
            >
              <template v-slot:prepend>
                <q-icon name="lock_outline" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="showConfirmPassword ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="showConfirmPassword = !showConfirmPassword"
                />
              </template>
            </q-input>

            <!-- Terms and Conditions -->
            <q-checkbox
              v-model="acceptTerms"
              color="primary"
            >
              <div class="text-body2">
                I agree to the
                <a href="#" class="text-primary">Terms of Service</a>
                and
                <a href="#" class="text-primary">Privacy Policy</a>
              </div>
            </q-checkbox>

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
              label="Create Account"
              class="full-width q-mt-md"
              size="lg"
              :loading="loading"
            />

            <!-- Login Link -->
            <div class="text-center q-mt-md">
              <p class="text-body2 text-grey-7">
                Already have an account?
              </p>
              <q-btn
                flat
                color="primary"
                label="Sign In"
                @click="goToLogin"
              />
            </div>

            <!-- Settings Link -->
            <div class="text-center q-mt-sm">
              <q-btn
                flat
                color="grey-7"
                label="App Settings"
                @click="goToSettings"
                size="sm"
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

// Form state
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Simple notification function
const showMessage = (message) => {
  console.log(message)
  // Simple alert for now - can be replaced with better notification system
  setTimeout(() => alert(message), 100)
}

// Methods
const handleRegister = async () => {
  console.log('Registration attempt:', {
    firstName: firstName.value,
    lastName: lastName.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
    acceptTerms: acceptTerms.value
  })

  // Clear previous errors
  error.value = ''

  // Basic validation
  if (!firstName.value || !lastName.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    console.log('Validation failed: missing fields')
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    console.log('Validation failed: passwords do not match')
    return
  }

  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    console.log('Validation failed: password too short')
    return
  }

  if (!acceptTerms.value) {
    error.value = 'You must accept the terms and conditions'
    console.log('Validation failed: terms not accepted')
    return
  }

  if (!/.+@.+\..+/.test(email.value)) {
    error.value = 'Please enter a valid email address'
    console.log('Validation failed: invalid email')
    return
  }

  loading.value = true

  console.log('Starting registration process...')

  try {
    console.log('Attempting to register with Django API...')

    // Use the configured API base URL
    const baseURL = process.env.NODE_ENV === 'production'
      ? 'https://proud-mercy-production.up.railway.app/api'
      : 'http://localhost:8000/api'

    const response = await fetch(`${baseURL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        first_name: firstName.value,
        last_name: lastName.value,
        email: email.value,
        password: password.value,
        password_confirm: confirmPassword.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      console.log('Registration successful:', data)

      // Store the token
      if (data.token) {
        localStorage.setItem('auth_token', data.token)
      }

      showMessage(`Welcome ${firstName.value}! Account created successfully!`)

      // Redirect to home
      router.push('/')

    } else {
      const data = await response.json()
      console.error('Registration failed with status:', response.status, data)

      // Handle specific field errors
      if (data.errors) {
        const errors = data.errors
        if (errors.email && errors.email[0]) {
          error.value = errors.email[0]
        } else if (errors.password && errors.password[0]) {
          error.value = errors.password[0]
        } else {
          error.value = 'Registration failed. Please check your information.'
        }
      } else {
        error.value = data.error || 'Registration failed. Please try again.'
      }
    }

  } catch (registrationError) {
    console.error('Registration error:', registrationError)

    // Show proper error message instead of demo mode
    if (registrationError.name === 'TypeError' && registrationError.message.includes('fetch')) {
      error.value = 'Unable to connect to server. Please check your internet connection and try again.'
    } else {
      error.value = 'Registration failed. Please try again.'
    }

  } finally {
    loading.value = false
    console.log('Registration process completed')
  }
}

const goToLogin = () => {
  router.push({ name: 'login' })
}

const goToSettings = () => {
  router.push({ name: 'settings' })
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 450px;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-card {
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

a {
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
