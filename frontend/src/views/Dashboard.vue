<template>
  <div class="dashboard-page">

    <!-- NAVBAR (mirrors Home.vue) -->
    <nav class="navbar">
      <div class="nav-brand" @click="router.push('/')" style="cursor:pointer">
        <span class="brand-dots">
          <span class="dot dot-blue"></span>
          <span class="dot dot-dark"></span>
          <span class="dot dot-dark"></span>
          <span class="dot dot-dark"></span>
        </span>
        PROPHESIZE AI
      </div>
      <div class="nav-center">
        <a class="nav-link" @click="router.push('/')">← Back to Home</a>
      </div>
      <div class="nav-right">
        <span class="page-label">Token Usage Dashboard</span>
      </div>
    </nav>

    <!-- MAIN CONTENT -->
    <div class="page-body">

      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Token Usage</h1>
          <p class="page-sub">All LLM calls tracked across projects and simulations</p>
        </div>
        <button class="refresh-btn" @click="load" :disabled="loading">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor"
            stroke-width="2.5" stroke-linecap="round" :class="{ spinning: loading }">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
          Refresh
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>Loading usage data…</span>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="error-state">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ error }}
      </div>

      <template v-else-if="data">

        <!-- ── OVERVIEW CARDS ── -->
        <div class="cards-row">
          <div class="stat-card">
            <div class="stat-icon blue">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
            </div>
            <div class="stat-value">{{ fmt(data.totals.total_tokens) }}</div>
            <div class="stat-label">Total Tokens Used</div>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <div class="stat-value">{{ fmt(data.totals.input_tokens) }}</div>
            <div class="stat-label">Input Tokens</div>
          </div>

          <div class="stat-card">
            <div class="stat-icon purple">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#7c3aed" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div class="stat-value">{{ fmt(data.totals.output_tokens) }}</div>
            <div class="stat-label">Output Tokens</div>
          </div>

          <div class="stat-card">
            <div class="stat-icon orange">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#d97706" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="stat-value">{{ data.totals.total_calls }}</div>
            <div class="stat-label">Total LLM Calls</div>
          </div>

          <div class="stat-card">
            <div class="stat-icon blue">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
            </div>
            <div class="stat-value">{{ data.by_project.length }}</div>
            <div class="stat-label">Projects</div>
          </div>

          <div class="stat-card">
            <div class="stat-icon green">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            </div>
            <div class="stat-value">{{ data.by_simulation.length }}</div>
            <div class="stat-label">Simulations Run</div>
          </div>
        </div>

        <!-- ── TOKEN SPLIT BAR ── -->
        <div class="section-card">
          <div class="section-header">
            <span class="section-title">Input vs Output Split</span>
            <span class="section-meta">{{ inputPct }}% input · {{ outputPct }}% output</span>
          </div>
          <div class="split-bar-track">
            <div class="split-bar-fill input" :style="{ width: inputPct + '%' }"></div>
            <div class="split-bar-fill output" :style="{ width: outputPct + '%' }"></div>
          </div>
          <div class="split-legend">
            <span class="legend-dot input"></span> Input ({{ fmt(data.totals.input_tokens) }})
            &nbsp;&nbsp;
            <span class="legend-dot output"></span> Output ({{ fmt(data.totals.output_tokens) }})
          </div>
        </div>

        <!-- ── BY OPERATION ── -->
        <div class="section-card">
          <div class="section-header">
            <span class="section-title">Breakdown by Operation</span>
            <span class="section-meta">{{ Object.keys(data.by_operation).length }} operation types</span>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Operation</th>
                <th class="num">Calls</th>
                <th class="num">Input Tokens</th>
                <th class="num">Output Tokens</th>
                <th class="num">Total Tokens</th>
                <th class="num">% of Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(op, name) in sortedOperations" :key="name">
                <td>
                  <span class="op-badge" :class="opColor(name)">{{ formatOpName(name) }}</span>
                </td>
                <td class="num mono">{{ op.calls }}</td>
                <td class="num mono">{{ fmt(op.input_tokens) }}</td>
                <td class="num mono">{{ fmt(op.output_tokens) }}</td>
                <td class="num mono bold">{{ fmt(op.input_tokens + op.output_tokens) }}</td>
                <td class="num">
                  <div class="pct-cell">
                    <div class="mini-bar">
                      <div class="mini-fill" :style="{ width: opPct(op) + '%' }"></div>
                    </div>
                    <span class="mono">{{ opPct(op) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ── BY PROJECT ── -->
        <div class="section-card" v-if="data.by_project.length">
          <div class="section-header">
            <span class="section-title">By Project</span>
            <span class="section-meta">{{ data.by_project.length }} projects</span>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Project ID</th>
                <th class="num">Calls</th>
                <th class="num">Input</th>
                <th class="num">Output</th>
                <th class="num">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in data.by_project" :key="p.project_id">
                <td class="mono id-cell">{{ p.project_id }}</td>
                <td class="num mono">{{ p.calls }}</td>
                <td class="num mono">{{ fmt(p.input_tokens) }}</td>
                <td class="num mono">{{ fmt(p.output_tokens) }}</td>
                <td class="num mono bold">{{ fmt(p.total_tokens) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ── BY SIMULATION ── -->
        <div class="section-card" v-if="data.by_simulation.length">
          <div class="section-header">
            <span class="section-title">By Simulation</span>
            <span class="section-meta">{{ data.by_simulation.length }} simulations</span>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>Simulation ID</th>
                <th class="num">Calls</th>
                <th class="num">Input</th>
                <th class="num">Output</th>
                <th class="num">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in data.by_simulation" :key="s.simulation_id">
                <td class="mono id-cell">{{ s.simulation_id }}</td>
                <td class="num mono">{{ s.calls }}</td>
                <td class="num mono">{{ fmt(s.input_tokens) }}</td>
                <td class="num mono">{{ fmt(s.output_tokens) }}</td>
                <td class="num mono bold">{{ fmt(s.total_tokens) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats } from '../api/analytics'

const router = useRouter()
const loading = ref(false)
const error   = ref(null)
const data    = ref(null)

const load = async () => {
  loading.value = true
  error.value   = null
  try {
    const res = await getDashboardStats()
    data.value = res.data
  } catch (e) {
    error.value = e.message || 'Failed to load dashboard data.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

// ── Helpers ──────────────────────────────────────────────────────────────────

const fmt = (n) => {
  if (n == null) return '0'
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K'
  return n.toString()
}

const inputPct = computed(() => {
  if (!data.value?.totals?.total_tokens) return 50
  return Math.round((data.value.totals.input_tokens / data.value.totals.total_tokens) * 100)
})
const outputPct = computed(() => 100 - inputPct.value)

const sortedOperations = computed(() => {
  if (!data.value?.by_operation) return {}
  return Object.fromEntries(
    Object.entries(data.value.by_operation).sort(
      ([, a], [, b]) => (b.input_tokens + b.output_tokens) - (a.input_tokens + a.output_tokens)
    )
  )
})

const opPct = (op) => {
  if (!data.value?.totals?.total_tokens) return 0
  return Math.round(((op.input_tokens + op.output_tokens) / data.value.totals.total_tokens) * 100)
}

const formatOpName = (name) =>
  name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

const OP_COLORS = {
  ontology_generation:              'badge-blue',
  simulation_config_generation:     'badge-purple',
  report_outline_generation:        'badge-green',
  report_section_writing:           'badge-orange',
  report_section_force_finalization:'badge-red',
}
const opColor = (name) => OP_COLORS[name] || 'badge-gray'
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

.dashboard-page {
  min-height: 100vh;
  background: #f8fafc;
  font-family: 'DM Sans', system-ui, sans-serif;
  color: #0a0a0a;
}

/* ── NAVBAR ── */
.navbar {
  position: sticky; top: 0; z-index: 100;
  height: 64px;
  background: rgba(255,255,255,0.94);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid #e5e7eb;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 48px;
}
.nav-brand {
  display: flex; align-items: center; gap: 10px;
  font-weight: 800; font-size: 0.95rem; letter-spacing: 2px; color: #0a0a0a;
}
.brand-dots { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; }
.dot { border-radius: 50%; display: inline-block; width: 8px; height: 8px; }
.dot.dot-blue { background: #2563EB; }
.dot.dot-dark { background: #111827; }
.nav-center { display: flex; gap: 32px; }
.nav-link {
  color: #4b5563; font-size: 0.9rem; font-weight: 500;
  cursor: pointer; text-decoration: none; transition: color 0.2s;
}
.nav-link:hover { color: #2563EB; }
.nav-right { display: flex; align-items: center; }
.page-label {
  font-family: 'DM Mono', monospace; font-size: 0.72rem;
  color: #9ca3af; font-weight: 500;
}

/* ── BODY ── */
.page-body {
  max-width: 1280px; margin: 0 auto;
  padding: 48px 48px 80px;
  display: flex; flex-direction: column; gap: 24px;
}

/* ── HEADER ── */
.page-header {
  display: flex; align-items: flex-end; justify-content: space-between;
}
.page-title {
  font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; color: #0a0a0a;
  margin-bottom: 4px;
}
.page-sub { color: #6b7280; font-size: 0.88rem; }
.refresh-btn {
  display: flex; align-items: center; gap: 7px;
  padding: 9px 18px; border-radius: 10px;
  border: 1px solid #e5e7eb; background: white;
  font-family: 'DM Sans', sans-serif; font-size: 0.85rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s; color: #374151;
}
.refresh-btn:hover { border-color: #2563EB; color: #2563EB; }
.refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }
@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin 0.8s linear infinite; }

/* Loading / Error */
.loading-state, .error-state {
  display: flex; align-items: center; gap: 12px;
  padding: 48px; justify-content: center;
  color: #6b7280; font-size: 0.9rem;
}
.spinner {
  width: 20px; height: 20px; border-radius: 50%;
  border: 2.5px solid #e5e7eb; border-top-color: #2563EB;
  animation: spin 0.7s linear infinite;
}

/* ── OVERVIEW CARDS ── */
.cards-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}
.stat-card {
  background: white; border: 1px solid #e5e7eb;
  border-radius: 16px; padding: 20px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s, transform 0.2s;
}
.stat-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }
.stat-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
}
.stat-icon.blue   { background: #eff6ff; }
.stat-icon.green  { background: #f0fdf4; }
.stat-icon.purple { background: #f5f3ff; }
.stat-icon.orange { background: #fffbeb; }
.stat-value { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 4px; }
.stat-label { font-size: 0.74rem; color: #9ca3af; font-weight: 400; }

/* ── SECTION CARDS ── */
.section-card {
  background: white; border: 1px solid #e5e7eb;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.section-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}
.section-title { font-weight: 700; font-size: 0.9rem; color: #111827; }
.section-meta { font-size: 0.75rem; color: #9ca3af; font-family: 'DM Mono', monospace; }

/* ── SPLIT BAR ── */
.split-bar-track {
  display: flex; height: 10px; margin: 20px 24px 10px;
  border-radius: 6px; overflow: hidden; background: #f3f4f6;
}
.split-bar-fill { height: 100%; transition: width 0.6s ease; }
.split-bar-fill.input  { background: #2563EB; }
.split-bar-fill.output { background: #7c3aed; }
.split-legend {
  padding: 0 24px 20px;
  font-size: 0.78rem; color: #6b7280;
  display: flex; align-items: center; gap: 4px;
}
.legend-dot {
  width: 9px; height: 9px; border-radius: 50%; display: inline-block;
}
.legend-dot.input  { background: #2563EB; }
.legend-dot.output { background: #7c3aed; }

/* ── TABLES ── */
.data-table {
  width: 100%; border-collapse: collapse; font-size: 0.84rem;
}
.data-table thead tr { background: #fafafa; }
.data-table th {
  padding: 11px 20px; text-align: left;
  font-weight: 700; font-size: 0.74rem;
  color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;
  border-bottom: 1px solid #f3f4f6;
}
.data-table th.num { text-align: right; }
.data-table td {
  padding: 12px 20px; border-bottom: 1px solid #f9fafb;
  color: #374151;
}
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover td { background: #f9fafb; }
.data-table td.num { text-align: right; }
.mono { font-family: 'DM Mono', monospace; font-size: 0.8rem; }
.bold { font-weight: 700; color: #111827; }
.id-cell {
  font-size: 0.72rem; color: #6b7280;
  max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Op badges */
.op-badge {
  display: inline-flex; padding: 4px 10px; border-radius: 20px;
  font-size: 0.74rem; font-weight: 600; white-space: nowrap;
}
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-purple { background: #ede9fe; color: #6d28d9; }
.badge-green  { background: #dcfce7; color: #15803d; }
.badge-orange { background: #ffedd5; color: #c2410c; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-gray   { background: #f3f4f6; color: #6b7280; }

/* Mini bar inside table */
.pct-cell { display: flex; align-items: center; gap: 8px; justify-content: flex-end; }
.mini-bar { width: 60px; height: 5px; background: #f3f4f6; border-radius: 3px; overflow: hidden; }
.mini-fill { height: 100%; background: #2563EB; border-radius: 3px; }

@media (max-width: 1024px) {
  .navbar { padding: 0 24px; }
  .page-body { padding: 32px 24px 60px; }
  .cards-row { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 600px) {
  .cards-row { grid-template-columns: repeat(2, 1fr); }
  .data-table { font-size: 0.75rem; }
}
</style>