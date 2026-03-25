<template>
  <div class="workbench-panel">
    <div class="scroll-container custom-scrollbar">
      <div class="step-card" :class="{ 'active': currentPhase === 0, 'completed': currentPhase > 0 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">Ontology Generation</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase > 0" class="badge success">COMPLETED</span>
            <span v-else-if="currentPhase === 0" class="badge processing">GENERATING</span>
            <span v-else class="badge pending">PENDING</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/graph/ontology/generate</p>
          <p class="description">
            LLM analyzes documents and extracts reality seeds to construct schema.
          </p>

          <transition name="fade">
            <div v-if="currentPhase === 0 && ontologyProgress" class="progress-section">
              <div class="spinner-sm"></div>
              <span>{{ ontologyProgress.message || 'Analyzing documents...' }}</span>
            </div>
          </transition>

          <transition name="slide-up">
            <div v-if="selectedOntologyItem" class="ontology-detail-overlay">
              <div class="detail-header">
                 <div class="detail-title-group">
                    <span class="detail-type-badge" :class="selectedOntologyItem.itemType">{{ selectedOntologyItem.itemType === 'entity' ? 'ENTITY' : 'RELATION' }}</span>
                    <span class="detail-name">{{ selectedOntologyItem.name }}</span>
                 </div>
                 <button class="close-btn" @click="selectedOntologyItem = null">
                   <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                 </button>
              </div>
              <div class="detail-body custom-scrollbar">
                 <div class="detail-desc">{{ selectedOntologyItem.description }}</div>
                 
                 <div class="detail-section" v-if="selectedOntologyItem.attributes?.length">
                    <span class="section-label">ATTRIBUTES</span>
                    <div class="attr-list">
                       <div v-for="attr in selectedOntologyItem.attributes" :key="attr.name" class="attr-item">
                          <div class="attr-header">
                            <span class="attr-name">{{ attr.name }}</span>
                            <span class="attr-type">{{ attr.type }}</span>
                          </div>
                          <span class="attr-desc">{{ attr.description }}</span>
                       </div>
                    </div>
                 </div>

                 <div class="detail-section" v-if="selectedOntologyItem.examples?.length">
                    <span class="section-label">EXAMPLES</span>
                    <div class="example-list">
                       <span v-for="ex in selectedOntologyItem.examples" :key="ex" class="example-tag">{{ ex }}</span>
                    </div>
                 </div>

                 <div class="detail-section" v-if="selectedOntologyItem.source_targets?.length">
                    <span class="section-label">CONNECTIONS</span>
                    <div class="conn-list">
                       <div v-for="(conn, idx) in selectedOntologyItem.source_targets" :key="idx" class="conn-item">
                          <span class="conn-node">{{ conn.source }}</span>
                          <span class="conn-arrow">→</span>
                          <span class="conn-node">{{ conn.target }}</span>
                       </div>
                    </div>
                 </div>
              </div>
            </div>
          </transition>

          <div v-if="projectData?.ontology?.entity_types" class="tags-container" :class="{ 'dimmed': selectedOntologyItem }">
            <span class="tag-label">GENERATED ENTITY TYPES</span>
            <div class="tags-list">
              <button 
                v-for="entity in projectData.ontology.entity_types" 
                :key="entity.name" 
                class="entity-tag clickable"
                @click="selectOntologyItem(entity, 'entity')"
              >
                {{ entity.name }}
              </button>
            </div>
          </div>

          <div v-if="projectData?.ontology?.edge_types" class="tags-container" :class="{ 'dimmed': selectedOntologyItem }">
            <span class="tag-label">GENERATED RELATION TYPES</span>
            <div class="tags-list">
              <button 
                v-for="rel in projectData.ontology.edge_types" 
                :key="rel.name" 
                class="entity-tag relation clickable"
                @click="selectOntologyItem(rel, 'relation')"
              >
                {{ rel.name }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="step-card" :class="{ 'active': currentPhase === 1, 'completed': currentPhase > 1 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">GraphRAG Build</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase > 1" class="badge success">COMPLETED</span>
            <span v-else-if="currentPhase === 1" class="badge processing">{{ buildProgress?.progress || 0 }}%</span>
            <span v-else class="badge pending">PENDING</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/graph/build</p>
          <p class="description">
            Documents are chunked and processed through Zep to extract relations and memory.
          </p>
          
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon-wrapper">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>
              </div>
              <span class="stat-value">{{ graphStats.nodes }}</span>
              <span class="stat-label">Entity Nodes</span>
            </div>
            <div class="stat-card">
              <div class="stat-icon-wrapper">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
              </div>
              <span class="stat-value">{{ graphStats.edges }}</span>
              <span class="stat-label">Relation Edges</span>
            </div>
            <div class="stat-card">
              <div class="stat-icon-wrapper">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
              </div>
              <span class="stat-value">{{ graphStats.types }}</span>
              <span class="stat-label">Schema Types</span>
            </div>
          </div>
        </div>
      </div>

      <div class="step-card" :class="{ 'active': currentPhase === 2, 'completed': currentPhase >= 2 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">Build Complete</span>
          </div>
          <div class="step-status">
            <span v-if="currentPhase >= 2" class="badge accent">READY</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/simulation/create</p>
          <p class="description">Graph construction complete. Set parameters below to proceed to environment setup.</p>
          
          <div class="settings-group">
            <div class="platform-toggle-row">
              <div class="toggle-copy">
                <span class="toggle-title">LinkedIn Connection</span>
                <span class="toggle-desc">Include LinkedIn alongside Reddit and Twitter when the simulation runs.</span>
              </div>
              <label class="switch-control">
                <input v-model="enableLinkedIn" type="checkbox" :disabled="currentPhase < 2">
                <span class="switch-track"></span>
                <span class="switch-label">{{ enableLinkedIn ? 'On' : 'Off' }}</span>
              </label>
            </div>
            <div class="platform-toggle-row">
              <div class="toggle-copy">
                <span class="toggle-title">Discover Related Entities</span>
                <span class="toggle-desc">Let the LLM add up to 5 extra relevant entities not explicitly mentioned in the source material.</span>
              </div>
              <label class="switch-control">
                <input v-model="discoverRelatedEntities" type="checkbox" :disabled="currentPhase < 2">
                <span class="switch-track"></span>
                <span class="switch-label">{{ discoverRelatedEntities ? 'On' : 'Off' }}</span>
              </label>
            </div>
          </div>

          <div class="custom-entities-panel">
            <div class="custom-entities-header">
              <div class="toggle-copy">
                <span class="toggle-title">Custom Entities</span>
                <span class="toggle-desc">Add custom entities with a name and short description. The backend will expand them automatically.</span>
              </div>
              <button class="mini-action-btn" type="button" @click="addCustomEntity" :disabled="currentPhase < 2">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                Add Entity
              </button>
            </div>
            
            <div v-if="customEntities.length === 0" class="custom-entities-empty">
              No custom entities added yet.
            </div>
            
            <transition-group name="list" tag="div" class="entities-wrapper">
              <div v-for="(entity, idx) in customEntities" :key="idx" class="custom-entity-card">
                <div class="custom-entity-row">
                  <input
                    v-model="entity.name"
                    class="entity-input"
                    type="text"
                    placeholder="Entity Name (e.g. Technology Enthusiast)"
                    :disabled="currentPhase < 2"
                  >
                  <button class="remove-entity-btn" type="button" @click="removeCustomEntity(idx)" title="Remove Entity" :disabled="currentPhase < 2">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                  </button>
                </div>
                <textarea
                  v-model="entity.description"
                  class="entity-textarea custom-scrollbar"
                  rows="2"
                  placeholder="Behavior description (e.g. Always highly critical of new technology regulations.)"
                  :disabled="currentPhase < 2"
                ></textarea>
              </div>
            </transition-group>
          </div>
          
          <button 
            class="action-btn" 
            :disabled="currentPhase < 2 || creatingSimulation"
            @click="handleEnterEnvSetup"
          >
            <span class="btn-content">
              <span v-if="creatingSimulation" class="spinner-sm white"></span>
              {{ creatingSimulation ? 'Creating...' : 'Enter Environment Setup' }}
              <svg v-if="!creatingSimulation" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
            </span>
          </button>
        </div>
      </div>
    </div>

    <div class="system-logs">
      <div class="log-header">
        <div class="log-title-group">
          <div class="status-dot pulsing"></div>
          <span class="log-title">SYSTEM TERMINAL</span>
        </div>
        <span class="log-id">{{ projectData?.project_id || 'NO_PROJECT' }}</span>
      </div>
      <div class="log-content custom-scrollbar" ref="logContent">
        <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
          <span class="log-time">[{{ log.time }}]</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
        <div v-if="systemLogs.length === 0" class="log-empty">Waiting for system events...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { createSimulation } from '../api/simulation'

const router = useRouter()

const props = defineProps({
  currentPhase: { type: Number, default: 0 },
  projectData: Object,
  ontologyProgress: Object,
  buildProgress: Object,
  graphData: Object,
  systemLogs: { type: Array, default: () => [] }
})

defineEmits(['next-step'])

const selectedOntologyItem = ref(null)
const logContent = ref(null)
const creatingSimulation = ref(false)
const enableLinkedIn = ref(true)
const discoverRelatedEntities = ref(false)
const customEntities = ref([])

const addCustomEntity = () => {
  customEntities.value.push({ name: '', description: '' })
}

const removeCustomEntity = (index) => {
  customEntities.value.splice(index, 1)
}

const handleEnterEnvSetup = async () => {
  if (!props.projectData?.project_id || !props.projectData?.graph_id) {
    console.error('Missing project or graph data')
    return
  }
  
  creatingSimulation.value = true
  
  try {
    const cleanedCustomEntities = customEntities.value
      .map(entity => ({
        name: (entity.name || '').trim(),
        description: (entity.description || '').trim()
      }))
      .filter(entity => entity.name && entity.description)

    const res = await createSimulation({
      project_id: props.projectData.project_id,
      graph_id: props.projectData.graph_id,
      enable_twitter: true,
      enable_reddit: true,
      enable_linkedin: enableLinkedIn.value,
      discover_related_entities: discoverRelatedEntities.value,
      custom_entities: cleanedCustomEntities
    })
    
    if (res.success && res.data?.simulation_id) {
      router.push({
        name: 'Simulation',
        params: { simulationId: res.data.simulation_id }
      })
    } else {
      const errorMsg = `Failed to create simulation: ${res.error || 'Unknown error'}`
      console.error(errorMsg)
      alert(errorMsg)
    }
  } catch (err) {
    const errorMsg = `Simulation creation error: ${err.message}`
    console.error(errorMsg)
    alert(errorMsg)
  } finally {
    creatingSimulation.value = false
  }
}

const selectOntologyItem = (item, type) => {
  selectedOntologyItem.value = { ...item, itemType: type }
}

const graphStats = computed(() => {
  const nodes = props.graphData?.node_count || props.graphData?.nodes?.length || 0
  const edges = props.graphData?.edge_count || props.graphData?.edges?.length || 0
  const types = props.projectData?.ontology?.entity_types?.length || 0
  return { nodes, edges, types }
})

// Auto-scroll logs
watch(() => props.systemLogs.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})
</script>

<style scoped>
/* Prophesize AI Design System */
.workbench-panel {
  --primary: #2563EB;
  --primary-hover: #1D4ED8;
  --primary-light: #EFF6FF;
  --bg-main: #F8FAFC;
  --bg-card: #FFFFFF;
  --text-main: #0F172A;
  --text-muted: #64748B;
  --border-light: #E2E8F0;
  --border-focus: #CBD5E1;
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.02);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.05);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.08);
  --shadow-glow: 0 0 0 4px rgba(37, 99, 235, 0.1);
  --terminal-bg: #020617;
  
  height: 100%;
  background-color: var(--bg-main);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* Step Cards */
.step-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.step-card:hover {
  box-shadow: var(--shadow-md);
}

.step-card.active {
  border-color: var(--primary);
  box-shadow: var(--shadow-glow), var(--shadow-md);
}

.step-card.active::before {
  content: '';
  position: absolute;
  left: -1px;
  top: 24px;
  bottom: 24px;
  width: 4px;
  background: var(--primary);
  border-radius: 0 4px 4px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.step-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 28px;
  font-weight: 800;
  color: #E2E8F0;
  transition: color 0.3s ease;
  line-height: 1;
}

.step-card.active .step-num { color: var(--primary); }
.step-card.completed .step-num { color: #10B981; }

.step-title {
  font-weight: 800;
  font-size: 16px;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

/* Badges */
.badge {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge.success { background: #D1FAE5; color: #059669; }
.badge.processing { background: #DBEAFE; color: #1D4ED8; animation: pulse-opacity 2s infinite; }
.badge.accent { background: var(--primary); color: #FFF; }
.badge.pending { background: #F1F5F9; color: #64748B; }

@keyframes pulse-opacity {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #64748B;
  margin-bottom: 12px;
  background: #F8FAFC;
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #E2E8F0;
}

.description {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
}

/* Tags & Interactions */
.tags-container {
  margin-top: 20px;
  transition: opacity 0.3s;
}

.tags-container.dimmed {
  opacity: 0.3;
  pointer-events: none;
}

.tag-label {
  display: block;
  font-size: 10px;
  color: #64748B;
  margin-bottom: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.entity-tag {
  background: #F8FAFC;
  border: 1px solid var(--border-light);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  color: #0F172A;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: default;
}

.entity-tag.relation {
  background: #FFF;
  border-style: dashed;
  color: #475569;
}

.entity-tag.clickable {
  cursor: pointer;
}

.entity-tag.clickable:hover {
  background: #EFF6FF;
  border-color: #93C5FD;
  color: #1D4ED8;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* Ontology Detail Overlay (Glassmorphism) */
.ontology-detail-overlay {
  position: absolute;
  top: 80px; 
  left: 24px;
  right: 24px;
  bottom: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  z-index: 10;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0,0,0,0.06);
  background: rgba(248, 250, 252, 0.9);
}

.detail-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-type-badge {
  font-size: 10px;
  font-weight: 800;
  color: #FFF;
  padding: 4px 8px;
  border-radius: 6px;
  letter-spacing: 0.05em;
}
.detail-type-badge.entity { background: #3B82F6; }
.detail-type-badge.relation { background: #8B5CF6; }

.detail-name {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-main);
}

.close-btn {
  background: #FFF;
  border: 1px solid var(--border-light);
  color: #64748B;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.close-btn:hover {
  background: #F1F5F9;
  color: #0F172A;
  border-color: #CBD5E1;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.detail-desc {
  font-size: 13px;
  color: var(--text-main);
  line-height: 1.6;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px dashed var(--border-light);
}

.detail-section { margin-bottom: 24px; }

.section-label {
  display: block;
  font-size: 10px;
  font-weight: 800;
  color: #64748B;
  margin-bottom: 12px;
  letter-spacing: 0.05em;
}

.attr-list, .conn-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attr-item {
  font-size: 12px;
  padding: 12px;
  background: #FFF;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.attr-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.attr-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: var(--text-main);
}

.attr-type {
  color: #64748B;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  background: #F1F5F9;
  padding: 2px 6px;
  border-radius: 4px;
}

.attr-desc { color: var(--text-muted); line-height: 1.5; }

.example-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-tag {
  font-size: 12px;
  font-weight: 500;
  background: #F8FAFC;
  border: 1px solid var(--border-light);
  padding: 6px 12px;
  border-radius: 8px;
  color: #475569;
}

.conn-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  padding: 10px 12px;
  background: #F8FAFC;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
}

.conn-node { font-weight: 600; color: #0F172A; }
.conn-arrow { color: #94A3B8; font-family: 'JetBrains Mono', monospace; }

/* Step 02 Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  background: #F8FAFC;
  padding: 20px;
  border-radius: var(--radius-md);
  text-align: center;
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }

.stat-icon-wrapper {
  color: #3B82F6;
  margin-bottom: 12px;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 800;
  color: var(--text-main);
  font-family: 'JetBrains Mono', monospace;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 10px;
  color: #64748B;
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.05em;
}

/* Settings & Forms */
.settings-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.platform-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: #FFF;
  transition: border-color 0.2s;
}
.platform-toggle-row:hover { border-color: var(--border-focus); }

.toggle-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toggle-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}

.toggle-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  max-width: 360px;
}

/* Switch UI */
.switch-control {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.switch-control input { display: none; }

.switch-track {
  width: 44px;
  height: 24px;
  border-radius: 999px;
  background: #E2E8F0;
  position: relative;
  transition: background 0.3s ease;
}

.switch-track::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #FFF;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.switch-control input:checked + .switch-track { background: var(--primary); }
.switch-control input:checked + .switch-track::after { transform: translateX(20px); }
.switch-control input:disabled + .switch-track { opacity: 0.5; cursor: not-allowed; }

.switch-label {
  min-width: 24px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* Custom Entities Panel */
.custom-entities-panel {
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: #F8FAFC;
}

.custom-entities-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.custom-entities-empty {
  font-size: 13px;
  color: #94A3B8;
  padding: 20px 0 12px;
  text-align: center;
  border: 1px dashed #CBD5E1;
  border-radius: var(--radius-sm);
  background: #FFF;
  font-weight: 500;
}

.custom-entity-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  margin-top: 12px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: #FFF;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}
.custom-entity-card:hover {
  box-shadow: var(--shadow-md);
}

.custom-entity-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.entity-input, .entity-textarea {
  width: 100%;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 13px;
  color: var(--text-main);
  background: #FFF;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.entity-input::placeholder, .entity-textarea::placeholder { color: #94A3B8; font-weight: 500; }

.entity-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

.entity-input:focus, .entity-textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}
.entity-input:disabled, .entity-textarea:disabled {
  background: #F8FAFC;
  color: #94A3B8;
  cursor: not-allowed;
}

/* Buttons */
.mini-action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  background: #FFF;
  color: var(--text-main);
  white-space: nowrap;
  transition: all 0.2s;
  box-shadow: var(--shadow-sm);
}

.mini-action-btn:hover:not(:disabled) {
  background: #F1F5F9;
  border-color: #CBD5E1;
  transform: translateY(-1px);
}
.mini-action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.remove-entity-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FEF2F2;
  color: #EF4444;
  border: 1px solid #FCA5A5;
  border-radius: var(--radius-sm);
  width: 42px;
  height: 42px;
  cursor: pointer;
  transition: all 0.2s;
}

.remove-entity-btn:hover:not(:disabled) {
  background: #FEE2E2;
  color: #DC2626;
}
.remove-entity-btn:disabled { opacity: 0.5; cursor: not-allowed; border-color: transparent; }

.action-btn {
  width: 100%;
  background: var(--text-main);
  color: #FFF;
  border: none;
  padding: 16px;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
}

.action-btn:hover:not(:disabled) {
  background: #1E293B;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.3);
}

.action-btn:active:not(:disabled) {
  transform: translateY(0);
}

.action-btn:disabled {
  background: #E2E8F0;
  color: #94A3B8;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Loaders */
.progress-section {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--primary);
  margin-bottom: 16px;
  font-weight: 600;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid var(--primary-light);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
.spinner-sm.white {
  border-color: rgba(255,255,255,0.2);
  border-top-color: #FFF;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* System Terminal Logs */
.system-logs {
  background: var(--terminal-bg);
  color: #94A3B8;
  padding: 16px 24px;
  font-family: 'JetBrains Mono', monospace;
  border-top: 1px solid #1E293B;
  flex-shrink: 0;
  box-shadow: inset 0 4px 20px rgba(0,0,0,0.3);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 11px;
}

.log-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10B981;
  border-radius: 50%;
}
.status-dot.pulsing {
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
  animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.log-title {
  color: #38BDF8;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.log-id { color: #475569; font-weight: 600; }

.log-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 120px;
  overflow-y: auto;
  padding-right: 8px;
  scroll-behavior: smooth;
}

.log-line {
  font-size: 12px;
  display: flex;
  gap: 12px;
  line-height: 1.6;
}

.log-time {
  color: #10B981;
  min-width: 95px;
  opacity: 0.8;
}

.log-msg { color: #CBD5E1; word-break: break-all; }
.log-empty { font-size: 12px; color: #475569; font-style: italic; }

/* Vue Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(10px); }

.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateX(-10px); }
</style>