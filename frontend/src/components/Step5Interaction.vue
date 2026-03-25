<template>
  <div class="interaction-panel">
    <div class="main-split-layout">
      <div class="left-panel report-style custom-scrollbar" ref="leftPanel">
        <div v-if="reportOutline" class="report-content-wrapper">
          <div class="report-header-block">
            <div class="report-meta">
              <span class="report-tag">Prediction Context</span>
              <span class="report-id">REF: {{ reportId?.substring(0, 8) || '2024-X92' }}</span>
            </div>
            <h1 class="main-title">{{ reportOutline.title }}</h1>
            <p class="sub-title">{{ reportOutline.summary }}</p>
            <div class="header-divider"></div>
          </div>

          <div class="sections-list">
            <div 
              v-for="(section, idx) in reportOutline.sections" 
              :key="idx"
              class="report-section-item"
              :class="{ 
                'is-active': currentSectionIndex === idx + 1,
                'is-completed': isSectionCompleted(idx + 1),
                'is-pending': !isSectionCompleted(idx + 1) && currentSectionIndex !== idx + 1
              }"
            >
              <div class="section-header-row" @click="toggleSectionCollapse(idx)" :class="{ 'clickable': isSectionCompleted(idx + 1) }">
                <span class="section-number">{{ String(idx + 1).padStart(2, '0') }}</span>
                <h3 class="section-title">{{ section.title }}</h3>
                <svg 
                  v-if="isSectionCompleted(idx + 1)" 
                  class="collapse-icon" 
                  :class="{ 'is-collapsed': collapsedSections.has(idx) }"
                  viewBox="0 0 24 24" 
                  width="20" 
                  height="20" 
                  fill="none" 
                  stroke="currentColor" 
                  stroke-width="2.5"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
              
              <div class="section-body" v-show="!collapsedSections.has(idx)">
                <div v-if="generatedSections[idx + 1]" class="generated-content" v-html="renderMarkdown(generatedSections[idx + 1])"></div>
                
                <div v-else-if="currentSectionIndex === idx + 1" class="loading-state">
                  <div class="loading-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="10" stroke-width="4" stroke="#E2E8F0"></circle>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke-width="4" stroke="#3B82F6" stroke-linecap="round"></path>
                    </svg>
                  </div>
                  <span class="loading-text">Generating {{ section.title }}...</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!reportOutline" class="waiting-placeholder">
          <div class="waiting-animation">
            <div class="waiting-ring"></div>
            <div class="waiting-ring"></div>
            <div class="waiting-ring"></div>
          </div>
          <span class="waiting-text">Synchronizing Report Context...</span>
        </div>
      </div>

      <div class="right-panel" ref="rightPanel">
        <div class="action-bar">
          <div class="action-bar-header">
            <svg class="action-bar-icon" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <div class="action-bar-text">
              <span class="action-bar-title">Interaction Hub</span>
              <span class="action-bar-subtitle mono">{{ profiles.length }} active nodes available</span>
            </div>
          </div>
          <div class="action-bar-tabs">
            <button 
              class="tab-pill"
              :class="{ active: activeTab === 'chat' && chatTarget === 'report_agent' }"
              @click="selectReportAgentChat"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
              </svg>
              <span>Lead Analyst</span>
            </button>
            
            <div class="agent-dropdown" v-if="profiles.length > 0">
              <button 
                class="tab-pill agent-pill"
                :class="{ active: activeTab === 'chat' && chatTarget === 'agent' }"
                @click="toggleAgentDropdown"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span>{{ selectedAgent ? selectedAgent.username : 'Interview Entity' }}</span>
                <svg class="dropdown-arrow" :class="{ open: showAgentDropdown }" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
              <div v-if="showAgentDropdown" class="dropdown-menu custom-scrollbar">
                <div class="dropdown-header">Select Target Node</div>
                <div 
                  v-for="(agent, idx) in profiles" 
                  :key="idx"
                  class="dropdown-item"
                  @click="selectAgent(agent, idx)"
                >
                  <div class="agent-avatar mesh-gradient">{{ (agent.username || 'A')[0] }}</div>
                  <div class="agent-info">
                    <span class="agent-name">{{ agent.username }}</span>
                    <span class="agent-role">{{ agent.profession || 'Subject Expert' }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="tab-divider"></div>
            
            <button 
              class="tab-pill survey-pill"
              :class="{ active: activeTab === 'survey' }"
              @click="selectSurveyTab"
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
              </svg>
              <span>Batch Survey</span>
            </button>
          </div>
        </div>

        <div v-if="activeTab === 'chat'" class="chat-container">

          <div v-if="chatTarget === 'report_agent'" class="context-card report-agent-card">
            <div class="context-card-header">
              <div class="context-card-avatar Analyst">A</div>
              <div class="context-card-info">
                <div class="context-card-name">Report Analyst Bot</div>
                <div class="context-card-subtitle">AI synthesis engine for cross-graph reasoning and document verification.</div>
              </div>
              <button class="context-card-toggle" @click="showToolsDetail = !showToolsDetail">
                <svg :class="{ 'is-expanded': showToolsDetail }" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
            </div>
            <div v-if="showToolsDetail" class="context-card-body">
              <div class="tools-grid">
                <div class="tool-item tool-purple">
                  <div class="tool-icon-wrapper">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.5V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.5A7 7 0 0 0 12 2z"></path></svg>
                  </div>
                  <div class="tool-content">
                    <div class="tool-name">Deep Insight</div>
                    <div class="tool-desc">Extract analytical insights across entities.</div>
                  </div>
                </div>
                <div class="tool-item tool-blue">
                  <div class="tool-icon-wrapper">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                  </div>
                  <div class="tool-content">
                    <div class="tool-name">Panorama Search</div>
                    <div class="tool-desc">Wide-angle search across the knowledge graph.</div>
                  </div>
                </div>
                <div class="tool-item tool-orange">
                  <div class="tool-icon-wrapper">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                  </div>
                  <div class="tool-content">
                    <div class="tool-name">Quick Search</div>
                    <div class="tool-desc">Rapid retrieval of specific facts and relations.</div>
                  </div>
                </div>
                <div class="tool-item tool-green">
                  <div class="tool-icon-wrapper">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                  </div>
                  <div class="tool-content">
                    <div class="tool-name">Agent Interview</div>
                    <div class="tool-desc">Directly query multiple simulated entities.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="chatTarget === 'agent' && selectedAgent" class="context-card agent-card">
            <div class="context-card-header">
              <div class="context-card-avatar Agent">{{ (selectedAgent.username || 'A')[0] }}</div>
              <div class="context-card-info">
                <div class="context-card-name">{{ selectedAgent.username }}</div>
                <div class="context-card-meta">
                  <span v-if="selectedAgent.name" class="context-card-handle">@{{ selectedAgent.name }}</span>
                  <span class="context-card-profession">{{ selectedAgent.profession || 'Active Participant' }}</span>
                </div>
              </div>
              <button class="context-card-toggle" @click="showFullProfile = !showFullProfile">
                <svg :class="{ 'is-expanded': showFullProfile }" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
            </div>
            <div v-if="showFullProfile && selectedAgent.bio" class="context-card-body">
              <div class="profile-bio-box">
                <div class="profile-card-label">Entity Bio Context</div>
                <p>{{ selectedAgent.bio }}</p>
              </div>
            </div>
          </div>

          <div class="chat-messages custom-scrollbar" ref="chatMessages">
            <div v-if="chatHistory.length === 0" class="chat-empty">
              <div class="empty-icon-wrapper">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <p class="empty-text">
                {{ chatTarget === 'report_agent' ? 'Ask the Analyst about key findings, edge risks, or platform trends.' : `Directly interview ${selectedAgent?.username} regarding their motivations.` }}
              </p>
            </div>
            
            <div 
              v-for="(msg, idx) in chatHistory" 
              :key="idx"
              class="chat-message"
              :class="msg.role"
            >
              <div class="message-avatar" :class="{ 'analyst-avatar': chatTarget === 'report_agent' && msg.role === 'assistant' }">
                <span v-if="msg.role === 'user'">U</span>
                <span v-else>{{ msg.role === 'assistant' && chatTarget === 'report_agent' ? 'A' : (selectedAgent?.username?.[0] || 'E') }}</span>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="sender-name">
                    {{ msg.role === 'user' ? 'Operator' : (chatTarget === 'report_agent' ? 'Lead Analyst' : (selectedAgent?.username || 'Entity')) }}
                  </span>
                  <span class="message-time mono">{{ formatTime(msg.timestamp) }}</span>
                </div>
                <div class="message-bubble" v-html="renderMarkdown(msg.content)"></div>
                <div v-if="msg.role === 'assistant' && msg.sourceLabel" class="message-footer mono">{{ msg.sourceLabel }}</div>
              </div>
            </div>
            
            <div v-if="isSending" class="chat-message assistant">
              <div class="message-avatar" :class="{ 'analyst-avatar': chatTarget === 'report_agent' }">
                <span>{{ chatTarget === 'report_agent' ? 'A' : (selectedAgent?.username?.[0] || 'E') }}</span>
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <textarea 
              v-model="chatInput"
              class="chat-input custom-scrollbar"
              placeholder="Enter directive or query..."
              @keydown.enter.exact.prevent="sendMessage"
              :disabled="isSending || (!selectedAgent && chatTarget === 'agent')"
              rows="1"
              ref="chatInputRef"
            ></textarea>
            <button 
              class="send-btn"
              @click="sendMessage"
              :disabled="!chatInput.trim() || isSending || (!selectedAgent && chatTarget === 'agent')"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="activeTab === 'survey'" class="survey-container">
          <div class="survey-setup">
            <div class="setup-section scrollable">
              <div class="section-header">
                <span class="section-title">Select Target Nodes</span>
                <span class="selection-count mono">{{ selectedAgents.size }} / {{ profiles.length }} Selected</span>
              </div>
              <div class="agents-grid custom-scrollbar">
                <label 
                  v-for="(agent, idx) in profiles" 
                  :key="idx"
                  class="agent-checkbox"
                  :class="{ checked: selectedAgents.has(idx) }"
                >
                  <input 
                    type="checkbox" 
                    :checked="selectedAgents.has(idx)"
                    @change="toggleAgentSelection(idx)"
                  >
                  <div class="checkbox-avatar">{{ (agent.username || 'A')[0] }}</div>
                  <div class="checkbox-info">
                    <span class="checkbox-name">{{ agent.username }}</span>
                    <span class="checkbox-role">{{ agent.profession || 'Subject Expert' }}</span>
                  </div>
                  <div class="checkbox-indicator">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="3">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                </label>
              </div>
              <div class="selection-actions">
                <button class="action-btn-small" @click="selectAllAgents">Select All</button>
                <div class="action-divider"></div>
                <button class="action-btn-small" @click="clearAgentSelection">Reset Selection</button>
              </div>
            </div>

            <div class="setup-section bottom-section">
              <div class="section-header">
                <span class="section-title">Common Query Directive</span>
              </div>
              <textarea 
                v-model="surveyQuestion"
                class="survey-input custom-scrollbar"
                placeholder="Submit a common prompt to all selected nodes..."
                rows="3"
              ></textarea>
              
              <button 
                class="survey-submit-btn"
                :disabled="selectedAgents.size === 0 || !surveyQuestion.trim() || isSurveying"
                @click="submitSurvey"
              >
                <span v-if="isSurveying" class="loading-spinner-small"></span>
                <span>{{ isSurveying ? 'Extracting Intelligence...' : 'Dispatch Batch Survey' }}</span>
              </button>
            </div>
          </div>

          <div v-if="surveyResults.length > 0" class="survey-results custom-scrollbar">
            <div class="results-header">
              <span class="results-title">Response Synthesis</span>
              <span class="results-count mono">{{ surveyResults.length }} responses logged</span>
            </div>
            <div class="results-list">
              <div 
                v-for="(result, idx) in surveyResults" 
                :key="idx"
                class="result-card"
              >
                <div class="result-card-header">
                  <div class="result-avatar">{{ (result.agent_name || 'A')[0] }}</div>
                  <div class="result-info">
                    <span class="result-name">{{ result.agent_name }}</span>
                    <span class="result-role">{{ result.profession || 'Verified Subject' }}</span>
                  </div>
                </div>
                <div class="result-body">
                  <div class="result-question">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                      <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    <span>{{ result.question }}</span>
                  </div>
                  <div class="result-answer" v-html="renderMarkdown(result.answer)"></div>
                </div>
                <div v-if="result.sourceLabel" class="result-footer mono">{{ result.sourceLabel }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="console-logs">
      <div class="log-header">
        <div class="log-title-group">
          <div class="status-dot pulsing"></div>
          <span class="log-title">AGENT CONSOLE</span>
        </div>
        <span class="log-id">{{ reportId || 'NO_REPORT_LINK' }}</span>
      </div>
      <div class="log-content custom-scrollbar" ref="logContent">
        <div class="log-line" v-for="(log, idx) in consoleLogs" :key="idx">
          <span class="log-msg" :class="getLogLevelClass(log)">{{ log }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { chatWithReport, getReport, getAgentLog, getConsoleLog } from '../api/report'
import { interviewAgents, getSimulationProfilesRealtime } from '../api/simulation'

const props = defineProps({
  reportId: String,
  simulationId: String
})

const emit = defineEmits(['add-log', 'update-status'])

// State
const activeTab = ref('chat')
const chatTarget = ref('report_agent')
const showAgentDropdown = ref(false)
const selectedAgent = ref(null)
const selectedAgentIndex = ref(null)
const showFullProfile = ref(true)
const showToolsDetail = ref(true)

// Chat State
const chatInput = ref('')
const chatHistory = ref([])
const chatHistoryCache = ref({}) // Cache all conversation records: { 'report_agent': [], 'agent_0': [], 'agent_1': [], ... }
const isSending = ref(false)
const chatMessages = ref(null)
const chatInputRef = ref(null)

// Survey State
const selectedAgents = ref(new Set())
const surveyQuestion = ref('')
const surveyResults = ref([])
const isSurveying = ref(false)

// Report Data
const reportOutline = ref(null)
const generatedSections = ref({})
const collapsedSections = ref(new Set())
const currentSectionIndex = ref(null)
const profiles = ref([])
const consoleLogs = ref([])
const agentLogLine = ref(0)
const consoleLogLine = ref(0)

// Helper Methods
const isSectionCompleted = (sectionIndex) => {
  return !!generatedSections.value[sectionIndex]
}

// Refs
const leftPanel = ref(null)
const rightPanel = ref(null)
const logContent = ref(null)

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

const toggleSectionCollapse = (idx) => {
  if (!generatedSections.value[idx + 1]) return
  const newSet = new Set(collapsedSections.value)
  if (newSet.has(idx)) {
    newSet.delete(idx)
  } else {
    newSet.add(idx)
  }
  collapsedSections.value = newSet
}

const selectReportAgentChat = () => {
  // Save current conversation records
  saveChatHistory()
  
  activeTab.value = 'chat'
  chatTarget.value = 'report_agent'
  selectedAgent.value = null
  selectedAgentIndex.value = null
  showAgentDropdown.value = false
  
  // Restore Report Agent conversation records
  chatHistory.value = chatHistoryCache.value['report_agent'] || []
}

const selectSurveyTab = () => {
  activeTab.value = 'survey'
  selectedAgent.value = null
  selectedAgentIndex.value = null
  showAgentDropdown.value = false
}

const toggleAgentDropdown = () => {
  showAgentDropdown.value = !showAgentDropdown.value
  if (showAgentDropdown.value) {
    activeTab.value = 'chat'
    chatTarget.value = 'agent'
  }
}

const selectAgent = (agent, idx) => {
  saveChatHistory()
  selectedAgent.value = agent
  selectedAgentIndex.value = idx
  chatTarget.value = 'agent'
  showAgentDropdown.value = false
  chatHistory.value = chatHistoryCache.value[`agent_${idx}`] || []
  addLog(`Connected to entity: ${agent.username}`)
}

const saveChatHistory = () => {
  if (chatHistory.value.length === 0) return
  if (chatTarget.value === 'report_agent') {
    chatHistoryCache.value['report_agent'] = [...chatHistory.value]
  } else if (selectedAgentIndex.value !== null) {
    chatHistoryCache.value[`agent_${selectedAgentIndex.value}`] = [...chatHistory.value]
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour12: false, hour: '2-digit', minute: '2-digit'
    })
  } catch { return '' }
}

const renderMarkdown = (content) => {
  if (!content) return ''
  let processedContent = content.replace(/^##\s+.+\n+/, '')
  let html = processedContent.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
  html = html.replace(/^#### (.+)$/gm, '<h5 class="md-h5">$1</h5>')
  html = html.replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2 class="md-h2">$1</h2>')
  html = html.replace(/^> (.+)$/gm, '<blockquote class="md-quote">$1</blockquote>')
  html = html.replace(/^(\s*)- (.+)$/gm, (match, indent, text) => `<li class="md-li" data-level="${Math.floor(indent.length / 2)}">${text}</li>`)
  html = html.replace(/^(\s*)(\d+)\. (.+)$/gm, (match, indent, num, text) => `<li class="md-oli" data-level="${Math.floor(indent.length / 2)}">${text}</li>`)
  html = html.replace(/(<li class="md-li"[^>]*>.*?<\/li>\s*)+/g, '<ul class="md-ul">$&</ul>')
  html = html.replace(/(<li class="md-oli"[^>]*>.*?<\/li>\s*)+/g, '<ol class="md-ol">$&</ol>')
  html = html.replace(/<\/li>\s+<li/g, '</li><li')
  html = html.replace(/<ul class="md-ul">\s+/g, '<ul class="md-ul">')
  html = html.replace(/<ol class="md-ol">\s+/g, '<ol class="md-ol">')
  html = html.replace(/\s+<\/ul>/g, '</ul>')
  html = html.replace(/\s+<\/ol>/g, '</ol>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/_(.+?)_/g, '<em>$1</em>')
  html = html.replace(/^---$/gm, '<hr class="md-hr">')
  html = html.replace(/\n\n/g, '</p><p class="md-p">')
  html = html.replace(/\n/g, '<br>')
  html = '<p class="md-p">' + html + '</p>'
  html = html.replace(/<p class="md-p"><\/p>/g, '')
  html = html.replace(/<p class="md-p">(<h[2-5])/g, '$1')
  html = html.replace(/(<\/h[2-5]>)<\/p>/g, '$1')
  html = html.replace(/<p class="md-p">(<ul|<ol|<blockquote|<pre|<hr)/g, '$1')
  html = html.replace(/(<\/ul>|<\/ol>|<\/blockquote>|<\/pre>)<\/p>/g, '$1')
  html = html.replace(/<br>\s*(<ul|<ol|<blockquote)/g, '$1')
  html = html.replace(/(<\/ul>|<\/ol>|<\/blockquote>)\s*<br>/g, '$1')
  html = html.replace(/<p class="md-p">(<br>\s*)+(<ul|<ol|<blockquote|<pre|<hr)/g, '$2')
  html = html.replace(/(<br>\s*){2,}/g, '<br>')
  html = html.replace(/(<\/ol>|<\/ul>|<\/blockquote>)<br>(<p|<div)/g, '$1$2')
  const tokens = html.split(/(<ol class="md-ol">(?:<li class="md-oli"[^>]*>[\s\S]*?<\/li>)+<\/ol>)/g)
  let olCounter = 0, inSequence = false
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].startsWith('<ol class="md-ol">')) {
      const liCount = (tokens[i].match(/<li class="md-oli"/g) || []).length
      if (liCount === 1) {
        olCounter++; if (olCounter > 1) tokens[i] = tokens[i].replace('<ol class="md-ol">', `<ol class="md-ol" start="${olCounter}">`)
        inSequence = true
      } else { olCounter = 0; inSequence = false }
    } else if (inSequence && /<h[2-5]/.test(tokens[i])) {
      olCounter = 0; inSequence = false
    }
  }
  return tokens.join('')
}

const getPlatformDisplayName = (platform) => {
  if (platform === 'twitter') return 'Info Plaza'
  if (platform === 'reddit') return 'Topic Community'
  if (platform === 'linkedin') return 'Professional Network'
  return platform || ''
}

const getLogLevelClass = (log) => {
  if (log.includes('ERROR') || log.includes('Error')) return 'error'
  if (log.includes('WARNING') || log.includes('Warning')) return 'warning'
  return ''
}

// Chat Methods
const sendMessage = async () => {
  if (!chatInput.value.trim() || isSending.value) return
  
  const message = chatInput.value.trim()
  chatInput.value = ''
  
  chatHistory.value.push({ role: 'user', content: message, timestamp: new Date().toISOString() })
  scrollToBottom()
  isSending.value = true
  
  try {
    if (chatTarget.value === 'report_agent') {
      addLog(`Sending to Analyst: ${message.substring(0, 50)}...`)
      const historyForApi = chatHistory.value.filter(msg => msg.role !== 'user' || msg.content !== message).slice(-10).map(msg => ({ role: msg.role, content: msg.content }))
      
      const res = await chatWithReport({
        simulation_id: props.simulationId,
        message: message,
        chat_history: historyForApi
      })
      
      if (res.success && res.data) {
        chatHistory.value.push({
          role: 'assistant',
          content: res.data.response || res.data.answer || 'No response received.',
          timestamp: new Date().toISOString(),
          sourceLabel: 'Report Analyst Bot'
        })
        addLog('Analyst replied')
      } else { throw new Error(res.error || 'Request failed') }
    } else {
      if (!selectedAgent.value || selectedAgentIndex.value === null) throw new Error('Please select an entity first')
      
      addLog(`Sending to ${selectedAgent.value.username}: ${message.substring(0, 50)}...`)
      let prompt = message
      if (chatHistory.value.length > 1) {
        const historyContext = chatHistory.value.filter(msg => msg.content !== message).slice(-6).map(msg => `${msg.role === 'user' ? 'Operator' : 'You'}: ${msg.content}`).join('\n')
        prompt = `Prior context:\n${historyContext}\n\nNew query: ${message}`
      }
      
      const res = await interviewAgents({
        simulation_id: props.simulationId,
        interviews: [{ agent_id: selectedAgentIndex.value, prompt: prompt }]
      })
      
      if (res.success && res.data) {
        const resultData = res.data.result || res.data
        const resultsDict = resultData.results || resultData
        let responseContent = null, responsePlatform = ''
        const agentId = selectedAgentIndex.value
        
        if (typeof resultsDict === 'object' && !Array.isArray(resultsDict)) {
          const redditKey = `reddit_${agentId}`, twitterKey = `twitter_${agentId}`, linkedinKey = `linkedin_${agentId}`
          const agentResult = resultsDict[redditKey] || resultsDict[twitterKey] || resultsDict[linkedinKey] || Object.values(resultsDict)[0]
          if (agentResult) {
            responseContent = agentResult.response || agentResult.answer
            responsePlatform = agentResult.platform || (resultsDict[redditKey] ? 'reddit' : resultsDict[twitterKey] ? 'twitter' : resultsDict[linkedinKey] ? 'linkedin' : '')
          }
        } else if (Array.isArray(resultsDict) && resultsDict.length > 0) {
          responseContent = resultsDict[0].response || resultsDict[0].answer
          responsePlatform = resultsDict[0].platform || ''
        }
        
        if (responseContent) {
          chatHistory.value.push({
            role: 'assistant',
            content: responseContent,
            timestamp: new Date().toISOString(),
            sourceLabel: `${getPlatformDisplayName(responsePlatform)}${selectedAgent.value?.username ? ` • ${selectedAgent.value.username}` : ''}`.trim()
          })
          addLog(`${selectedAgent.value.username} replied`)
        } else { throw new Error('No response data') }
      } else { throw new Error(res.error || 'Request failed') }
    }
  } catch (err) {
    addLog(`Send failed: ${err.message}`)
    chatHistory.value.push({ role: 'assistant', content: `System Error: ${err.message}`, timestamp: new Date().toISOString() })
  } finally {
    isSending.value = false
    scrollToBottom()
    saveChatHistory()
  }
}

const scrollToBottom = () => {
  nextTick(() => { if (chatMessages.value) chatMessages.value.scrollTop = chatMessages.value.scrollHeight })
}

// Survey Methods
const toggleAgentSelection = (idx) => {
  const newSet = new Set(selectedAgents.value)
  if (newSet.has(idx)) newSet.delete(idx)
  else newSet.add(idx)
  selectedAgents.value = newSet
}

const selectAllAgents = () => {
  const newSet = new Set()
  profiles.value.forEach((_, idx) => newSet.add(idx))
  selectedAgents.value = newSet
}

const clearAgentSelection = () => { selectedAgents.value = new Set() }

const submitSurvey = async () => {
  if (selectedAgents.value.size === 0 || !surveyQuestion.value.trim() || isSurveying.value) return
  isSurveying.value = true
  addLog(`Dispatching survey to ${selectedAgents.value.size} targets...`)
  
  try {
    const interviews = Array.from(selectedAgents.value).map(idx => ({ agent_id: idx, prompt: surveyQuestion.value.trim() }))
    const res = await interviewAgents({ simulation_id: props.simulationId, interviews: interviews })
    
    if (res.success && res.data) {
      const resultData = res.data.result || res.data
      const resultsDict = resultData.results || resultData
      const surveyResultsList = []
      
      for (const interview of interviews) {
        const agentIdx = interview.agent_id
        const agent = profiles.value[agentIdx]
        let responseContent = 'No Response', responsePlatform = ''
        
        if (typeof resultsDict === 'object' && !Array.isArray(resultsDict)) {
          const redditKey = `reddit_${agentIdx}`, twitterKey = `twitter_${agentIdx}`, linkedinKey = `linkedin_${agentIdx}`
          const agentResult = resultsDict[redditKey] || resultsDict[twitterKey] || resultsDict[linkedinKey]
          if (agentResult) {
            responseContent = agentResult.response || agentResult.answer || 'No Response'
            responsePlatform = agentResult.platform || (resultsDict[redditKey] ? 'reddit' : resultsDict[twitterKey] ? 'twitter' : resultsDict[linkedinKey] ? 'linkedin' : '')
          }
        } else if (Array.isArray(resultsDict)) {
          const matchedResult = resultsDict.find(r => r.agent_id === agentIdx)
          if (matchedResult) {
            responseContent = matchedResult.response || matchedResult.answer || 'No Response'
            responsePlatform = matchedResult.platform || ''
          }
        }
        
        surveyResultsList.push({
          agent_id: agentIdx,
          agent_name: agent?.username || `Agent ${agentIdx}`,
          profession: agent?.profession,
          question: surveyQuestion.value.trim(),
          answer: responseContent,
          sourceLabel: `${getPlatformDisplayName(responsePlatform)}${agent?.username ? ` • ${agent.username}` : ''}`.trim()
        })
      }
      
      surveyResults.value = surveyResultsList
      addLog(`Received ${surveyResults.value.length} responses`)
    } else { throw new Error(res.error || 'Request failed') }
  } catch (err) {
    addLog(`Survey dispatch failed: ${err.message}`)
  } finally { isSurveying.value = false }
}

const loadReportData = async () => {
  if (!props.reportId) return
  try {
    addLog(`Loading report context: ${props.reportId}`)
    const reportRes = await getReport(props.reportId)
    if (reportRes.success && reportRes.data) await loadAgentLogs()
  } catch (err) { addLog(`Failed to load report: ${err.message}`) }
}

const loadAgentLogs = async () => {
  if (!props.reportId) return
  try {
    const res = await getAgentLog(props.reportId, 0)
    if (res.success && res.data) {
      const logs = res.data.logs || []
      logs.forEach(log => {
        if (log.action === 'planning_complete' && log.details?.outline) reportOutline.value = log.details.outline
        if (log.action === 'section_complete' && log.section_index < 100 && log.details?.content) generatedSections.value[log.section_index] = log.details.content
      })
      addLog('Report context synchronized')
    }
  } catch (err) { addLog(`Failed to load report logs: ${err.message}`) }
}

const loadProfiles = async () => {
  if (!props.simulationId) return
  try {
    const res = await getSimulationProfilesRealtime(props.simulationId, 'reddit')
    if (res.success && res.data) {
      profiles.value = res.data.profiles || []
      addLog(`Loaded ${profiles.value.length} entities for interaction`)
    }
  } catch (err) { addLog(`Failed to load entities: ${err.message}`) }
}

let logTimer = null
const fetchConsoleLog = async () => {
  if (!props.reportId) return
  try {
    const res = await getConsoleLog(props.reportId, consoleLogLine.value)
    if (res.success && res.data.logs?.length) {
      consoleLogs.value.push(...res.data.logs)
      consoleLogLine.value += res.data.logs.length
      nextTick(() => { if (logContent.value) logContent.value.scrollTop = logContent.value.scrollHeight })
    }
  } catch (e) { console.warn('Terminal log fetch failed') }
}

const handleClickOutside = (e) => {
  const dropdown = document.querySelector('.agent-dropdown')
  if (dropdown && !dropdown.contains(e.target)) showAgentDropdown.value = false
}

onMounted(() => {
  addLog('Step 5 Deep Interaction Initialized')
  loadReportData()
  loadProfiles()
  document.addEventListener('click', handleClickOutside)
  if (props.reportId) logTimer = setInterval(fetchConsoleLog, 1500)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (logTimer) clearInterval(logTimer)
})

watch(() => props.reportId, (newId) => { if (newId) loadReportData() }, { immediate: true })
watch(() => props.simulationId, (newId) => { if (newId) loadProfiles() }, { immediate: true })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

.interaction-panel {
  --primary: #2563EB;
  --primary-hover: #1D4ED8;
  --bg-main: #F8FAFC;
  --bg-card: #FFFFFF;
  --text-main: #0F172A;
  --text-muted: #64748B;
  --border-light: #E2E8F0;
  --border-focus: #CBD5E1;
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.02);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.05);
  --shadow-glow: 0 0 0 4px rgba(37, 99, 235, 0.1);
  --primary-gradient: linear-gradient(135deg, #2563EB, #7C3AED);

  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  overflow: hidden;
}

/* Utility Classes */
.mono { font-family: 'JetBrains Mono', monospace; }
.mesh-gradient { background: var(--primary-gradient); }

/* Custom Scrollbars */
.custom-scrollbar::-webkit-scrollbar,
.left-panel::-webkit-scrollbar,
.dropdown-menu::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar,
.agents-grid::-webkit-scrollbar,
.survey-results::-webkit-scrollbar { width: 6px; }

.custom-scrollbar::-webkit-scrollbar-track,
.left-panel::-webkit-scrollbar-track,
.dropdown-menu::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track,
.agents-grid::-webkit-scrollbar-track,
.survey-results::-webkit-scrollbar-track { background: transparent; }

.custom-scrollbar::-webkit-scrollbar-thumb,
.left-panel::-webkit-scrollbar-thumb,
.dropdown-menu::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb,
.agents-grid::-webkit-scrollbar-thumb,
.survey-results::-webkit-scrollbar-thumb { background: var(--border-focus); border-radius: 10px; }

.custom-scrollbar::-webkit-scrollbar-thumb:hover,
.left-panel:hover::-webkit-scrollbar-thumb,
.dropdown-menu:hover::-webkit-scrollbar-thumb,
.chat-messages:hover::-webkit-scrollbar-thumb,
.agents-grid:hover::-webkit-scrollbar-thumb,
.survey-results:hover::-webkit-scrollbar-thumb { background: var(--text-muted); }

/* Main Split Layout */
.main-split-layout { flex: 1; display: flex; overflow: hidden; }

/* ==========================================================================
   LEFT PANEL (REPORT VIEW - SYNCED PERFECTLY WITH STEP 4)
   ========================================================================== */
.left-panel.report-style {
  width: 45%;
  min-width: 450px;
  background: var(--bg-card);
  border-right: 1px solid var(--border-light);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 40px 50px 60px 50px;
}

.report-content-wrapper { max-width: 800px; margin: 0 auto; width: 100%; }
.report-header-block { margin-bottom: 40px; }

.report-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.report-tag { background: var(--text-main); color: #FFFFFF; font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.05em; text-transform: uppercase; }
.report-id { font-size: 11px; color: var(--text-muted); font-weight: 700; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;}

.main-title { font-size: 28px; font-weight: 800; color: var(--text-main); line-height: 1.3; margin: 20px 0 12px 0; letter-spacing: -0.02em; }
.sub-title { font-size: 15px; color: var(--text-muted); line-height: 1.6; margin-bottom: 32px; font-weight: 500; }
.header-divider { height: 1px; background: var(--border-light); width: 100%; }

.sections-list { display: flex; flex-direction: column; gap: 32px; }
.report-section-item { display: flex; flex-direction: column; gap: 16px; }

.section-header-row { display: flex; align-items: baseline; gap: 16px; transition: all 0.2s ease; padding: 12px 16px; margin: -12px -16px; border-radius: var(--radius-md); }
.section-header-row.clickable { cursor: pointer; }
.section-header-row.clickable:hover { background: var(--bg-main); }

.collapse-icon { margin-left: auto; color: var(--text-muted); transition: transform 0.3s ease; flex-shrink: 0; align-self: center; }
.collapse-icon.is-collapsed { transform: rotate(-90deg); }

.section-number { font-size: 18px; color: var(--border-focus); font-weight: 800; transition: color 0.3s ease; letter-spacing: 0.05em;}
.section-title { font-size: 18px; font-weight: 800; color: var(--text-main); margin: 0; transition: color 0.3s ease; letter-spacing: -0.01em;}

.report-section-item.is-pending .section-number { color: var(--border-light); }
.report-section-item.is-pending .section-title { color: var(--text-muted); opacity: 0.5; }
.report-section-item.is-active .section-number, .report-section-item.is-completed .section-number { color: var(--border-focus); }
.report-section-item.is-active .section-title, .report-section-item.is-completed .section-title { color: var(--text-main); }

.section-body { padding-left: 40px; overflow: hidden; }

/* Generated Content - Modern Reading Experience */
.generated-content { font-size: 15px; line-height: 1.8; color: #334155; }
.generated-content :deep(p) { margin-bottom: 1.2em; }
.generated-content :deep(.md-h2), .generated-content :deep(.md-h3), .generated-content :deep(.md-h4) { color: var(--text-main); margin-top: 2em; margin-bottom: 1em; font-weight: 800; letter-spacing: -0.01em;}
.generated-content :deep(.md-h2) { font-size: 18px; border-bottom: 1px solid var(--border-light); padding-bottom: 10px; margin-top: 0;}
.generated-content :deep(.md-h3) { font-size: 16px; }
.generated-content :deep(.md-h4) { font-size: 15px; }
.generated-content :deep(.md-ul), .generated-content :deep(.md-ol) { padding-left: 24px; margin: 16px 0; }
.generated-content :deep(.md-li), .generated-content :deep(.md-oli) { margin: 8px 0; }
.generated-content :deep(.md-quote) { border-left: 4px solid var(--primary); padding-left: 20px; margin: 2em 0; color: #475569; font-style: italic; background: var(--bg-main); padding: 16px 20px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;}
.generated-content :deep(.code-block) { background: #0F172A; color: #F8FAFC; padding: 16px; border-radius: var(--radius-sm); font-family: 'JetBrains Mono', monospace; font-size: 13px; overflow-x: auto; margin: 1.5em 0; }
.generated-content :deep(.inline-code) { background: var(--bg-main); border: 1px solid var(--border-light); padding: 2px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--primary);}
.generated-content :deep(strong) { font-weight: 800; color: var(--text-main); }

/* Loading State */
.loading-state { display: flex; align-items: center; gap: 12px; color: var(--text-muted); font-size: 14px; margin-top: 8px; padding: 16px; background: var(--bg-main); border-radius: var(--radius-md); border: 1px dashed var(--border-focus);}
.loading-icon { width: 18px; height: 18px; animation: spin 1s linear infinite; display: flex; align-items: center; justify-content: center; }
.loading-text { font-size: 14px; font-weight: 600; color: var(--text-main); }
@keyframes spin { to { transform: rotate(360deg); } }

/* Waiting Placeholder */
.waiting-placeholder { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24px; padding: 40px; color: var(--text-muted); }
.waiting-animation { position: relative; width: 64px; height: 64px; }
.waiting-ring { position: absolute; inset: 0; border: 2px solid var(--primary); border-radius: 50%; opacity: 0; animation: radar-ripple 3s cubic-bezier(0.165, 0.84, 0.44, 1) infinite; }
.waiting-ring:nth-child(2) { animation-delay: 1s; }
.waiting-ring:nth-child(3) { animation-delay: 2s; }
@keyframes radar-ripple { 0% { transform: scale(0.1); opacity: 1; border-width: 4px; } 100% { transform: scale(1.5); opacity: 0; border-width: 0px; } }
.waiting-text { font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted);}

/* ==========================================================================
   RIGHT PANEL (INTERACTION HUB)
   ========================================================================== */
.right-panel { flex: 1; display: flex; flex-direction: column; background: var(--bg-main); overflow: hidden; }

/* Action Bar - Segmented Control */
.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  z-index: 20;
}

.action-bar-header { display: flex; align-items: center; gap: 12px; min-width: 160px; }
.action-bar-icon { color: var(--text-main); flex-shrink: 0; }
.action-bar-text { display: flex; flex-direction: column; gap: 2px; }
.action-bar-title { font-size: 14px; font-weight: 800; color: var(--text-main); letter-spacing: 0.05em; text-transform: uppercase; }
.action-bar-subtitle { font-size: 11px; color: var(--text-muted); }

.action-bar-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}

.tab-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.tab-pill:hover { background: #FFFFFF; color: var(--text-main); border-color: var(--border-focus); }
.tab-pill.active { background: var(--text-main); color: #FFFFFF; border-color: var(--text-main); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.tab-pill svg { flex-shrink: 0; opacity: 0.7; }
.tab-pill.active svg { opacity: 1; }

.tab-divider { width: 1px; height: 24px; background: var(--border-light); margin: 0 8px; }

.agent-pill { width: 220px; justify-content: space-between; }
.agent-pill span { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: left; }
.survey-pill { color: #059669; }
.survey-pill.active { background: #059669; color: #FFFFFF; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.2); border-color: #059669; }

/* Agent Dropdown */
.agent-dropdown { position: relative; }
.dropdown-arrow { margin-left: 4px; transition: transform 0.2s ease; opacity: 0.6; }
.dropdown-arrow.open { transform: rotate(180deg); }

.dropdown-menu {
  position: absolute;
  top: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 280px;
  background: #FFFFFF;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  max-height: 400px;
  overflow-y: auto;
  z-index: 100;
}

.dropdown-header { padding: 12px 16px; font-size: 10px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--bg-main);}
.dropdown-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; cursor: pointer; transition: background 0.15s ease; border-left: 3px solid transparent; }
.dropdown-item:hover { background: var(--bg-main); border-left-color: var(--text-main); }
.dropdown-item:first-of-type { margin-top: 4px; }
.dropdown-item:last-child { margin-bottom: 4px; }
.agent-avatar { width: 32px; height: 32px; min-width: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; color: #FFFFFF; flex-shrink: 0; box-shadow: var(--shadow-sm); }
.agent-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
.agent-name { font-size: 13px; font-weight: 700; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.agent-role { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Chat Architecture */
.chat-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* Premium Context Cards */
.context-card {
  margin: 20px 24px 0 24px;
  background: #FFFFFF;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  overflow: hidden;
  flex-shrink: 0;
}

.context-card-header { display: flex; align-items: center; gap: 14px; padding: 16px; }
.context-card-avatar {
  width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 800; color: #FFFFFF; flex-shrink: 0; box-shadow: var(--shadow-sm);
}
.context-card-avatar.Analyst { background: var(--primary-gradient); }
.context-card-avatar.Agent { background: var(--text-main); }

.context-card-info { flex: 1; min-width: 0; }
.context-card-name { font-size: 15px; font-weight: 800; color: var(--text-main); margin-bottom: 2px; }
.context-card-subtitle, .context-card-profession { font-size: 12px; color: var(--text-muted); line-height: 1.4; }
.context-card-profession { padding: 2px 8px; background: var(--bg-main); border-radius: 4px; font-weight: 600; border: 1px solid var(--border-light); display: inline-block; margin-top: 4px;}

.context-card-toggle { margin-left: auto; width: 32px; height: 32px; background: #FFFFFF; border: 1px solid var(--border-light); border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--text-muted); transition: all 0.2s ease; flex-shrink: 0;}
.context-card-toggle:hover { background: var(--bg-main); border-color: var(--border-focus); color: var(--text-main);}
.context-card-toggle svg { transition: transform 0.3s ease; }
.context-card-toggle svg.is-expanded { transform: rotate(180deg); }

.context-card-body { padding: 0 16px 16px 16px; }
.profile-bio-box { background: var(--bg-main); padding: 16px; border-radius: var(--radius-sm); border: 1px solid var(--border-light); }
.profile-card-label { font-size: 11px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;}
.profile-bio-box p { margin: 0; font-size: 13px; line-height: 1.6; color: #334155; }

/* Analyst Tools Grid */
.tools-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.tool-item { display: flex; gap: 10px; padding: 12px; background: #FFFFFF; border-radius: 10px; border: 1px solid var(--border-light); transition: all 0.2s ease; }
.tool-item:hover { box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); }
.tool-icon-wrapper { width: 32px; height: 32px; min-width: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.tool-purple .tool-icon-wrapper { background: rgba(139, 92, 246, 0.1); color: #8B5CF6; }
.tool-blue .tool-icon-wrapper { background: rgba(59, 130, 246, 0.1); color: #3B82F6; }
.tool-orange .tool-icon-wrapper { background: rgba(249, 115, 22, 0.1); color: #F97316; }
.tool-green .tool-icon-wrapper { background: rgba(34, 197, 94, 0.1); color: #22C55E; }
.tool-content { flex: 1; min-width: 0; }
.tool-name { font-size: 12px; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }
.tool-desc { font-size: 11px; color: var(--text-muted); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* Chat Messages */
.chat-messages { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 28px; }

.chat-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; color: var(--text-muted); }
.empty-icon-wrapper { opacity: 0.3; }
.empty-text { font-size: 14px; text-align: center; max-width: 300px; line-height: 1.6; font-weight: 500;}

.chat-message { display: flex; gap: 16px; width: 100%;}
.chat-message.user { flex-direction: row-reverse; }

.message-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.08);}
.chat-message.user .message-avatar { background: var(--text-main); color: #FFFFFF; }
.chat-message.assistant .message-avatar { background: var(--border-focus); color: var(--text-main); }
.chat-message.assistant .analyst-avatar { background: var(--primary-gradient); color: #FFFFFF; }

.message-content { max-width: 75%; display: flex; flex-direction: column; gap: 6px; }
.chat-message.user .message-content { align-items: flex-end; }

.message-header { display: flex; align-items: center; gap: 10px; margin-bottom: 2px;}
.chat-message.user .message-header { flex-direction: row-reverse; }
.sender-name { font-size: 12px; font-weight: 800; color: var(--text-main); }
.message-time { font-size: 10px; color: var(--text-muted); }

.message-bubble { padding: 14px 20px; border-radius: 16px; font-size: 14px; line-height: 1.6; }
.chat-message.user .message-bubble { background: var(--text-main); color: #FFFFFF; border-bottom-right-radius: 4px; box-shadow: 0 4px 10px rgba(15, 23, 42, 0.15);}
.chat-message.assistant .message-bubble { background: #FFFFFF; border: 1px solid var(--border-light); color: #334155; border-bottom-left-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); }

/* Markdown inside Chat */
.message-bubble :deep(.md-p) { margin: 0 0 12px 0; }
.message-bubble :deep(.md-p:last-child) { margin-bottom: 0; }
.message-bubble :deep(.md-ol), .message-bubble :deep(.md-ul) { padding-left: 20px; margin: 8px 0; }
.message-bubble :deep(.md-li), .message-bubble :deep(.md-oli) { margin: 4px 0; }
.message-bubble :deep(.md-quote) { border-left: 3px solid var(--border-focus); padding-left: 12px; margin: 12px 0; color: var(--text-muted); font-style: italic;}
.message-bubble :deep(strong) { font-weight: 700; color: var(--text-main); }
.chat-message.user .message-bubble :deep(strong) { color: #FFF; }

.message-footer { margin-top: 4px; font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

/* Typing Indicator */
.typing-indicator { display: flex; gap: 4px; padding: 14px 18px; background: #FFFFFF; border: 1px solid var(--border-light); border-radius: 16px; border-bottom-left-radius: 4px; }
.typing-indicator span { width: 6px; height: 6px; background: var(--text-muted); border-radius: 50%; animation: typing 1.4s infinite ease-in-out; }
.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-4px); } }

/* Chat Input */
.chat-input-area { padding: 20px 24px; background: #FFFFFF; border-top: 1px solid var(--border-light); display: flex; gap: 16px; align-items: flex-end; }
.chat-input { flex: 1; padding: 16px; font-size: 14px; border: 1px solid var(--border-light); border-radius: var(--radius-md); resize: none; transition: all 0.2s ease; background: var(--bg-main); line-height: 1.5;}
.chat-input:focus { outline: none; border-color: var(--primary); background: #FFFFFF; box-shadow: var(--shadow-glow); }
.chat-input:disabled { opacity: 0.6; cursor: not-allowed; }

.send-btn { 
  width: 54px; height: 54px; background: var(--text-main); color: #FFFFFF; border: none; border-radius: 14px; 
  cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  flex-shrink: 0;
}
.send-btn:hover:not(:disabled) { background: var(--primary); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25); }
.send-btn:disabled { background: var(--border-light); color: var(--text-muted); cursor: not-allowed; }

/* Batch Survey Architecture */
.survey-container { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.survey-setup { flex: 1; display: flex; flex-direction: column; padding: 24px 32px; border-bottom: 1px solid var(--border-light); overflow: hidden;}
.setup-section { margin-bottom: 32px; }
.setup-section.scrollable { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; margin-bottom: 24px; }
.setup-section.bottom-section { margin-bottom: 0; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.setup-section .section-header .section-title { font-size: 14px; font-weight: 800; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.05em; }
.selection-count { font-size: 11px; font-weight: 700; color: var(--text-muted); background: var(--bg-main); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-light);}

/* Interactive Entity Checkboxes */
.agents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; flex: 1; overflow-y: auto; padding: 4px; align-content: start; }
.agent-checkbox {
  display: flex; align-items: center; gap: 14px; padding: 14px; background: #FFFFFF; 
  border: 1px solid var(--border-light); border-radius: 12px; cursor: pointer; transition: all 0.25s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.agent-checkbox:hover { border-color: var(--border-focus); transform: translateY(-1px); box-shadow: var(--shadow-sm);}
.agent-checkbox.checked { background: #ECFDF5; border-color: #10B981; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15); }
.agent-checkbox input { display: none; }

.checkbox-avatar { width: 32px; height: 32px; border-radius: 8px; background: var(--bg-main); color: var(--text-main); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 800; flex-shrink: 0; border: 1px solid var(--border-light);}
.agent-checkbox.checked .checkbox-avatar { background: #10B981; color: #FFFFFF; border-color: #10B981;}
.checkbox-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px;}
.checkbox-name { font-size: 13px; font-weight: 700; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.checkbox-role { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.checkbox-indicator { width: 20px; height: 20px; border: 2px solid var(--border-focus); border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s ease; background: #FFF;}
.agent-checkbox.checked .checkbox-indicator { background: #10B981; border-color: #10B981; color: #FFFFFF; }
.checkbox-indicator svg { opacity: 0; transform: scale(0.5); transition: all 0.2s ease; }
.agent-checkbox.checked .checkbox-indicator svg { opacity: 1; transform: scale(1); }

.selection-actions { display: flex; gap: 12px; margin-top: 16px; align-items: center;}
.action-btn-small { background: #FFFFFF; border: 1px solid var(--border-light); padding: 6px 14px; border-radius: 8px; font-size: 11px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer; transition: all 0.2s ease; box-shadow: var(--shadow-sm);}
.action-btn-small:hover { border-color: var(--text-muted); color: var(--text-main); background: var(--bg-main); transform: translateY(-1px);}
.action-divider { width: 1px; height: 16px; background: var(--border-light); }

/* Survey Action Block */
.survey-input { width: 100%; padding: 16px; font-size: 14px; border: 1px solid var(--border-light); border-radius: var(--radius-md); resize: none; transition: all 0.2s ease; background: var(--bg-main); }
.survey-input:focus { outline: none; border-color: var(--primary); background: #FFFFFF; box-shadow: var(--shadow-glow);}

.survey-submit-btn {
  position: relative; width: 100%; padding: 18px; color: #FFFFFF; background: var(--text-main); 
  border: none; border-radius: 12px; font-weight: 800; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 20px; text-transform: uppercase; letter-spacing: 0.1em;
  z-index: 1; overflow: hidden;
}
.survey-submit-btn::before { content: ''; position: absolute; inset: 0; background: var(--primary-gradient); opacity: 0; transition: opacity 0.3s; z-index: -1;}
.survey-submit-btn:hover:not(:disabled)::before { opacity: 1; }
.survey-submit-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25); }
.survey-submit-btn:disabled { background: var(--border-light); color: var(--text-muted); cursor: not-allowed; }

/* Result Cards - Synthesis View */
.survey-results { flex: 1; overflow-y: auto; padding: 32px; background: var(--bg-main);}
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.results-title { font-size: 16px; font-weight: 800; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.05em;}
.results-count { font-size: 11px; font-weight: 700; color: var(--text-muted); background: #FFFFFF; border: 1px solid var(--border-light); padding: 4px 10px; border-radius: 6px;}
.results-list { display: flex; flex-direction: column; gap: 20px; }

.result-card { background: #FFFFFF; border: 1px solid var(--border-light); border-radius: var(--radius-lg); padding: 24px; box-shadow: var(--shadow-sm); }
.result-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--bg-main); }
.result-avatar { width: 40px; height: 40px; background: var(--text-main); color: #FFFFFF; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 800; flex-shrink: 0; box-shadow: var(--shadow-sm);}
.result-info { display: flex; flex-direction: column; gap: 2px; }
.result-name { font-size: 15px; font-weight: 800; color: var(--text-main); }
.result-role { font-size: 12px; color: var(--text-muted); }

.result-question { display: flex; align-items: flex-start; gap: 10px; padding: 14px 16px; background: var(--bg-main); border: 1px solid var(--border-light); border-radius: var(--radius-sm); margin-bottom: 16px; font-size: 13px; font-weight: 700; color: var(--text-muted); }
.result-question svg { flex-shrink: 0; margin-top: 2px; color: var(--text-muted);}
.result-answer { font-size: 14px; line-height: 1.7; color: #334155; }
.result-answer :deep(.md-p) { margin: 0 0 12px 0; }
.result-answer :deep(.md-p:last-child) { margin-bottom: 0; }

.result-footer { margin-top: 16px; padding-top: 12px; border-top: 1px dashed var(--border-light); font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;}

/* ----------------------------------------------------
   SOLID DARK TERMINAL (LOCKED TO PROPHEZE AI STYLE)
------------------------------------------------------- */
.console-logs {
  background-color: #0F172A !important;
  color: #94A3B8; 
  padding: 16px 24px;
  font-family: 'JetBrains Mono', ui-monospace, monospace; 
  border-top: 1px solid #1E293B; 
  flex-shrink: 0;
  box-shadow: 0 -4px 10px rgba(0,0,0,0.1); 
  position: relative;
  z-index: 30;
}

.log-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 11px; }
.log-title-group { display: flex; align-items: center; gap: 8px; }
.status-dot { width: 8px; height: 8px; background: #10B981; border-radius: 50%; }
.status-dot.pulsing { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); animation: pulse-green 2s infinite; }
@keyframes pulse-green { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }
.log-title { color: #38BDF8; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
.log-id { color: #475569; font-weight: 600; }
.log-content { display: flex; flex-direction: column; gap: 6px; height: 110px; overflow-y: auto; padding-right: 8px; scroll-behavior: smooth; }
.log-line { font-size: 12px; line-height: 1.5; }
.log-msg { color: #F8FAFC !important; word-break: break-all; }
.log-msg.error { color: #EF4444 !important; }
.log-msg.warning { color: #F59E0B !important; }

/* Utilities */
.loading-spinner-small { width: 18px; height: 18px; border: 3px solid rgba(255,255,255,0.3); border-top-color: #FFF; border-radius: 50%; animation: spin 0.8s linear infinite; }
</style>