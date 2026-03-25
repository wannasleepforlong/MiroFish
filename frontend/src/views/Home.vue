<template>
  <div class="home-container">

    <!-- ── NAVBAR ── -->
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-dots">
          <span class="dot dot-blue"></span>
          <span class="dot dot-dark"></span>
          <span class="dot dot-dark"></span>
          <span class="dot dot-dark"></span>
        </span>
        PROPHESIZE AI
      </div>
      <div class="nav-center">
        <a class="nav-link" @click.prevent="scrollTo('features')">Features</a>
        <a class="nav-link" @click.prevent="scrollTo('workflow')">Workflow</a>
        <a class="nav-link" @click.prevent="scrollTo('simulation')">Simulation</a>
        <a class="nav-link" @click.prevent="scrollTo('history')">History</a>
      </div>
      <div class="nav-right">
      </div>
    </nav>

    <!-- ── HERO ── -->
    <section class="hero-section" id="features">

      <!-- TOP-LEFT: yellow sticky note with pin -->
      <div class="float-card sticky-note float-anim-1">
        <div class="pin">
          <div class="pin-head"></div>
          <div class="pin-needle"></div>
        </div>
        <p>Upload reports &amp; let<br>agents predict the future<br>with ease.</p>
      </div>

      <!-- BELOW sticky: blue checkbox card -->
      <div class="float-card checkbox-card float-anim-2">
        <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5"
          stroke-linecap="round" stroke-linejoin="round" width="28" height="28">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>

      <!-- CENTER TOP: app icon dots -->
      <div class="float-card app-icon-card float-anim-4">
        <div class="dots-grid">
          <span class="dot dot-blue lg"></span>
          <span class="dot dot-dark lg"></span>
          <span class="dot dot-dark lg"></span>
          <span class="dot dot-dark lg"></span>
        </div>
      </div>

      <!-- TOP-RIGHT: simulation card with SVG clock -->
      <div class="float-card reminders-card float-anim-3">
        <svg class="clock-svg" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="36" fill="white" stroke="#e5e7eb" stroke-width="2.5"/>
          <circle cx="40" cy="40" r="32" fill="white" stroke="#f3f4f6" stroke-width="1"/>
          <line x1="40" y1="8" x2="40" y2="14" stroke="#d1d5db" stroke-width="2" stroke-linecap="round"/>
          <line x1="40" y1="66" x2="40" y2="72" stroke="#d1d5db" stroke-width="2" stroke-linecap="round"/>
          <line x1="8" y1="40" x2="14" y2="40" stroke="#d1d5db" stroke-width="2" stroke-linecap="round"/>
          <line x1="66" y1="40" x2="72" y2="40" stroke="#d1d5db" stroke-width="2" stroke-linecap="round"/>
          <line x1="40" y1="40" x2="40" y2="20" stroke="#111827" stroke-width="3.5" stroke-linecap="round"/>
          <line x1="40" y1="40" x2="56" y2="32" stroke="#111827" stroke-width="2.5" stroke-linecap="round"/>
          <line x1="40" y1="40" x2="30" y2="58" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
          <circle cx="40" cy="40" r="3" fill="#111827"/>
          <circle cx="40" cy="40" r="1.5" fill="white"/>
        </svg>
        <div class="reminders-body">
          <div class="reminders-title">Simulation Run</div>
          <div class="reminders-meta">Agents</div>
          <div class="reminder-label">Active Run</div>
          <div class="reminder-sub">Multi-agent parallel sim</div>
          <div class="reminder-time">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.5">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            13:00 · 1,000 agents
          </div>
        </div>
      </div>

      <!-- HERO TEXT -->
      <div class="hero-text">
        <h1 class="hero-headline">
          <span class="line-dark">Upload, simulate,</span><br>
          <span class="line-muted">predict anything</span>
        </h1>
        <p class="hero-sub">Efficiently run swarm intelligence simulations and boost decision accuracy.</p>
        <button class="cta-btn" @click="scrollToConsole">Start free simulation</button>
      </div>

      <!-- BOTTOM-LEFT: today's simulations -->
      <div class="float-card tasks-card float-anim-5">
        <div class="tasks-title">Today's simulations</div>
        <div class="task-row">
          <span class="task-badge red">8</span>
          <span class="task-name">Market opinion shift</span>
          <div class="avatar-stack">
            <div class="avatar" style="background:#fbbf24;"></div>
            <div class="avatar" style="background:#60a5fa; margin-left:-8px;"></div>
          </div>
        </div>
        <div class="task-sep">Sep 10</div>
        <div class="task-bar-wrap">
          <div class="task-bar"><div class="task-fill" style="width:60%; background:linear-gradient(90deg,#3b82f6,#6366f1);"></div></div>
          <span class="task-pct">60%</span>
        </div>
        <div class="task-row" style="margin-top:14px">
          <span class="task-badge green">3</span>
          <span class="task-name">Policy impact model</span>
          <div class="avatar-stack">
            <div class="avatar" style="background:#34d399;"></div>
            <div class="avatar" style="background:#f87171; margin-left:-8px;"></div>
          </div>
        </div>
        <div class="task-sep">Sep 18</div>
        <div class="task-bar-wrap">
          <div class="task-bar"><div class="task-fill" style="width:100%; background:linear-gradient(90deg,#3b82f6,#f97316);"></div></div>
          <span class="task-pct">112%</span>
        </div>
      </div>

      <!-- BOTTOM-RIGHT: colorful data source logos -->
      <div class="float-card integrations-card float-anim-6">
        <div class="int-title">100+ Data Sources</div>
        <div class="int-logos">
          <div class="int-logo" style="background:#fee2e2;">
            <svg viewBox="0 0 36 36" width="30" height="30">
              <rect width="36" height="36" rx="7" fill="#ef4444"/>
              <text x="18" y="23" text-anchor="middle" fill="white" font-size="9" font-weight="800" font-family="sans-serif">PDF</text>
            </svg>
          </div>
          <div class="int-logo" style="background:#ede9fe;">
            <svg viewBox="0 0 36 36" width="30" height="30">
              <rect width="36" height="36" rx="7" fill="#7c3aed"/>
              <text x="18" y="23" text-anchor="middle" fill="white" font-size="9" font-weight="800" font-family="sans-serif">.MD</text>
            </svg>
          </div>
          <div class="int-logo" style="background:#dcfce7;">
            <svg viewBox="0 0 36 36" width="30" height="30">
              <rect width="36" height="36" rx="7" fill="#16a34a"/>
              <text x="18" y="23" text-anchor="middle" fill="white" font-size="8" font-weight="800" font-family="sans-serif">LIVE</text>
            </svg>
          </div>
          <div class="int-logo" style="background:#fef9c3;">
            <svg viewBox="0 0 36 36" width="30" height="30">
              <rect width="36" height="36" rx="7" fill="#d97706"/>
              <text x="18" y="23" text-anchor="middle" fill="white" font-size="9" font-weight="800" font-family="sans-serif">TXT</text>
            </svg>
          </div>
        </div>
      </div>

    </section>

    <!-- ── DASHBOARD ── -->
    <section class="dashboard-section" id="simulation" ref="consoleRef">

      <div class="left-panel" id="workflow">

        <!-- Status badge -->
        <div class="status-badge">
          <div class="status-dot-live"></div>
          <span>{{ t('home.systemStatus') }}</span>
        </div>

        <!-- Title block -->
        <div class="left-title-block">
          <h2 class="section-title">{{ t('home.ready') }}</h2>
          <p class="section-desc">{{ t('home.readyDesc') }}</p>
        </div>

        <!-- Metric cards -->
        <div class="metrics-row">
          <div class="metric-card">
            <div class="metric-icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </div>
            <div class="metric-value">{{ t('home.lowCost') }}</div>
            <div class="metric-label">{{ t('home.lowCostDesc') }}</div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <div class="metric-value">{{ t('home.highAvail') }}</div>
            <div class="metric-label">{{ t('home.highAvailDesc') }}</div>
          </div>
        </div>

        <!-- Workflow steps card -->
        <div class="steps-container" id="features-detail">
          <div class="steps-header">
            <div class="steps-header-left">
              <div class="steps-icon">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              </div>
              <span>{{ t('home.workflowSeq') }}</span>
            </div>
            <span class="steps-count">5 steps</span>
          </div>
          <div class="workflow-list">
            <div class="workflow-item" v-for="n in 5" :key="n">
              <div class="step-num-badge">0{{ n }}</div>
              <div class="step-info">
                <div class="step-title">{{ t(`home.step${n}Title`) }}</div>
                <div class="step-desc">{{ t(`home.step${n}Desc`) }}</div>
              </div>
              <div class="step-check" v-if="n === 1">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="white" stroke-width="3" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <!-- Step indicator -->
        <div class="steps-track">
          <div class="step-pill active">
            <span class="step-pill-num">01</span>
            <span>Reality Seeds</span>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-pill" :class="{ active: formData.simulationRequirement.trim() }">
            <span class="step-pill-num">02</span>
            <span>Prompt</span>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-pill" :class="{ active: canSubmit }">
            <span class="step-pill-num">03</span>
            <span>Launch</span>
          </div>
        </div>

        <!-- Upload card -->
        <div class="input-card">
          <div class="input-card-header">
            <div class="input-card-title">
              <div class="card-step-badge">01</div>
              <span>{{ t('home.seedLabel') }}</span>
            </div>
            <span class="input-card-meta">{{ t('home.seedFormats') }}</span>
          </div>
          <div
            class="upload-zone"
            :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input ref="fileInput" type="file" multiple accept=".pdf,.md,.txt"
              @change="handleFileSelect" style="display:none" :disabled="loading"/>
            <div v-if="files.length === 0" class="upload-placeholder">
              <div class="upload-cloud">
                <svg viewBox="0 0 48 48" width="40" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="48" height="48" rx="12" fill="#eff6ff"/>
                  <path d="M24 30V18M24 18L19 23M24 18L29 23" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M15 34h18" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
                  <path d="M14 26.5A6 6 0 0 1 14 14.5a6 6 0 0 1 5.5-3.5 8 8 0 0 1 14.5 4 5.5 5.5 0 0 1 0 11" stroke="#bfdbfe" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="upload-title">{{ t('home.dragUpload') }}</div>
              <div class="upload-hint">{{ t('home.browseFiles') }}</div>
              <div class="upload-formats">
                <span class="fmt-badge pdf">PDF</span>
                <span class="fmt-badge md">.MD</span>
                <span class="fmt-badge txt">TXT</span>
              </div>
            </div>
            <div v-else class="file-list">
              <div v-for="(file, index) in files" :key="index" class="file-item">
                <div class="file-type-icon">
                  {{ file.name.split('.').pop().toUpperCase() }}
                </div>
                <span class="file-name">{{ file.name }}</span>
                <button @click.stop="removeFile(index)" class="remove-btn">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Prompt card -->
        <div class="input-card">
          <div class="input-card-header">
            <div class="input-card-title">
              <div class="card-step-badge">02</div>
              <span>{{ t('home.promptLabel') }}</span>
            </div>
            <span class="engine-chip">
              <svg width="8" height="8" viewBox="0 0 8 8"><circle cx="4" cy="4" r="4" fill="#22c55e"/></svg>
              {{ t('home.engineBadge') }}
            </span>
          </div>
          <div class="prompt-wrapper" :class="{ focused: promptFocused }">
            <textarea
              v-model="formData.simulationRequirement"
              class="prompt-input"
              :placeholder="t('home.promptPlaceholder')"
              rows="5"
              :disabled="loading"
              @focus="promptFocused = true"
              @blur="promptFocused = false"
            ></textarea>
          </div>
        </div>

        <!-- News toggle card -->
        <div class="input-card toggle-card" @click="formData.enableNews = !formData.enableNews">
          <div class="toggle-card-left">
            <div class="toggle-icon-wrap">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div>
              <div class="toggle-name">{{ t('home.newsToggle') }}</div>
              <div class="toggle-desc">{{ t('home.newsToggleDesc') }}</div>
            </div>
          </div>
          <div class="toggle-switch" :class="{ 'is-active': formData.enableNews }">
            <div class="toggle-handle"></div>
          </div>
        </div>

        <!-- Launch button -->
        <button class="start-engine-btn" @click="startSimulation" :disabled="!canSubmit || loading">
          <div class="btn-left">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            <span v-if="!loading">{{ t('home.startEngine') }}</span>
            <span v-else class="loading-dots">{{ t('home.initializing') }}</span>
          </div>
          <span class="btn-arrow">→</span>
        </button>
      </div>
    </section>

    <div id="history">
      <HistoryDatabase />
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import HistoryDatabase from '../components/HistoryDatabase.vue'

const router = useRouter()
const { t, locale } = useI18n()

const toggleLang = () => {
  locale.value = locale.value === 'en' ? 'zh' : 'en'
  localStorage.setItem('locale', locale.value)
}

const formData = ref({ simulationRequirement: '', enableNews: false })
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const fileInput = ref(null)
const consoleRef = ref(null)
const promptFocused = ref(false)

const canSubmit = computed(() =>
  formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
)

const scrollTo = (id) => {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const scrollToConsole = () => {
  consoleRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const triggerFileInput = () => { if (!loading.value) fileInput.value?.click() }
const handleFileSelect = (e) => addFiles(Array.from(e.target.files))
const handleDragOver = () => { if (!loading.value) isDragOver.value = true }
const handleDragLeave = () => { isDragOver.value = false }
const handleDrop = (e) => {
  isDragOver.value = false
  if (!loading.value) addFiles(Array.from(e.dataTransfer.files))
}
const addFiles = (newFiles) => {
  files.value.push(...newFiles.filter(f =>
    ['pdf','md','txt'].includes(f.name.split('.').pop().toLowerCase())
  ))
}
const removeFile = (i) => files.value.splice(i, 1)

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement, formData.value.enableNews)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&family=Caveat:wght@600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

.home-container {
  min-height: 100vh;
  background: #fff;
  font-family: 'DM Sans', system-ui, sans-serif;
  color: #0a0a0a;
}

/* ── NAVBAR ── */
.navbar {
  position: sticky; top: 0; z-index: 100;
  height: 64px;
  background: rgba(255,255,255,0.94);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid #e5e7eb;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 48px;
}

.nav-brand {
  display: flex; align-items: center; gap: 10px;
  font-weight: 800; font-size: 0.95rem; letter-spacing: 2px;
  color: #0a0a0a; cursor: default;
}

.brand-dots { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; }

.dot { border-radius: 50%; display: inline-block; }
.dot.dot-blue { background: #2563EB; }
.dot.dot-dark { background: #111827; }
.dot.lg { width: 11px; height: 11px; }

.nav-center { display: flex; gap: 40px; }

.nav-link {
  color: #4b5563; font-size: 0.9rem; font-weight: 500;
  cursor: pointer; text-decoration: none;
  transition: color 0.2s; position: relative;
}
.nav-link::after {
  content: ''; position: absolute; bottom: -4px; left: 0;
  width: 0; height: 2px; background: #2563EB;
  transition: width 0.22s; border-radius: 2px;
}
.nav-link:hover { color: #0a0a0a; }
.nav-link:hover::after { width: 100%; }

.nav-right { display: flex; align-items: center; gap: 12px; }

.lang-toggle {
  border: 1px solid #e5e7eb; background: transparent;
  padding: 6px 16px; font-size: 0.8rem; font-weight: 700;
  font-family: 'DM Mono', monospace; border-radius: 6px;
  cursor: pointer; transition: all 0.2s; color: #0a0a0a;
}
.lang-toggle:hover { background: #f9fafb; border-color: #d1d5db; }

.github-btn {
  background: #0a0a0a; color: #fff; text-decoration: none;
  padding: 8px 22px; border-radius: 8px;
  font-size: 0.85rem; font-weight: 600;
  transition: opacity 0.2s; white-space: nowrap;
}
.github-btn:hover { opacity: 0.8; }

/* ── HERO ── */
.hero-section {
  position: relative; min-height: 90vh;
  background-color: #efefef;
  background-image: radial-gradient(circle, #bebebe 1px, transparent 1px);
  background-size: 22px 22px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}

.hero-text {
  text-align: center; z-index: 2;
  max-width: 680px; padding: 0 20px;
}

.hero-headline {
  font-size: clamp(3rem, 6.5vw, 5.6rem);
  font-weight: 800; line-height: 1.08;
  letter-spacing: -3px; margin-bottom: 22px;
}
.line-dark { color: #0a0a0a; }
.line-muted { color: #c4c4c4; }

.hero-sub {
  font-size: 1rem; color: #6b7280;
  margin-bottom: 38px; font-weight: 400; line-height: 1.6;
}

.cta-btn {
  background: #2563EB; color: white; border: none;
  padding: 17px 44px; border-radius: 50px;
  font-size: 1rem; font-weight: 600;
  font-family: 'DM Sans', sans-serif; cursor: pointer;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 6px 24px rgba(37,99,235,0.38);
}
.cta-btn:hover {
  background: #1d4ed8; transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(37,99,235,0.46);
}

/* ── FLOAT CARDS ── */
.float-card {
  position: absolute;
  background: white; border-radius: 18px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.11), 0 1px 4px rgba(0,0,0,0.06);
  z-index: 3;
}

@keyframes floatA { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-12px) rotate(-2deg)} }
@keyframes floatB { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-9px)} }
@keyframes floatC { 0%,100%{transform:translateY(0) rotate(1.5deg)} 50%{transform:translateY(-11px) rotate(1.5deg)} }

.float-anim-1 { animation: floatA 5.5s ease-in-out infinite; }
.float-anim-2 { animation: floatB 4.5s ease-in-out infinite 0.6s; }
.float-anim-3 { animation: floatC 6s ease-in-out infinite 1.1s; }
.float-anim-4 { animation: floatB 5s ease-in-out infinite 0.3s; }
.float-anim-5 { animation: floatA 6.5s ease-in-out infinite 0.9s; }
.float-anim-6 { animation: floatC 5.8s ease-in-out infinite 0.4s; }

/* Sticky note */
.sticky-note {
  top: 9%; left: 5%;
  background: #fef08a; padding: 28px 24px 22px;
  width: 220px; border-radius: 3px;
  box-shadow: 4px 6px 20px rgba(0,0,0,0.15);
  transform: rotate(-2deg);
}
.sticky-note p {
  font-family: 'Caveat', cursive;
  font-size: 1.1rem; line-height: 1.65;
  color: #374151; font-weight: 600;
}

.pin {
  position: absolute; top: -16px; left: 50%;
  transform: translateX(-50%);
  display: flex; flex-direction: column; align-items: center;
}
.pin-head {
  width: 18px; height: 18px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #f87171, #dc2626);
  box-shadow: 0 2px 8px rgba(220,38,38,0.5);
}
.pin-needle {
  width: 2px; height: 10px;
  background: linear-gradient(#9ca3af, #6b7280);
  border-radius: 0 0 2px 2px;
}

/* Blue checkbox */
.checkbox-card {
  top: 45%; left: 7.5%;
  width: 70px; height: 70px; border-radius: 18px;
  background: #2563EB;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(37,99,235,0.38);
}

/* App icon */
.app-icon-card {
  top: 7%; left: 50%; transform: translateX(-50%);
  width: 82px; height: 82px; border-radius: 22px;
  display: flex; align-items: center; justify-content: center;
}
.dots-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }

/* Clock card */
.reminders-card {
  top: 9%; right: 5%;
  display: flex; align-items: flex-start; gap: 14px;
  padding: 18px 22px; width: 265px;
  transform: rotate(1.5deg);
}
.clock-svg {
  width: 72px; height: 72px; flex-shrink: 0;
  filter: drop-shadow(0 3px 10px rgba(0,0,0,0.1));
}
.reminders-body { flex: 1; }
.reminders-title { font-weight: 800; font-size: 0.88rem; margin-bottom: 2px; }
.reminders-meta {
  font-size: 0.68rem; color: #9ca3af;
  font-family: 'DM Mono', monospace; text-align: right; margin-bottom: 8px;
}
.reminder-label { font-weight: 600; font-size: 0.82rem; color: #111827; }
.reminder-sub { font-size: 0.72rem; color: #6b7280; margin: 2px 0 5px; }
.reminder-time {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.7rem; color: #2563EB;
  font-family: 'DM Mono', monospace; font-weight: 500;
}

/* Tasks card */
.tasks-card {
  bottom: 5%; left: 3.5%;
  width: 275px; padding: 20px 22px;
}
.tasks-title {
  font-weight: 700; font-size: 0.88rem; margin-bottom: 14px;
  font-family: 'DM Mono', monospace;
}
.task-row { display: flex; align-items: center; gap: 8px; }
.task-badge {
  width: 22px; height: 22px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 800; color: white; flex-shrink: 0;
}
.task-badge.red { background: #ef4444; }
.task-badge.green { background: #22c55e; }
.task-name { flex: 1; font-size: 0.78rem; font-weight: 500; font-family: 'DM Mono', monospace; }
.avatar-stack { display: flex; flex-shrink: 0; }
.avatar { width: 22px; height: 22px; border-radius: 50%; border: 2px solid white; }
.task-sep { font-size: 0.68rem; color: #9ca3af; margin: 6px 0 4px; font-family: 'DM Mono', monospace; }
.task-bar-wrap { display: flex; align-items: center; gap: 8px; }
.task-bar { flex: 1; height: 5px; background: #f3f4f6; border-radius: 3px; overflow: hidden; }
.task-fill { height: 100%; border-radius: 3px; }
.task-pct { font-size: 0.7rem; color: #6b7280; font-family: 'DM Mono', monospace; white-space: nowrap; }

/* Integrations */
.integrations-card { bottom: 7%; right: 3.5%; padding: 20px 24px; }
.int-title { font-weight: 700; font-size: 0.88rem; margin-bottom: 14px; }
.int-logos { display: flex; gap: 10px; }
.int-logo {
  width: 54px; height: 54px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.09);
  transition: transform 0.2s;
}
.int-logo:hover { transform: scale(1.1) translateY(-2px); }

/* ── DASHBOARD ── */
.dashboard-section {
  display: flex; gap: 60px;
  max-width: 1300px; margin: 0 auto;
  padding: 80px 48px; align-items: flex-start;
}

.left-panel { flex: 0.85; display: flex; flex-direction: column; gap: 20px; }

/* Status badge */
.status-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: 20px;
  border: 1px solid #e5e7eb; background: white;
  font-size: 0.75rem; font-weight: 600; color: #374151;
  width: fit-content;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.status-dot-live {
  width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
  box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
  animation: pulse-green 2s ease-in-out infinite;
}
@keyframes pulse-green {
  0%,100% { box-shadow: 0 0 0 3px rgba(34,197,94,0.2); }
  50% { box-shadow: 0 0 0 6px rgba(34,197,94,0.08); }
}

/* Title block */
.section-title { font-size: 2.6rem; font-weight: 800; margin-bottom: 10px; letter-spacing: -2px; color: #0a0a0a; line-height: 1.1; }
.section-desc { color: #6b7280; font-size: 0.88rem; line-height: 1.7; font-weight: 400; }

/* Metric cards */
.metrics-row { display: flex; gap: 14px; }
.metric-card {
  flex: 1; border: 1px solid #e5e7eb; padding: 20px 22px; border-radius: 16px;
  background: white; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s, transform 0.2s;
}
.metric-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.09); transform: translateY(-2px); }
.metric-icon {
  width: 36px; height: 36px; border-radius: 10px; background: #eff6ff;
  display: flex; align-items: center; justify-content: center; margin-bottom: 14px;
}
.metric-value { font-size: 1.5rem; font-weight: 800; margin-bottom: 4px; letter-spacing: -0.5px; color: #0a0a0a; }
.metric-label { font-size: 0.78rem; color: #9ca3af; font-weight: 400; }

/* Steps container */
.steps-container {
  border: 1px solid #e5e7eb; border-radius: 16px;
  background: white; box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  overflow: hidden;
}
.steps-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 22px;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}
.steps-header-left {
  display: flex; align-items: center; gap: 8px;
  font-weight: 600; font-size: 0.82rem; color: #374151;
}
.steps-icon {
  width: 26px; height: 26px; border-radius: 8px; background: #eff6ff;
  display: flex; align-items: center; justify-content: center;
}
.steps-count {
  font-size: 0.72rem; color: #9ca3af; font-weight: 500;
  background: #f3f4f6; padding: 3px 10px; border-radius: 20px;
}

.workflow-list { display: flex; flex-direction: column; padding: 8px 0; }
.workflow-item {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 14px 22px; position: relative;
  transition: background 0.15s;
}
.workflow-item:hover { background: #f9fafb; }
.workflow-item:not(:last-child)::after {
  content: ''; position: absolute;
  left: 42px; bottom: 0; right: 22px;
  height: 1px; background: #f3f4f6;
}

.step-num-badge {
  width: 28px; height: 28px; border-radius: 8px;
  background: #f3f4f6; color: #9ca3af;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.68rem; font-weight: 800;
  font-family: 'DM Mono', monospace; flex-shrink: 0; margin-top: 1px;
}
.step-info { flex: 1; }
.step-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 3px; color: #111827; }
.step-desc { font-size: 0.78rem; color: #9ca3af; line-height: 1.55; }
.step-check {
  width: 20px; height: 20px; border-radius: 6px; background: #22c55e;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;
}

.right-panel { flex: 1.2; display: flex; flex-direction: column; gap: 14px; }

/* Step progress track */
.steps-track {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 18px;
  background: #fafafa; border: 1px solid #e5e7eb;
  border-radius: 14px; margin-bottom: 4px;
}
.step-pill {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 20px;
  border: 1.5px solid #e5e7eb; background: white;
  font-size: 0.75rem; font-weight: 500; color: #9ca3af;
  font-family: 'DM Mono', monospace; transition: all 0.3s;
}
.step-pill.active { border-color: #2563EB; color: #2563EB; background: #eff6ff; }
.step-pill-num { font-weight: 800; font-size: 0.7rem; }
.step-arrow { color: #d1d5db; font-size: 0.8rem; flex-shrink: 0; }

/* Input cards */
.input-card {
  background: white; border: 1px solid #e5e7eb;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s;
}
.input-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.08); }

.input-card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px 12px;
  border-bottom: 1px solid #f3f4f6;
}
.input-card-title {
  display: flex; align-items: center; gap: 10px;
  font-weight: 700; font-size: 0.88rem; color: #111827;
}
.card-step-badge {
  width: 24px; height: 24px; border-radius: 8px;
  background: #0a0a0a; color: white;
  display: flex; align-items: center; justify-content: center;
  font-family: 'DM Mono', monospace; font-size: 0.65rem; font-weight: 800;
}
.input-card-meta { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #9ca3af; }

.engine-chip {
  display: flex; align-items: center; gap: 5px;
  font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #374151;
  background: #f0fdf4; border: 1px solid #bbf7d0;
  padding: 3px 10px; border-radius: 20px; font-weight: 500;
}

/* Upload zone */
.upload-zone {
  padding: 0;
  min-height: 150px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.25s; background: white; overflow-y: auto;
  border-radius: 0 0 16px 16px;
}
.upload-zone.drag-over { background: #eff6ff; }
.upload-zone.has-files { align-items: flex-start; }

.upload-placeholder { text-align: center; padding: 24px 20px; }
.upload-cloud { margin: 0 auto 12px; display: flex; justify-content: center; }
.upload-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; color: #111827; }
.upload-hint { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #9ca3af; margin-bottom: 14px; }
.upload-formats { display: flex; justify-content: center; gap: 6px; }
.fmt-badge {
  padding: 3px 10px; border-radius: 6px;
  font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 700;
}
.fmt-badge.pdf { background: #fee2e2; color: #dc2626; }
.fmt-badge.md { background: #ede9fe; color: #7c3aed; }
.fmt-badge.txt { background: #fef9c3; color: #d97706; }

.file-list { width: 100%; padding: 12px 16px; display: flex; flex-direction: column; gap: 8px; }
.file-item {
  display: flex; align-items: center;
  background: #f9fafb; padding: 10px 12px;
  border: 1px solid #f3f4f6; border-radius: 10px; gap: 10px;
}
.file-type-icon {
  width: 32px; height: 32px; border-radius: 8px; background: #2563EB;
  color: white; display: flex; align-items: center; justify-content: center;
  font-family: 'DM Mono', monospace; font-size: 0.55rem; font-weight: 800; flex-shrink: 0;
}
.file-name { flex: 1; font-family: 'DM Mono', monospace; font-size: 0.78rem; color: #374151; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.remove-btn { background: none; border: none; cursor: pointer; color: #d1d5db; display: flex; align-items: center; padding: 2px; border-radius: 4px; transition: color 0.15s; }
.remove-btn:hover { color: #ef4444; }

/* Prompt card */
.prompt-wrapper {
  transition: border-color 0.2s;
}
.prompt-input {
  width: 100%; border: none; background: transparent;
  padding: 16px 18px;
  font-family: 'DM Mono', monospace; font-size: 0.84rem; line-height: 1.75;
  resize: vertical; outline: none; min-height: 130px; color: #111827;
  border-radius: 0 0 16px 16px;
}

/* Toggle card */
.toggle-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; cursor: pointer;
  overflow: visible;
}
.toggle-card:hover { background: #fafafa; }
.toggle-card-left { display: flex; align-items: center; gap: 12px; }
.toggle-icon-wrap {
  width: 36px; height: 36px; border-radius: 10px; background: #eff6ff;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.toggle-switch { width: 42px; height: 24px; background: #e5e7eb; border-radius: 12px; position: relative; transition: background 0.3s; flex-shrink: 0; }
.toggle-switch.is-active { background: #2563EB; }
.toggle-handle { width: 18px; height: 18px; background: white; border-radius: 50%; position: absolute; top: 3px; left: 3px; transition: left 0.3s; box-shadow: 0 1px 4px rgba(0,0,0,0.15); }
.toggle-switch.is-active .toggle-handle { left: 21px; }
.toggle-name { font-weight: 600; font-size: 0.85rem; color: #111827; margin-bottom: 2px; }
.toggle-desc { font-size: 0.72rem; color: #9ca3af; }

/* Launch button */
.start-engine-btn {
  width: 100%; background: #0a0a0a; color: white; border: none;
  padding: 18px 24px; font-family: 'DM Sans', sans-serif; font-weight: 700;
  font-size: 1rem; border-radius: 14px;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer; transition: all 0.25s; letter-spacing: 0.3px;
}
.start-engine-btn .btn-left { display: flex; align-items: center; gap: 10px; }
.start-engine-btn:not(:disabled):hover { background: #2563EB; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(37,99,235,0.38); }
.start-engine-btn:disabled { background: #e5e7eb; color: #9ca3af; cursor: not-allowed; }
.btn-arrow { font-size: 1.3rem; }
.loading-dots::after { content: '...'; animation: dots 1.2s steps(4, end) infinite; }
@keyframes dots { 0%,20%{content:'.'} 40%{content:'..'} 60%,100%{content:'...'} }

@media (max-width: 1024px) {
  .navbar { padding: 0 24px; }
  .nav-center { display: none; }
  .dashboard-section { flex-direction: column; padding: 60px 24px; }
  .hero-section { min-height: 70vh; }
  .float-card { display: none; }
}
</style>