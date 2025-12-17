<template>
  <div class="password-reset-page">
    <div class="password-reset-container">
      <!-- Header -->
      <div class="password-reset-header">
        <q-icon name="lock_reset" size="64px" color="primary" />
        <h1 class="text-h4 text-primary q-mt-sm">Reset Password</h1>
        <p class="text-subtitle1 text-grey-7">Enter your email to receive reset instructions</p>
      </div>

      <!-- Password Reset Form -->
      <q-card class="password-reset-card">
        <q-card-section class="q-pa-lg">
          <q-form @submit.prevent="handlePasswordReset" class="q-gutter-md">
            <!-- Email Field -->
            <q-input
              v-model="email"
              type="email"
              label="Email Address"
              outlined
              required
              :rules="[
                val => !!val || 'Email is required',
                val => /.+@.+\..+/.test(val) || 'Please enter a valid email'
              ]"
            >
              <template v-slot:prepend>
                <q-icon name="email" />
              </template>
            </q-input>

            <!-- Instructions -->
            <q-banner class="bg-info text-white">
              <template v-slot:avatar>
                <q-icon name="info" />
              </template>
              <div>
                <strong>What happens next:</strong>
                <ul class="q-ma-none q-pl-md">
                  <li>We'll send a reset link to your email</li>
                  <li>Click the link to create a new password</li>
                  <li>The link expires in 24 hours</li>
                </ul>
              </div>
            </q-banner>

            <!-- Error Message -->
            <q-banner v-if="error" class="bg-negative text-white">
              <template v-slot:avatar>
                <q-icon name="error" />
              </template>
              {{ error }}
            </q-banner>

            <!-- Success Message -->
            <q-banner v-if="success" class="bg-positive text-white">
              <template v-slot:avatar>
                <q-icon name="check_circle" />
              </template>
              {{ success }}
            </q-banner>

            <!-- Submit Button -->
            <q-btn
              type="submit"
              color="primary"
              label="Send Reset Link"
              class="full-width q-mt-md"
              size="lg"
              :loading="loading"
              :disable="!email || !/.+@.+\..+/.test(email)"
            />

            <!-- Back to Login -->
            <div class="text-center q-mt-md">
              <p class="text-body2 text-grey-7">
                Remember your password?
              </p>
              <q-btn
                flat
                color="primary"
                label="Back to Login"
                @click="goToLogin"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>

      <!-- Additional Help -->
      <q-card class="q-mt-md">
        <q-card-section>
          <div class="text-h6 q-mb-md">Need Help?</div>
          <q-list>
            <q-item>
              <q-item-section avatar>
                <q-icon name="help" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Can't access your email?</q-item-label>
                <q-item-label caption>Contact support for assistance</q-item-label>
              </q-item-section>
            </q-item>
            <q-item>
              <q-item-section avatar>
                <q-icon name="security" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Account Security</q-item-label>
                <q-item-label caption>Learn about keeping your account safe</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
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
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

// Simple notification function
const showMessage = (message) => {
  console.log(message)
  setTimeout(() => alert(message), 100)
}

// Methods
const handlePasswordReset = async () => {
  if (!email.value || !/.+@.+\..+/.test(email.value)) {
    error.value = 'Please enter a valid email address'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    console.log('Sending password reset email to:', email.value)

    // Use the configured API base URL
    const baseURL = process.env.NODE_ENV === 'production'
      ? '/api'
      : 'http://localhost:8000/api'

    const response = await fetch(`${baseURL}/auth/password-reset/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        email: email.value
      })
    })

    if (response.ok) {
      const data = await response.json()
      console.log('Password reset successful:', data)

      success.value = `Password reset instructions have been sent to ${email.value}. Please check your inbox and spam folder.`

      showMessage('Password reset email sent!')

    } else {
      const data = await response.json()
      console.error('Password reset failed:', data)

      if (data.error) {
        error.value = data.error
      } else {
        error.value = 'Failed to send reset email. Please try again.'
      }
    }

  } catch (resetError) {
    console.error('Password reset error:', resetError)

    // Show proper error message instead of demo mode
    if (resetError.name === 'TypeError' && resetError.message.includes('fetch')) {
      error.value = 'Unable to connect to server. Please check your internet connection and try again.'
    } else {
      error.value = 'Password reset failed. Please try again.'
    }

  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push({ name: 'login' })
}
</script>

<style scoped>
.password-reset-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.password-reset-container {
  width: 100%;
  max-width: 500px;
}

.password-reset-header {
  text-align: center;
  margin-bottom: 2rem;
}

.password-reset-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  margin: 0.5rem 0;
}

p {
  margin: 0;
}

ul {
  margin: 0;
  padding-left: 1rem;
}
</style>
