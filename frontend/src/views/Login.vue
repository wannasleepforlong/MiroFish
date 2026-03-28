<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <span class="brand-dots">
          <span class="dot dot-blue"></span>
          <span class="dot dot-dark"></span>
          <span class="dot dot-dark"></span>
          <span class="dot dot-dark"></span>
        </span>
        PROPHESIZE AI
      </div>
      <h2 class="login-title">Sign in</h2>
      <p class="login-sub">Access your simulation workspace</p>

      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="you@example.com" :disabled="loading" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="password" type="password" placeholder="••••••••" :disabled="loading"
          @keyup.enter="handleLogin" />
      </div>

      <div v-if="error" class="login-error">{{ error }}</div>

      <button class="login-btn" @click="isSignUp ? handleSignUp : handleLogin" :disabled="loading">
        <span v-if="!loading">{{ isSignUp ? 'Sign up →' : 'Sign in →' }}</span>
        <span v-else class="loading-dots">{{ isSignUp ? 'Signing up' : 'Signing in' }}</span>
      </button>
      <div class="divider"><span>or</span></div>
        <button class="google-btn" @click="handleGoogle" :disabled="loading">
        <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        Continue with Google
        </button>
        <p class="toggle-mode">
        {{ isSignUp ? 'Already have an account?' : "Don't have an account?" }}
        <a @click="isSignUp = !isSignUp">{{ isSignUp ? 'Sign in' : 'Sign up' }}</a>
        </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginWithEmail, signUpWithEmail, loginWithGoogle } from '../store/auth'

const router = useRouter()
const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref(null)

const handleLogin = async () => {
  if (!email.value || !password.value) return
  loading.value = true
  error.value = null
  try {
    await loginWithEmail(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.message || 'Login failed'
  } finally {
    loading.value = false
  }
}

const handleGoogle = async () => {
  try {
    await loginWithGoogle()
  } catch (e) {
    error.value = e.message
  }
}
const isSignUp = ref(false)
const handleSignUp = async () => {
  loading.value = true
  error.value = null
  try {
    await signUpWithEmail(email.value, password.value)
    error.value = null
    alert('Check your email for a confirmation link!')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
.login-page {
  min-height: 100vh; background: #f8fafc;
  display: flex; align-items: center; justify-content: center;
  font-family: 'DM Sans', sans-serif;
}
.login-card {
  background: white; border: 1px solid #e5e7eb;
  border-radius: 20px; padding: 44px 40px;
  width: 100%; max-width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}
.login-brand {
  display: flex; align-items: center; gap: 10px;
  font-weight: 800; font-size: 0.88rem; letter-spacing: 2px;
  color: #0a0a0a; margin-bottom: 28px;
}
.brand-dots { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; }
.dot { border-radius: 50%; display: inline-block; width: 7px; height: 7px; }
.dot.dot-blue { background: #2563EB; }
.dot.dot-dark { background: #111827; }
.login-title { font-size: 1.7rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 6px; }
.login-sub { color: #6b7280; font-size: 0.86rem; margin-bottom: 28px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: 600; color: #374151; margin-bottom: 6px; }
.form-group input {
  width: 100%; padding: 11px 14px;
  border: 1px solid #e5e7eb; border-radius: 10px;
  font-family: 'DM Sans', sans-serif; font-size: 0.9rem;
  outline: none; transition: border-color 0.2s;
}
.form-group input:focus { border-color: #2563EB; }
.login-error {
  background: #fee2e2; color: #b91c1c;
  padding: 10px 14px; border-radius: 10px;
  font-size: 0.82rem; margin-bottom: 16px;
}
.login-btn {
  width: 100%; padding: 14px;
  background: #0a0a0a; color: white; border: none;
  border-radius: 12px; font-family: 'DM Sans', sans-serif;
  font-size: 1rem; font-weight: 700; cursor: pointer;
  transition: all 0.2s; margin-top: 8px;
}

.login-btn:hover:not(:disabled) { background: #2563EB; }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.loading-dots::after { content: '...'; animation: dots 1.2s steps(4,end) infinite; }
@keyframes dots { 0%,20%{content:'.'} 40%{content:'..'} 60%,100%{content:'...'} }

.divider { display:flex; align-items:center; gap:12px; margin:16px 0; color:#9ca3af; font-size:0.78rem; }
.divider::before, .divider::after { content:''; flex:1; height:1px; background:#e5e7eb; }
.google-btn { width:100%; padding:12px; border:1px solid #e5e7eb; background:white; border-radius:12px; font-family:'DM Sans',sans-serif; font-size:0.9rem; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:10px; transition:all 0.2s; color:#374151; margin-top:8px; }
.google-btn:hover { border-color:#d1d5db; background:#f9fafb; }
.toggle-mode { text-align:center; font-size:0.82rem; color:#6b7280; margin-top:16px; }
.toggle-mode a { color:#2563EB; cursor:pointer; font-weight:600; }
</style>
