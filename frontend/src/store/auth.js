import { reactive } from 'vue'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Validate before creating client
if (!supabaseUrl) {
  throw new Error('Missing VITE_SUPABASE_URL in environment')
}
if (!supabaseAnonKey) {
  throw new Error('Missing VITE_SUPABASE_ANON_KEY in environment')
}

const supabase = createClient(supabaseUrl, supabaseAnonKey)

// ── Helper functions for localStorage ──
const saveUserToStorage = (user) => {
  if (user) {
    localStorage.setItem('prophesize_user', JSON.stringify({
      id: user.id,
      email: user.email,
      user_metadata: user.user_metadata
    }))
  } else {
    localStorage.removeItem('prophesize_user')
  }
}

const loadUserFromStorage = () => {
  const stored = localStorage.getItem('prophesize_user')
  return stored ? JSON.parse(stored) : null
}

const state = reactive({
  user: null,
  loading: true
})

export async function initAuth() {
  // First, check if user was stored in localStorage
  const storedUser = loadUserFromStorage()
  if (storedUser) {
    state.user = storedUser
  }

  // Then sync with Supabase session
  const { data } = await supabase.auth.getSession()
  state.user = data.session?.user ?? null
  
  // Save to localStorage
  saveUserToStorage(state.user)
  
  state.loading = false

  // Listen for auth changes
  supabase.auth.onAuthStateChange((_event, session) => {
    state.user = session?.user ?? null
    saveUserToStorage(state.user)
  })
}

export async function loginWithEmail(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password })
  if (error) throw error
  state.user = data.user
  saveUserToStorage(state.user)
  return data.user
}

export async function logout() {
  await supabase.auth.signOut()
  state.user = null
  saveUserToStorage(null)
}

export function getUser() { return state.user }
export function getUserId() { return state.user?.id ?? null }

export async function loginWithGoogle() {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: window.location.origin }
  })
  if (error) throw error
}

export async function signUpWithEmail(email, password) {
  const { data, error } = await supabase.auth.signUp({ email, password })
  if (error) throw error
  return data.user
}

export default state
