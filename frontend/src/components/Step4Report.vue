<template>
  <div class="report-panel">
    <div class="main-split-layout">
      <div class="left-panel report-style" ref="leftPanel">
        <div v-if="reportOutline" class="report-content-wrapper">
          <div class="report-header-block">
            <div class="report-meta">
              <span class="report-tag">Prediction Report</span>
              <span class="report-id">ID: {{ reportId || 'REF-2024-X92' }}</span>
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
                  stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </div>
              
              <div class="section-body" v-show="!collapsedSections.has(idx)">
                <div v-if="generatedSections[idx + 1]" class="generated-content" v-html="renderMarkdown(generatedSections[idx + 1])"></div>
                
                <div v-else-if="currentSectionIndex === idx + 1" class="loading-state">
                  <div class="loading-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="12" cy="12" r="10" stroke-width="4" stroke="#E5E7EB"></circle>
                      <path d="M12 2a10 10 0 0 1 10 10" stroke-width="4" stroke="#4B5563" stroke-linecap="round"></path>
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
          <span class="waiting-text">Waiting for Report Agent...</span>
        </div>
      </div>

      <div class="right-panel" ref="rightPanel">
        <div class="panel-header" :class="`panel-header--${activeStep.status}`" v-if="!isComplete">
          <span class="header-dot" v-if="activeStep.status === 'active'"></span>
          <span class="header-index mono">{{ activeStep.noLabel }}</span>
          <span class="header-title">{{ activeStep.title }}</span>
          <span class="header-meta mono" v-if="activeStep.meta">{{ activeStep.meta }}</span>
        </div>

        <div class="workflow-overview" v-if="agentLogs.length > 0 || reportOutline">
          <div class="workflow-metrics">
            <div class="metric">
              <span class="metric-label">Sections</span>
              <span class="metric-value mono">{{ completedSections }}/{{ totalSections }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Elapsed</span>
              <span class="metric-value mono">{{ formatElapsedTime }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Tools</span>
              <span class="metric-value mono">{{ totalToolCalls }}</span>
            </div>
            <div class="metric metric-right">
              <span class="metric-pill" :class="`pill--${statusClass}`">{{ statusText }}</span>
            </div>
          </div>

          <div class="workflow-steps" v-if="workflowSteps.length > 0">
            <div
              v-for="(step, sidx) in workflowSteps"
              :key="step.key"
              class="wf-step"
              :class="`wf-step--${step.status}`"
            >
              <div class="wf-step-connector">
                <div class="wf-step-dot"></div>
                <div class="wf-step-line" v-if="sidx < workflowSteps.length - 1"></div>
              </div>

              <div class="wf-step-content">
                <div class="wf-step-title-row">
                  <span class="wf-step-index mono">{{ step.noLabel }}</span>
                  <span class="wf-step-title">{{ step.title }}</span>
                  <span class="wf-step-meta mono" v-if="step.meta">{{ step.meta }}</span>
                </div>
              </div>
            </div>
          </div>

          <button v-if="isComplete" class="next-step-btn" @click="goToInteraction">
            <span>Enter Deep Interaction</span>
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>

          <div class="workflow-divider"></div>
        </div>

        <div class="workflow-timeline">
          <TransitionGroup name="timeline-item">
            <div 
              v-for="(log, idx) in displayLogs" 
              :key="log.timestamp + '-' + idx"
              class="timeline-item"
              :class="getTimelineItemClass(log, idx, displayLogs.length)"
            >
              <div class="timeline-connector">
                <div class="connector-dot" :class="getConnectorClass(log, idx, displayLogs.length)"></div>
                <div class="connector-line" v-if="idx < displayLogs.length - 1"></div>
              </div>
              
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="action-label">{{ getActionLabel(log.action) }}</span>
                  <span class="action-time">{{ formatTime(log.timestamp) }}</span>
                </div>
                
                <div class="timeline-body" :class="{ 'collapsed': isLogCollapsed(log) }" @click="toggleLogExpand(log)">
                  
                  <template v-if="log.action === 'report_start'">
                    <div class="info-row">
                      <span class="info-key">Simulation</span>
                      <span class="info-val mono">{{ log.details?.simulation_id }}</span>
                    </div>
                    <div class="info-row" v-if="log.details?.simulation_requirement">
                      <span class="info-key">Requirement</span>
                      <span class="info-val">{{ log.details.simulation_requirement }}</span>
                    </div>
                  </template>

                  <template v-if="log.action === 'planning_start'">
                    <div class="status-message planning">{{ log.details?.message }}</div>
                  </template>
                  <template v-if="log.action === 'planning_complete'">
                    <div class="status-message success">{{ log.details?.message }}</div>
                    <div class="outline-badge" v-if="log.details?.outline">
                      {{ log.details.outline.sections?.length || 0 }} sections planned
                    </div>
                  </template>

                  <template v-if="log.action === 'section_start'">
                    <div class="section-tag">
                      <span class="tag-num">#{{ log.section_index }}</span>
                      <span class="tag-title">{{ log.section_title }}</span>
                    </div>
                  </template>
                  
                  <template v-if="log.action === 'section_content'">
                    <div class="section-tag content-ready">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 20h9"></path>
                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                      </svg>
                      <span class="tag-title">{{ log.section_title }}</span>
                    </div>
                  </template>

                  <template v-if="log.action === 'section_complete'">
                    <div class="section-tag completed">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      <span class="tag-title">{{ log.section_title }}</span>
                    </div>
                  </template>

                  <template v-if="log.action === 'tool_call'">
                    <div class="tool-badge" :class="'tool-' + getToolColor(log.details?.tool_name)">
                      <svg v-if="getToolIcon(log.details?.tool_name) === 'lightbulb'" class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.5V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.5A7 7 0 0 0 12 2z"></path>
                      </svg>
                      <svg v-else-if="getToolIcon(log.details?.tool_name) === 'globe'" class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                      </svg>
                      <svg v-else-if="getToolIcon(log.details?.tool_name) === 'users'" class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path>
                      </svg>
                      <svg v-else-if="getToolIcon(log.details?.tool_name) === 'zap'" class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                      </svg>
                      <svg v-else-if="getToolIcon(log.details?.tool_name) === 'chart'" class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                      </svg>
                      <svg v-else-if="getToolIcon(log.details?.tool_name) === 'database'" class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                      </svg>
                      <svg v-else class="tool-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                      </svg>
                      {{ getToolDisplayName(log.details?.tool_name) }}
                    </div>
                    <div v-if="log.details?.parameters && expandedLogs.has(log.timestamp)" class="tool-params">
                      <pre>{{ formatParams(log.details.parameters) }}</pre>
                    </div>
                  </template>

                  <template v-if="log.action === 'tool_result'">
                    <div class="result-wrapper" :class="'result-' + log.details?.tool_name">
                      <div v-if="!['interview_agents', 'insight_forge', 'panorama_search', 'quick_search'].includes(log.details?.tool_name)" class="result-meta">
                        <span class="result-tool">{{ getToolDisplayName(log.details?.tool_name) }}</span>
                        <span class="result-size">{{ formatResultSize(log.details?.result_length) }}</span>
                      </div>
                      
                      <div v-if="!showRawResult[log.timestamp]" class="result-structured">
                        <template v-if="log.details?.tool_name === 'interview_agents'">
                          <InterviewDisplay :result="parseInterview(log.details.result)" :result-length="log.details?.result_length" />
                        </template>
                        
                        <template v-else-if="log.details?.tool_name === 'insight_forge'">
                          <InsightDisplay :result="parseInsightForge(log.details.result)" :result-length="log.details?.result_length" />
                        </template>
                        
                        <template v-else-if="log.details?.tool_name === 'panorama_search'">
                          <PanoramaDisplay :result="parsePanorama(log.details.result)" :result-length="log.details?.result_length" />
                        </template>
                        
                        <template v-else-if="log.details?.tool_name === 'quick_search'">
                          <QuickSearchDisplay :result="parseQuickSearch(log.details.result)" :result-length="log.details?.result_length" />
                        </template>
                        
                        <template v-else>
                          <pre class="raw-preview">{{ truncateText(log.details?.result, 300) }}</pre>
                        </template>
                      </div>
                      
                      <div v-else class="result-raw">
                        <pre>{{ log.details?.result }}</pre>
                      </div>
                    </div>
                  </template>

                  <template v-if="log.action === 'llm_response'">
                    <div class="llm-meta">
                      <span class="meta-tag">Iteration {{ log.details?.iteration }}</span>
                      <span class="meta-tag" :class="{ active: log.details?.has_tool_calls }">
                        Tools: {{ log.details?.has_tool_calls ? 'Yes' : 'No' }}
                      </span>
                      <span class="meta-tag" :class="{ active: log.details?.has_final_answer, 'final-answer': log.details?.has_final_answer }">
                        Final: {{ log.details?.has_final_answer ? 'Yes' : 'No' }}
                      </span>
                    </div>
                    <div v-if="log.details?.has_final_answer" class="final-answer-hint">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                      </svg>
                      <span>Section "{{ log.section_title }}" content generated</span>
                    </div>
                    <div v-if="expandedLogs.has(log.timestamp) && log.details?.response" class="llm-content">
                      <pre>{{ log.details.response }}</pre>
                    </div>
                  </template>

                  <template v-if="log.action === 'report_complete'">
                    <div class="complete-banner">
                      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                      <span>Report Generation Complete</span>
                    </div>
                  </template>
                </div>

                <div class="timeline-footer" v-if="log.elapsed_seconds || (log.action === 'tool_call' && log.details?.parameters) || log.action === 'tool_result' || (log.action === 'llm_response' && log.details?.response)">
                  <span v-if="log.elapsed_seconds" class="elapsed-badge">+{{ log.elapsed_seconds.toFixed(1) }}s</span>
                  <span v-else class="elapsed-placeholder"></span>
                  
                  <div class="footer-actions">
                    <button v-if="log.action === 'tool_call' && log.details?.parameters" class="action-btn" @click.stop="toggleLogExpand(log)">
                      {{ expandedLogs.has(log.timestamp) ? 'Hide Params' : 'Show Params' }}
                    </button>
                    
                    <button v-if="log.action === 'tool_result'" class="action-btn" @click.stop="toggleRawResult(log.timestamp, $event)">
                      {{ showRawResult[log.timestamp] ? 'Structured View' : 'Raw Output' }}
                    </button>
                    
                    <button v-if="log.action === 'llm_response' && log.details?.response" class="action-btn" @click.stop="toggleLogExpand(log)">
                      {{ expandedLogs.has(log.timestamp) ? 'Hide Response' : 'Show Response' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </TransitionGroup>

          <div v-if="agentLogs.length === 0 && !isComplete" class="workflow-empty">
            <div class="empty-pulse"></div>
            <span>Waiting for agent activity...</span>
          </div>
        </div>
      </div>
    </div>

    <div class="console-logs">
      <div class="log-header">
        <div class="log-title-group">
          <div class="status-dot pulsing"></div>
          <span class="log-title">CONSOLE OUTPUT</span>
        </div>
        <span class="log-id">{{ reportId || 'NO_REPORT' }}</span>
      </div>
      <div class="log-content" ref="logContent">
        <div class="log-line" v-for="(log, idx) in consoleLogs" :key="idx">
          <span class="log-msg" :class="getLogLevelClass(log)">{{ log }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, h, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { getAgentLog, getConsoleLog } from '../api/report'

const router = useRouter()

const props = defineProps({
  reportId: String,
  simulationId: String,
  systemLogs: Array
})

const emit = defineEmits(['add-log', 'update-status'])

// Navigation
const goToInteraction = () => {
  if (props.reportId) {
    router.push({ name: 'Interaction', params: { reportId: props.reportId } })
  }
}

// State
const agentLogs = ref([])
const consoleLogs = ref([])
const agentLogLine = ref(0)
const consoleLogLine = ref(0)
const reportOutline = ref(null)
const currentSectionIndex = ref(null)
const generatedSections = ref({})
const expandedContent = ref(new Set())
const expandedLogs = ref(new Set())
const collapsedSections = ref(new Set())
const isComplete = ref(false)
const startTime = ref(null)
const leftPanel = ref(null)
const rightPanel = ref(null)
const logContent = ref(null)
const showRawResult = reactive({})

// Toggle functions
const toggleRawResult = (timestamp, event) => {
  // Save button position relative to viewport
  const button = event?.target
  const buttonRect = button?.getBoundingClientRect()
  const buttonTopBeforeToggle = buttonRect?.top
  
  // Toggle state
  showRawResult[timestamp] = !showRawResult[timestamp]
  
  // After DOM update, adjust scroll position to keep button at the same location
  if (button && buttonTopBeforeToggle !== undefined && rightPanel.value) {
    nextTick(() => {
      const newButtonRect = button.getBoundingClientRect()
      const buttonTopAfterToggle = newButtonRect.top
      const scrollDelta = buttonTopAfterToggle - buttonTopBeforeToggle
      
      // Adjust scroll position
      rightPanel.value.scrollTop += scrollDelta
    })
  }
}

const toggleSectionContent = (idx) => {
  if (!generatedSections.value[idx + 1]) return
  const newSet = new Set(expandedContent.value)
  if (newSet.has(idx)) {
    newSet.delete(idx)
  } else {
    newSet.add(idx)
  }
  expandedContent.value = newSet
}

const toggleSectionCollapse = (idx) => {
  // Only completed sections can be collapsed
  if (!generatedSections.value[idx + 1]) return
  const newSet = new Set(collapsedSections.value)
  if (newSet.has(idx)) {
    newSet.delete(idx)
  } else {
    newSet.add(idx)
  }
  collapsedSections.value = newSet
}

const toggleLogExpand = (log) => {
  const newSet = new Set(expandedLogs.value)
  if (newSet.has(log.timestamp)) {
    newSet.delete(log.timestamp)
  } else {
    newSet.add(log.timestamp)
  }
  expandedLogs.value = newSet
}

const isLogCollapsed = (log) => {
  if (['tool_call', 'tool_result', 'llm_response'].includes(log.action)) {
    return !expandedLogs.value.has(log.timestamp)
  }
  return false
}

// Tool configurations with display names and colors
const toolConfig = {
  'insight_forge': {
    name: 'Deep Insight',
    color: 'purple',
    icon: 'lightbulb' 
  },
  'panorama_search': {
    name: 'Panorama Search',
    color: 'blue',
    icon: 'globe' 
  },
  'interview_agents': {
    name: 'Agent Interview',
    color: 'green',
    icon: 'users' 
  },
  'quick_search': {
    name: 'Quick Search',
    color: 'orange',
    icon: 'zap' 
  },
  'get_graph_statistics': {
    name: 'Graph Stats',
    color: 'cyan',
    icon: 'chart' 
  },
  'get_entities_by_type': {
    name: 'Entity Query',
    color: 'pink',
    icon: 'database' 
  }
}

const getToolDisplayName = (toolName) => {
  return toolConfig[toolName]?.name || toolName
}

const getToolColor = (toolName) => {
  return toolConfig[toolName]?.color || 'gray'
}

const getToolIcon = (toolName) => {
  return toolConfig[toolName]?.icon || 'tool'
}

// English+Chinese Compatible Parsers
const parseInsightForge = (text) => {
  const result = {
    query: '', simulationRequirement: '',
    stats: { facts: 0, entities: 0, relationships: 0 },
    subQueries: [], facts: [], entities: [], relations: []
  }
  try {
    const queryMatch = text.match(/(?:Analysis Question|Query|分析问题):\s*(.+?)(?:\n|$)/i)
    if (queryMatch) result.query = queryMatch[1].trim()
    
    const reqMatch = text.match(/(?:Prediction Scenario|Simulation Requirement|预测场景):\s*(.+?)(?:\n|$)/i)
    if (reqMatch) result.simulationRequirement = reqMatch[1].trim()
    
    const factMatch = text.match(/(?:Related Prediction Facts|Key Facts|相关预测事实):\s*(\d+)/i)
    const entityMatch = text.match(/(?:Involved Entities|Core Entities|涉及实体):\s*(\d+)/i)
    const relMatch = text.match(/(?:Relationship Chains|Relations|关系链):\s*(\d+)/i)
    if (factMatch) result.stats.facts = parseInt(factMatch[1])
    if (entityMatch) result.stats.entities = parseInt(entityMatch[1])
    if (relMatch) result.stats.relationships = parseInt(relMatch[1])
    
    const subQSection = text.match(/### (?:Sub-questions for Analysis|Sub-questions|分析的子问题)\n([\s\S]*?)(?=\n###|$)/i)
    if (subQSection) {
      const lines = subQSection[1].split('\n').filter(l => l.match(/^\d+\./))
      result.subQueries = lines.map(l => l.replace(/^\d+\.\s*/, '').trim()).filter(Boolean)
    }
    
    const factsSection = text.match(/### (?:\[?Key Facts\]?|【关键事实】)[\s\S]*?\n([\s\S]*?)(?=\n###|$)/i)
    if (factsSection) {
      const lines = factsSection[1].split('\n').filter(l => l.match(/^\d+\./))
      result.facts = lines.map(l => {
        const match = l.match(/^\d+\.\s*"?(.+?)"?\s*$/)
        return match ? match[1].replace(/^"|"$/g, '').trim() : l.replace(/^\d+\.\s*/, '').trim()
      }).filter(Boolean)
    }
    
    const entitySection = text.match(/### (?:\[?Core Entities\]?|【核心实体】)\n([\s\S]*?)(?=\n###|$)/i)
    if (entitySection) {
      const entityBlocks = entitySection[1].split(/\n(?=- \*\*)/).filter(b => b.trim().startsWith('- **'))
      result.entities = entityBlocks.map(block => {
        const nameMatch = block.match(/^-\s*\*\*(.+?)\*\*\s*\((.+?)\)/)
        const summaryMatch = block.match(/(?:Summary|摘要):\s*"?(.+?)"?(?:\n|$)/i)
        const relatedMatch = block.match(/(?:Related Facts|相关事实):\s*(\d+)/i)
        return {
          name: nameMatch ? nameMatch[1].trim() : '',
          type: nameMatch ? nameMatch[2].trim() : '',
          summary: summaryMatch ? summaryMatch[1].trim() : '',
          relatedFactsCount: relatedMatch ? parseInt(relatedMatch[1]) : 0
        }
      }).filter(e => e.name)
    }
    
    const relSection = text.match(/### (?:\[?Relationship Chains\]?|【关系链】)\n([\s\S]*?)(?=\n###|$)/i)
    if (relSection) {
      const lines = relSection[1].split('\n').filter(l => l.trim().startsWith('-'))
      result.relations = lines.map(l => {
        const match = l.match(/^-\s*(.+?)\s*--\[(.+?)\]-->\s*(.+)$/)
        if (match) return { source: match[1].trim(), relation: match[2].trim(), target: match[3].trim() }
        return null
      }).filter(Boolean)
    }
  } catch (e) { console.warn('Parse insight_forge failed:', e) }
  return result
}

const parsePanorama = (text) => {
  const result = {
    query: '', stats: { nodes: 0, edges: 0, activeFacts: 0, historicalFacts: 0 },
    activeFacts: [], historicalFacts: [], entities: []
  }
  try {
    const queryMatch = text.match(/(?:Query|Search|查询):\s*(.+?)(?:\n|$)/i)
    if (queryMatch) result.query = queryMatch[1].trim()
    
    const nodesMatch = text.match(/(?:Total Nodes|总节点数):\s*(\d+)/i)
    const edgesMatch = text.match(/(?:Total Edges|总边数):\s*(\d+)/i)
    const activeMatch = text.match(/(?:Current Active Facts|Active Memories|当前有效事实):\s*(\d+)/i)
    const histMatch = text.match(/(?:Historical\/Expired Facts|Historical Memories|历史\/过期事实):\s*(\d+)/i)
    
    if (nodesMatch) result.stats.nodes = parseInt(nodesMatch[1])
    if (edgesMatch) result.stats.edges = parseInt(edgesMatch[1])
    if (activeMatch) result.stats.activeFacts = parseInt(activeMatch[1])
    if (histMatch) result.stats.historicalFacts = parseInt(histMatch[1])
    
    const activeSection = text.match(/### (?:\[?Current Active Facts\]?|Active Memories|【当前有效事实】)[\s\S]*?\n([\s\S]*?)(?=\n###|$)/i)
    if (activeSection) {
      const lines = activeSection[1].split('\n').filter(l => l.match(/^\d+\./))
      result.activeFacts = lines.map(l => l.replace(/^\d+\.\s*/, '').replace(/^"|"$/g, '').trim()).filter(Boolean)
    }
    
    const histSection = text.match(/### (?:\[?Historical\/Expired Facts\]?|Historical Memories|【历史\/过期事实】)[\s\S]*?\n([\s\S]*?)(?=\n###|$)/i)
    if (histSection) {
      const lines = histSection[1].split('\n').filter(l => l.match(/^\d+\./))
      result.historicalFacts = lines.map(l => l.replace(/^\d+\.\s*/, '').replace(/^"|"$/g, '').trim()).filter(Boolean)
    }
    
    const entitySection = text.match(/### (?:\[?Involved Entities\]?|Related Entities|【涉及实体】)\n([\s\S]*?)(?=\n###|$)/i)
    if (entitySection) {
      const lines = entitySection[1].split('\n').filter(l => l.trim().startsWith('-'))
      result.entities = lines.map(l => {
        const match = l.match(/^-\s*\*\*(.+?)\*\*\s*\((.+?)\)/)
        if (match) return { name: match[1].trim(), type: match[2].trim() }
        return null
      }).filter(Boolean)
    }
  } catch (e) { console.warn('Parse panorama failed:', e) }
  return result
}

const parseInterview = (text) => {
  const result = {
    topic: '', agentCount: '', successCount: 0, totalCount: 0,
    selectionReason: '', interviews: [], summary: ''
  }
  try {
    const topicMatch = text.match(/\*\*(?:Interview Topic|采访主题):\*\*\s*(.+?)(?:\n|$)/i)
    if (topicMatch) result.topic = topicMatch[1].trim()
    
    const countMatch = text.match(/\*\*(?:Interview Count|Interviewees|采访人数):\*\*\s*(\d+)\s*\/\s*(\d+)/i)
    if (countMatch) {
      result.successCount = parseInt(countMatch[1])
      result.totalCount = parseInt(countMatch[2])
      result.agentCount = `${countMatch[1]} / ${countMatch[2]}`
    }
    
    const reasonMatch = text.match(/### (?:Interviewee Selection Reasons|Selection Reason|采访对象选择理由)\n([\s\S]*?)(?=\n---\n|\n### (?:Interview Transcript|采访实录))/i)
    if (reasonMatch) result.selectionReason = reasonMatch[1].trim()
    
    const parseIndividualReasons = (reasonText) => {
      const reasons = {}
      if (!reasonText) return reasons
      const lines = reasonText.split(/\n+/)
      let currentName = null, currentReason = []
      
      for (const line of lines) {
        let headerMatch = line.match(/^\d+\.\s*\*\*([^*（(]+)(?:[（(]index\s*=?\s*\d+[)）])?\*\*[：:]\s*(.*)/)
        if (!headerMatch) headerMatch = line.match(/^-\s*(?:Select|选择)\s*([^（(]+)(?:[（(]index\s*=?\s*\d+[)）])?[：:]\s*(.*)/i)
        if (!headerMatch) headerMatch = line.match(/^-\s*\*\*([^*（(]+)(?:[（(]index\s*=?\s*\d+[)）])?\*\*[：:]\s*(.*)/)
        
        if (headerMatch) {
          if (currentName && currentReason.length > 0) reasons[currentName] = currentReason.join(' ').trim()
          currentName = headerMatch[1].trim()
          currentReason = headerMatch[2] ? [headerMatch[2].trim()] : []
        } else if (currentName && line.trim() && !line.match(/^(?:Not selected|In summary|Final selection|未选|综上|最终选择)/i)) {
          currentReason.push(line.trim())
        }
      }
      if (currentName && currentReason.length > 0) reasons[currentName] = currentReason.join(' ').trim()
      return reasons
    }
    
    const individualReasons = parseIndividualReasons(result.selectionReason)
    const interviewBlocks = text.split(/#### (?:Interview|采访) #\d+:/i).slice(1)
    
    interviewBlocks.forEach((block, index) => {
      const interview = {
        num: index + 1, title: '', name: '', role: '', bio: '',
        selectionReason: '', questions: [], twitterAnswer: '', redditAnswer: '', quotes: []
      }
      
      const titleMatch = block.match(/^(.+?)\n/)
      if (titleMatch) interview.title = titleMatch[1].trim()
      
      const nameRoleMatch = block.match(/\*\*(.+?)\*\*\s*\((.+?)\)/)
      if (nameRoleMatch) {
        interview.name = nameRoleMatch[1].trim()
        interview.role = nameRoleMatch[2].trim()
        interview.selectionReason = individualReasons[interview.name] || ''
      }
      
      const bioMatch = block.match(/_(?:Bio|Profile|简介):\s*([\s\S]*?)_\n/i)
      if (bioMatch) interview.bio = bioMatch[1].trim().replace(/\.\.\.$/, '...')
      
      const qMatch = block.match(/\*\*Q:\*\*\s*([\s\S]*?)(?=\n\n\*\*A:\*\*|\*\*A:\*\*)/)
      if (qMatch) {
        const qText = qMatch[1].trim()
        const questions = qText.split(/\n\d+\.\s+/).filter(q => q.trim())
        if (questions.length > 0) {
          const firstQ = qText.match(/^1\.\s+(.+)/)
          if (firstQ) interview.questions = [firstQ[1].trim(), ...questions.slice(1).map(q => q.trim())]
          else interview.questions = questions.map(q => q.trim())
        }
      }
      
      const answerMatch = block.match(/\*\*A:\*\*\s*([\s\S]*?)(?=\*\*(?:Key Quotes|关键引言)|$)/i)
      if (answerMatch) {
        const answerText = answerMatch[1].trim()
        const twitterMatch = answerText.match(/(?:\[Twitter Answer\]|\[Twitter Platform Answer\]|Twitter:|【Twitter平台回答】)\n?([\s\S]*?)(?=(?:\[Reddit|Reddit:|【Reddit)|$)/i)
        const redditMatch = answerText.match(/(?:\[Reddit Answer\]|\[Reddit Platform Answer\]|Reddit:|【Reddit平台回答】)\n?([\s\S]*?)$/i)
        
        if (twitterMatch) interview.twitterAnswer = twitterMatch[1].trim()
        if (redditMatch) interview.redditAnswer = redditMatch[1].trim()
        
        const noReplyRegex = /(?:No reply from this platform|\[No reply\]|（该平台未获得回复）|\(该平台未获得回复\))/i
        
        if (!twitterMatch && redditMatch) {
          if (interview.redditAnswer && !noReplyRegex.test(interview.redditAnswer)) interview.twitterAnswer = interview.redditAnswer
        } else if (twitterMatch && !redditMatch) {
          if (interview.twitterAnswer && !noReplyRegex.test(interview.twitterAnswer)) interview.redditAnswer = interview.twitterAnswer
        } else if (!twitterMatch && !redditMatch) {
          interview.twitterAnswer = answerText
        }
      }
      
      const quotesMatch = block.match(/\*\*(?:Key Quotes|关键引言):\*\*\n([\s\S]*?)(?=\n---|\n####|$)/i)
      if (quotesMatch) {
        const quotesText = quotesMatch[1]
        let quoteMatches = quotesText.match(/> "([^"]+)"/g)
        if (!quoteMatches) quoteMatches = quotesText.match(/> [\u201C""]([^\u201D""]+)[\u201D""]/g)
        if (quoteMatches) {
          interview.quotes = quoteMatches.map(q => q.replace(/^> [\u201C""]|[\u201D""]$/g, '').trim()).filter(q => q)
        }
      }
      
      if (interview.name || interview.title) result.interviews.push(interview)
    })
    
    const summaryMatch = text.match(/### (?:Interview Summary and Core Insights|Interview Summary|采访摘要与核心观点)\n([\s\S]*?)$/i)
    if (summaryMatch) result.summary = summaryMatch[1].trim()
  } catch (e) { console.warn('Parse interview failed:', e) }
  return result
}

const parseQuickSearch = (text) => {
  const result = { query: '', count: 0, facts: [], edges: [], nodes: [] }
  try {
    const queryMatch = text.match(/(?:Search Query|搜索查询):\s*(.+?)(?:\n|$)/i)
    if (queryMatch) result.query = queryMatch[1].trim()
    
    const countMatch = text.match(/(?:Found|找到)\s*(\d+)\s*(?:results|条)/i)
    if (countMatch) result.count = parseInt(countMatch[1])
    
    const factsSection = text.match(/### (?:Related Facts|相关事实):\n([\s\S]*)$/i)
    if (factsSection) {
      const lines = factsSection[1].split('\n').filter(l => l.match(/^\d+\./))
      result.facts = lines.map(l => l.replace(/^\d+\.\s*/, '').trim()).filter(Boolean)
    }
    
    const edgesSection = text.match(/### (?:Related Edges|Related Relations|相关边):\n([\s\S]*?)(?=\n###|$)/i)
    if (edgesSection) {
      const lines = edgesSection[1].split('\n').filter(l => l.trim().startsWith('-'))
      result.edges = lines.map(l => {
        const match = l.match(/^-\s*(.+?)\s*--\[(.+?)\]-->\s*(.+)$/)
        if (match) return { source: match[1].trim(), relation: match[2].trim(), target: match[3].trim() }
        return null
      }).filter(Boolean)
    }
    
    const nodesSection = text.match(/### (?:Related Nodes|相关节点):\n([\s\S]*?)(?=\n###|$)/i)
    if (nodesSection) {
      const lines = nodesSection[1].split('\n').filter(l => l.trim().startsWith('-'))
      result.nodes = lines.map(l => {
        const match = l.match(/^-\s*\*\*(.+?)\*\*\s*\((.+?)\)/)
        if (match) return { name: match[1].trim(), type: match[2].trim() }
        const simpleMatch = l.match(/^-\s*(.+)$/)
        if (simpleMatch) return { name: simpleMatch[1].trim(), type: '' }
        return null
      }).filter(Boolean)
    }
  } catch (e) { console.warn('Parse quick_search failed:', e) }
  return result
}

// ========== Sub Components ==========

// Insight Display Component - Enhanced with full data rendering (Interview-like style)
const InsightDisplay = {
  props: ['result', 'resultLength'],
  setup(props) {
    const activeTab = ref('facts') 
    const expandedFacts = ref(false)
    const expandedEntities = ref(false)
    const expandedRelations = ref(false)
    const INITIAL_SHOW_COUNT = 5
    
    const formatSize = (length) => {
      if (!length) return ''
      if (length >= 1000) return `${(length / 1000).toFixed(1)}k chars`
      return `${length} chars`
    }
    
    return () => h('div', { class: 'insight-display' }, [
      h('div', { class: 'insight-header' }, [
        h('div', { class: 'header-main' }, [
          h('div', { class: 'header-title' }, 'Deep Insight'),
          h('div', { class: 'header-stats' }, [
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.stats.facts || props.result.facts.length),
              h('span', { class: 'stat-label' }, 'Facts')
            ]),
            h('span', { class: 'stat-divider' }, '/'),
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.stats.entities || props.result.entities.length),
              h('span', { class: 'stat-label' }, 'Entities')
            ]),
            h('span', { class: 'stat-divider' }, '/'),
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.stats.relationships || props.result.relations.length),
              h('span', { class: 'stat-label' }, 'Relations')
            ]),
            props.resultLength && h('span', { class: 'stat-divider' }, '·'),
            props.resultLength && h('span', { class: 'stat-size' }, formatSize(props.resultLength))
          ])
        ]),
        props.result.query && h('div', { class: 'header-topic' }, props.result.query),
        props.result.simulationRequirement && h('div', { class: 'header-scenario' }, [
          h('span', { class: 'scenario-label' }, 'Prediction Scenario: '),
          h('span', { class: 'scenario-text' }, props.result.simulationRequirement)
        ])
      ]),
      
      h('div', { class: 'insight-tabs' }, [
        h('button', {
          class: ['insight-tab', { active: activeTab.value === 'facts' }],
          onClick: () => { activeTab.value = 'facts' }
        }, [
          h('span', { class: 'tab-label' }, `Current Key Memories (${props.result.facts.length})`)
        ]),
        h('button', {
          class: ['insight-tab', { active: activeTab.value === 'entities' }],
          onClick: () => { activeTab.value = 'entities' }
        }, [
          h('span', { class: 'tab-label' }, `Core Entities (${props.result.entities.length})`)
        ]),
        h('button', {
          class: ['insight-tab', { active: activeTab.value === 'relations' }],
          onClick: () => { activeTab.value = 'relations' }
        }, [
          h('span', { class: 'tab-label' }, `Relationship Chains (${props.result.relations.length})`)
        ]),
        props.result.subQueries.length > 0 && h('button', {
          class: ['insight-tab', { active: activeTab.value === 'subqueries' }],
          onClick: () => { activeTab.value = 'subqueries' }
        }, [
          h('span', { class: 'tab-label' }, `Sub Questions (${props.result.subQueries.length})`)
        ])
      ]),
      
      h('div', { class: 'insight-content' }, [
        activeTab.value === 'facts' && props.result.facts.length > 0 && h('div', { class: 'facts-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Latest Key Facts from Temporal Memory'),
            h('span', { class: 'panel-count' }, `${props.result.facts.length} Total`)
          ]),
          h('div', { class: 'facts-list' },
            (expandedFacts.value ? props.result.facts : props.result.facts.slice(0, INITIAL_SHOW_COUNT)).map((fact, i) => 
              h('div', { class: 'fact-item', key: i }, [
                h('span', { class: 'fact-number' }, i + 1),
                h('div', { class: 'fact-content' }, fact)
              ])
            )
          ),
          props.result.facts.length > INITIAL_SHOW_COUNT && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedFacts.value = !expandedFacts.value }
          }, expandedFacts.value ? `Collapse ▲` : `Expand All (${props.result.facts.length}) ▼`)
        ]),

        activeTab.value === 'entities' && props.result.entities.length > 0 && h('div', { class: 'entities-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Core Entities'),
            h('span', { class: 'panel-count' }, `${props.result.entities.length} Total`)
          ]),
          h('div', { class: 'entities-grid' },
            (expandedEntities.value ? props.result.entities : props.result.entities.slice(0, 12)).map((entity, i) => 
              h('div', { class: 'entity-tag', key: i, title: entity.summary || '' }, [
                h('span', { class: 'entity-name' }, entity.name),
                h('span', { class: 'entity-type' }, entity.type),
                entity.relatedFactsCount > 0 && h('span', { class: 'entity-fact-count' }, `${entity.relatedFactsCount} items`)
              ])
            )
          ),
          props.result.entities.length > 12 && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedEntities.value = !expandedEntities.value }
          }, expandedEntities.value ? `Collapse ▲` : `Expand All (${props.result.entities.length}) ▼`)
        ]),

        activeTab.value === 'relations' && props.result.relations.length > 0 && h('div', { class: 'relations-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Relationship Chains'),
            h('span', { class: 'panel-count' }, `${props.result.relations.length} Total`)
          ]),
          h('div', { class: 'relations-list' },
            (expandedRelations.value ? props.result.relations : props.result.relations.slice(0, INITIAL_SHOW_COUNT)).map((rel, i) => 
              h('div', { class: 'relation-item', key: i }, [
                h('span', { class: 'rel-source' }, rel.source),
                h('span', { class: 'rel-arrow' }, [
                  h('span', { class: 'rel-line' }),
                  h('span', { class: 'rel-label' }, rel.relation),
                  h('span', { class: 'rel-line' })
                ]),
                h('span', { class: 'rel-target' }, rel.target)
              ])
            )
          ),
          props.result.relations.length > INITIAL_SHOW_COUNT && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedRelations.value = !expandedRelations.value }
          }, expandedRelations.value ? `Collapse ▲` : `Expand All (${props.result.relations.length}) ▼`)
        ]),

        activeTab.value === 'subqueries' && props.result.subQueries.length > 0 && h('div', { class: 'subqueries-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Drift Query Sub-Questions'),
            h('span', { class: 'panel-count' }, `${props.result.subQueries.length} Total`)
          ]),
          h('div', { class: 'subqueries-list' },
            props.result.subQueries.map((sq, i) => 
              h('div', { class: 'subquery-item', key: i }, [
                h('span', { class: 'subquery-number' }, `Q${i + 1}`),
                h('div', { class: 'subquery-text' }, sq)
              ])
            )
          )
        ]),
        
        activeTab.value === 'facts' && props.result.facts.length === 0 && h('div', { class: 'empty-state' }, 'No key memories found'),
        activeTab.value === 'entities' && props.result.entities.length === 0 && h('div', { class: 'empty-state' }, 'No core entities found'),
        activeTab.value === 'relations' && props.result.relations.length === 0 && h('div', { class: 'empty-state' }, 'No relationship chains found')
      ])
    ])
  }
}

// Panorama Display Component - Enhanced with Active/Historical tabs
const PanoramaDisplay = {
  props: ['result', 'resultLength'],
  setup(props) {
    const activeTab = ref('active') // 'active', 'historical', 'entities'
    const expandedActive = ref(false)
    const expandedHistorical = ref(false)
    const expandedEntities = ref(false)
    const INITIAL_SHOW_COUNT = 5
    
    const formatSize = (length) => {
      if (!length) return ''
      if (length >= 1000) return `${(length / 1000).toFixed(1)}k chars`
      return `${length} chars`
    }
    
    return () => h('div', { class: 'panorama-display' }, [
      h('div', { class: 'panorama-header' }, [
        h('div', { class: 'header-main' }, [
          h('div', { class: 'header-title' }, 'Panorama Search'),
          h('div', { class: 'header-stats' }, [
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.stats.nodes),
              h('span', { class: 'stat-label' }, 'Nodes')
            ]),
            h('span', { class: 'stat-divider' }, '/'),
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.stats.edges),
              h('span', { class: 'stat-label' }, 'Edges')
            ]),
            props.resultLength && h('span', { class: 'stat-divider' }, '·'),
            props.resultLength && h('span', { class: 'stat-size' }, formatSize(props.resultLength))
          ])
        ]),
        props.result.query && h('div', { class: 'header-topic' }, props.result.query)
      ]),
      
      h('div', { class: 'panorama-tabs' }, [
        h('button', {
          class: ['panorama-tab', { active: activeTab.value === 'active' }],
          onClick: () => { activeTab.value = 'active' }
        }, [
          h('span', { class: 'tab-label' }, `Current Active Memories (${props.result.activeFacts.length})`)
        ]),
        h('button', {
          class: ['panorama-tab', { active: activeTab.value === 'historical' }],
          onClick: () => { activeTab.value = 'historical' }
        }, [
          h('span', { class: 'tab-label' }, `Historical Memories (${props.result.historicalFacts.length})`)
        ]),
        h('button', {
          class: ['panorama-tab', { active: activeTab.value === 'entities' }],
          onClick: () => { activeTab.value = 'entities' }
        }, [
          h('span', { class: 'tab-label' }, `Related Entities (${props.result.entities.length})`)
        ])
      ]),
      
      h('div', { class: 'panorama-content' }, [
        activeTab.value === 'active' && h('div', { class: 'facts-panel active-facts' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Current Active Memories'),
            h('span', { class: 'panel-count' }, `${props.result.activeFacts.length} Total`)
          ]),
          props.result.activeFacts.length > 0 ? h('div', { class: 'facts-list' },
            (expandedActive.value ? props.result.activeFacts : props.result.activeFacts.slice(0, INITIAL_SHOW_COUNT)).map((fact, i) => 
              h('div', { class: 'fact-item active', key: i }, [
                h('span', { class: 'fact-number' }, i + 1),
                h('div', { class: 'fact-content' }, fact)
              ])
            )
          ) : h('div', { class: 'empty-state' }, 'No active memories found'),
          props.result.activeFacts.length > INITIAL_SHOW_COUNT && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedActive.value = !expandedActive.value }
          }, expandedActive.value ? `Collapse ▲` : `Expand All (${props.result.activeFacts.length}) ▼`)
        ]),

        activeTab.value === 'historical' && h('div', { class: 'facts-panel historical-facts' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Historical Memories'),
            h('span', { class: 'panel-count' }, `${props.result.historicalFacts.length} Total`)
          ]),
          props.result.historicalFacts.length > 0 ? h('div', { class: 'facts-list' },
            (expandedHistorical.value ? props.result.historicalFacts : props.result.historicalFacts.slice(0, INITIAL_SHOW_COUNT)).map((fact, i) => 
              h('div', { class: 'fact-item historical', key: i }, [
                h('span', { class: 'fact-number' }, i + 1),
                h('div', { class: 'fact-content' }, [
                  (() => {
                    const timeMatch = fact.match(/^\[(.+?)\]\s*(.*)$/)
                    if (timeMatch) {
                      return [
                        h('span', { class: 'fact-time' }, timeMatch[1]),
                        h('span', { class: 'fact-text' }, timeMatch[2])
                      ]
                    }
                    return h('span', { class: 'fact-text' }, fact)
                  })()
                ])
              ])
            )
          ) : h('div', { class: 'empty-state' }, 'No historical memories found'),
          props.result.historicalFacts.length > INITIAL_SHOW_COUNT && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedHistorical.value = !expandedHistorical.value }
          }, expandedHistorical.value ? `Collapse ▲` : `Expand All (${props.result.historicalFacts.length}) ▼`)
        ]),

        activeTab.value === 'entities' && h('div', { class: 'entities-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Related Entities'),
            h('span', { class: 'panel-count' }, `${props.result.entities.length} Total`)
          ]),
          props.result.entities.length > 0 ? h('div', { class: 'entities-grid' },
            (expandedEntities.value ? props.result.entities : props.result.entities.slice(0, 8)).map((entity, i) => 
              h('div', { class: 'entity-tag', key: i }, [
                h('span', { class: 'entity-name' }, entity.name),
                entity.type && h('span', { class: 'entity-type' }, entity.type)
              ])
            )
          ) : h('div', { class: 'empty-state' }, 'No related entities found'),
          props.result.entities.length > 8 && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedEntities.value = !expandedEntities.value }
          }, expandedEntities.value ? `Collapse ▲` : `Expand All (${props.result.entities.length}) ▼`)
        ])
      ])
    ])
  }
}

// Interview Display Component - Conversation Style (Q&A Format)
const InterviewDisplay = {
  props: ['result', 'resultLength'],
  setup(props) {
    const formatSize = (length) => {
      if (!length) return ''
      if (length >= 1000) return `${(length / 1000).toFixed(1)}k chars`
      return `${length} chars`
    }
    
    const cleanQuoteText = (text) => {
      if (!text) return ''
      return text.replace(/^\s*\d+[\.\、\)）]\s*/, '').trim()
    }
    
    const activeIndex = ref(0)
    const expandedAnswers = ref(new Set())
    const platformTabs = reactive({})
    
    const getPlatformTab = (agentIdx, qIdx) => {
      const key = `${agentIdx}-${qIdx}`
      return platformTabs[key] || 'twitter'
    }
    
    const setPlatformTab = (agentIdx, qIdx, platform) => {
      const key = `${agentIdx}-${qIdx}`
      platformTabs[key] = platform
    }
    
    const toggleAnswer = (key) => {
      const newSet = new Set(expandedAnswers.value)
      if (newSet.has(key)) newSet.delete(key)
      else newSet.add(key)
      expandedAnswers.value = newSet
    }
    
    const formatAnswer = (text, expanded) => {
      if (!text) return ''
      if (expanded || text.length <= 400) return text
      return text.substring(0, 400) + '...'
    }
    
    const isPlaceholderText = (text) => {
      if (!text) return true
      const t = text.trim()
      return t === '（该平台未获得回复）' || t === '(该平台未获得回复)' || t === '[无回复]' || t === '(No reply from this platform)' || t === '[No reply]'
    }

    const splitAnswerByQuestions = (answerText, questionCount) => {
      if (!answerText || questionCount <= 0) return [answerText]
      if (isPlaceholderText(answerText)) return ['']

      let matches = []
      let match

      const cnPattern = /(?:^|[\r\n]+)问题(\d+)[：:]\s*/g
      while ((match = cnPattern.exec(answerText)) !== null) {
        matches.push({ num: parseInt(match[1]), index: match.index, fullMatch: match[0] })
      }

      if (matches.length === 0) {
        const numPattern = /(?:^|[\r\n]+)(\d+)\.\s+/g
        while ((match = numPattern.exec(answerText)) !== null) {
          matches.push({ num: parseInt(match[1]), index: match.index, fullMatch: match[0] })
        }
      }

      if (matches.length <= 1) {
        const cleaned = answerText.replace(/^问题\d+[：:]\s*/, '').replace(/^\d+\.\s+/, '').trim()
        return [cleaned || answerText]
      }

      const parts = []
      for (let i = 0; i < matches.length; i++) {
        const current = matches[i]
        const next = matches[i + 1]
        const startIdx = current.index + current.fullMatch.length
        const endIdx = next ? next.index : answerText.length

        let part = answerText.substring(startIdx, endIdx).trim()
        part = part.replace(/[\r\n]+$/, '').trim()
        parts.push(part)
      }

      if (parts.length > 0 && parts.some(p => p)) return parts
      return [answerText]
    }
    
    const getAnswerForQuestion = (interview, qIdx, platform) => {
      const answer = platform === 'twitter' ? interview.twitterAnswer : (interview.redditAnswer || interview.twitterAnswer)
      if (!answer || isPlaceholderText(answer)) return answer || ''

      const questionCount = interview.questions?.length || 1
      const answers = splitAnswerByQuestions(answer, questionCount)

      if (answers.length > 1 && qIdx < answers.length) return answers[qIdx] || ''
      return qIdx === 0 ? answer : ''
    }
    
    const hasMultiplePlatforms = (interview, qIdx) => {
      if (!interview.twitterAnswer || !interview.redditAnswer) return false
      const twitterAnswer = getAnswerForQuestion(interview, qIdx, 'twitter')
      const redditAnswer = getAnswerForQuestion(interview, qIdx, 'reddit')
      return !isPlaceholderText(twitterAnswer) && !isPlaceholderText(redditAnswer) && twitterAnswer !== redditAnswer
    }
    
    return () => h('div', { class: 'interview-display' }, [
      h('div', { class: 'interview-header' }, [
        h('div', { class: 'header-main' }, [
          h('div', { class: 'header-title' }, 'Agent Interview'),
          h('div', { class: 'header-stats' }, [
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.successCount || props.result.interviews.length),
              h('span', { class: 'stat-label' }, 'Interviewed')
            ]),
            props.result.totalCount > 0 && h('span', { class: 'stat-divider' }, '/'),
            props.result.totalCount > 0 && h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.totalCount),
              h('span', { class: 'stat-label' }, 'Total')
            ]),
            props.resultLength && h('span', { class: 'stat-divider' }, '·'),
            props.resultLength && h('span', { class: 'stat-size' }, formatSize(props.resultLength))
          ])
        ]),
        props.result.topic && h('div', { class: 'header-topic' }, props.result.topic)
      ]),
      
      props.result.interviews.length > 0 && h('div', { class: 'agent-tabs' }, 
        props.result.interviews.map((interview, i) => h('button', {
          class: ['agent-tab', { active: activeIndex.value === i }],
          key: i,
          onClick: () => { activeIndex.value = i }
        }, [
          h('span', { class: 'tab-avatar' }, interview.name ? interview.name.charAt(0) : (i + 1)),
          h('span', { class: 'tab-name' }, interview.title || interview.name || `Agent ${i + 1}`)
        ]))
      ),
      
      props.result.interviews.length > 0 && h('div', { class: 'interview-detail' }, [
        h('div', { class: 'agent-profile' }, [
          h('div', { class: 'profile-avatar' }, props.result.interviews[activeIndex.value]?.name?.charAt(0) || 'A'),
          h('div', { class: 'profile-info' }, [
            h('div', { class: 'profile-name' }, props.result.interviews[activeIndex.value]?.name || 'Agent'),
            h('div', { class: 'profile-role' }, props.result.interviews[activeIndex.value]?.role || ''),
            props.result.interviews[activeIndex.value]?.bio && h('div', { class: 'profile-bio' }, props.result.interviews[activeIndex.value].bio)
          ])
        ]),
        
        props.result.interviews[activeIndex.value]?.selectionReason && h('div', { class: 'selection-reason' }, [
          h('div', { class: 'reason-label' }, 'Selection Reason'),
          h('div', { class: 'reason-content' }, props.result.interviews[activeIndex.value].selectionReason)
        ]),
        
        h('div', { class: 'qa-thread' }, 
          (props.result.interviews[activeIndex.value]?.questions?.length > 0 
            ? props.result.interviews[activeIndex.value].questions 
            : [props.result.interviews[activeIndex.value]?.question || 'No question available']
          ).map((question, qIdx) => {
            const interview = props.result.interviews[activeIndex.value]
            const currentPlatform = getPlatformTab(activeIndex.value, qIdx)
            const answerText = getAnswerForQuestion(interview, qIdx, currentPlatform)
            const hasDualPlatform = hasMultiplePlatforms(interview, qIdx)
            const expandKey = `${activeIndex.value}-${qIdx}`
            const isExpanded = expandedAnswers.value.has(expandKey)
            const isPlaceholder = isPlaceholderText(answerText)

            return h('div', { class: 'qa-pair', key: qIdx }, [
              h('div', { class: 'qa-question' }, [
                h('div', { class: 'qa-badge q-badge' }, `Q${qIdx + 1}`),
                h('div', { class: 'qa-content' }, [
                  h('div', { class: 'qa-sender' }, 'Interviewer'),
                  h('div', { class: 'qa-text' }, question)
                ])
              ]),

              answerText && h('div', { class: ['qa-answer', { 'answer-placeholder': isPlaceholder }] }, [
                h('div', { class: 'qa-badge a-badge' }, `A${qIdx + 1}`),
                h('div', { class: 'qa-content' }, [
                  h('div', { class: 'qa-answer-header' }, [
                    h('div', { class: 'qa-sender' }, interview?.name || 'Agent'),
                    hasDualPlatform && h('div', { class: 'platform-switch' }, [
                      h('button', {
                        class: ['platform-btn', { active: currentPlatform === 'twitter' }],
                        onClick: (e) => { e.stopPropagation(); setPlatformTab(activeIndex.value, qIdx, 'twitter') }
                      }, [
                        h('svg', { class: 'platform-icon', viewBox: '0 0 24 24', width: 12, height: 12, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
                          h('circle', { cx: '12', cy: '12', r: '10' }),
                          h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }),
                          h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })
                        ]),
                        h('span', {}, 'World 1')
                      ]),
                      h('button', {
                        class: ['platform-btn', { active: currentPlatform === 'reddit' }],
                        onClick: (e) => { e.stopPropagation(); setPlatformTab(activeIndex.value, qIdx, 'reddit') }
                      }, [
                        h('svg', { class: 'platform-icon', viewBox: '0 0 24 24', width: 12, height: 12, fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
                          h('path', { d: 'M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z' })
                        ]),
                        h('span', {}, 'World 2')
                      ])
                    ])
                  ]),
                  h('div', {
                    class: ['qa-text', 'answer-text', { 'placeholder-text': isPlaceholder }],
                    innerHTML: isPlaceholder
                      ? answerText
                      : formatAnswer(answerText, isExpanded)
                          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\n/g, '<br>')
                  }),
                  !isPlaceholder && answerText.length > 400 && h('button', {
                    class: 'expand-answer-btn',
                    onClick: () => toggleAnswer(expandKey)
                  }, isExpanded ? 'Show Less' : 'Show More')
                ])
              ])
            ])
          })
        ),
        
        props.result.interviews[activeIndex.value]?.quotes?.length > 0 && h('div', { class: 'quotes-section' }, [
          h('div', { class: 'quotes-header' }, 'Key Quotes'),
          h('div', { class: 'quotes-list' },
            props.result.interviews[activeIndex.value].quotes.slice(0, 3).map((quote, qi) => {
              const cleanedQuote = cleanQuoteText(quote)
              const displayQuote = cleanedQuote.length > 200 ? cleanedQuote.substring(0, 200) + '...' : cleanedQuote
              return h('blockquote', { 
                key: qi, 
                class: 'quote-item',
                innerHTML: renderMarkdown(displayQuote)
              })
            })
          )
        ])
      ]),

      props.result.summary && h('div', { class: 'summary-section' }, [
        h('div', { class: 'summary-header' }, 'Interview Summary'),
        h('div', { 
          class: 'summary-content',
          innerHTML: renderMarkdown(props.result.summary.length > 500 ? props.result.summary.substring(0, 500) + '...' : props.result.summary)
        })
      ])
    ])
  }
}

const QuickSearchDisplay = {
  props: ['result', 'resultLength'],
  setup(props) {
    const activeTab = ref('facts')
    const expandedFacts = ref(false)
    const INITIAL_SHOW_COUNT = 5
    
    const hasEdges = computed(() => props.result.edges && props.result.edges.length > 0)
    const hasNodes = computed(() => props.result.nodes && props.result.nodes.length > 0)
    const showTabs = computed(() => hasEdges.value || hasNodes.value)
    
    const formatSize = (length) => {
      if (!length) return ''
      if (length >= 1000) return `${(length / 1000).toFixed(1)}k chars`
      return `${length} chars`
    }
    
    return () => h('div', { class: 'quick-search-display' }, [
      h('div', { class: 'quicksearch-header' }, [
        h('div', { class: 'header-main' }, [
          h('div', { class: 'header-title' }, 'Quick Search'),
          h('div', { class: 'header-stats' }, [
            h('span', { class: 'stat-item' }, [
              h('span', { class: 'stat-value' }, props.result.count || props.result.facts.length),
              h('span', { class: 'stat-label' }, 'Results')
            ]),
            props.resultLength && h('span', { class: 'stat-divider' }, '·'),
            props.resultLength && h('span', { class: 'stat-size' }, formatSize(props.resultLength))
          ])
        ]),
        props.result.query && h('div', { class: 'header-query' }, [
          h('span', { class: 'query-label' }, 'Search: '),
          h('span', { class: 'query-text' }, props.result.query)
        ])
      ]),
      
      showTabs.value && h('div', { class: 'quicksearch-tabs' }, [
        h('button', {
          class: ['quicksearch-tab', { active: activeTab.value === 'facts' }],
          onClick: () => { activeTab.value = 'facts' }
        }, [
          h('span', { class: 'tab-label' }, `Facts (${props.result.facts.length})`)
        ]),
        hasEdges.value && h('button', {
          class: ['quicksearch-tab', { active: activeTab.value === 'edges' }],
          onClick: () => { activeTab.value = 'edges' }
        }, [
          h('span', { class: 'tab-label' }, `Related Relations (${props.result.edges.length})`)
        ]),
        hasNodes.value && h('button', {
          class: ['quicksearch-tab', { active: activeTab.value === 'nodes' }],
          onClick: () => { activeTab.value = 'nodes' }
        }, [
          h('span', { class: 'tab-label' }, `Related Nodes (${props.result.nodes.length})`)
        ])
      ]),
      
      h('div', { class: ['quicksearch-content', { 'no-tabs': !showTabs.value }] }, [
        ((!showTabs.value) || activeTab.value === 'facts') && h('div', { class: 'facts-panel' }, [
          !showTabs.value && h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Search Results'),
            h('span', { class: 'panel-count' }, `${props.result.facts.length} Total`)
          ]),
          props.result.facts.length > 0 ? h('div', { class: 'facts-list' },
            (expandedFacts.value ? props.result.facts : props.result.facts.slice(0, INITIAL_SHOW_COUNT)).map((fact, i) => 
              h('div', { class: 'fact-item', key: i }, [
                h('span', { class: 'fact-number' }, i + 1),
                h('div', { class: 'fact-content' }, fact)
              ])
            )
          ) : h('div', { class: 'empty-state' }, 'No relevant results found'),
          props.result.facts.length > INITIAL_SHOW_COUNT && h('button', {
            class: 'expand-btn',
            onClick: () => { expandedFacts.value = !expandedFacts.value }
          }, expandedFacts.value ? `Collapse ▲` : `Expand All (${props.result.facts.length}) ▼`)
        ]),

        activeTab.value === 'edges' && hasEdges.value && h('div', { class: 'edges-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Related Relations'),
            h('span', { class: 'panel-count' }, `${props.result.edges.length} Total`)
          ]),
          h('div', { class: 'edges-list' },
            props.result.edges.map((edge, i) => 
              h('div', { class: 'edge-item', key: i }, [
                h('span', { class: 'edge-source' }, edge.source),
                h('span', { class: 'edge-arrow' }, [
                  h('span', { class: 'edge-line' }),
                  h('span', { class: 'edge-label' }, edge.relation),
                  h('span', { class: 'edge-line' })
                ]),
                h('span', { class: 'edge-target' }, edge.target)
              ])
            )
          )
        ]),
        
        activeTab.value === 'nodes' && hasNodes.value && h('div', { class: 'nodes-panel' }, [
          h('div', { class: 'panel-header' }, [
            h('span', { class: 'panel-title' }, 'Related Nodes'),
            h('span', { class: 'panel-count' }, `${props.result.nodes.length} Total`)
          ]),
          h('div', { class: 'nodes-grid' },
            props.result.nodes.map((node, i) => 
              h('div', { class: 'node-tag', key: i }, [
                h('span', { class: 'node-name' }, node.name),
                node.type && h('span', { class: 'node-type' }, node.type)
              ])
            )
          )
        ])
      ])
    ])
  }
}

// Computed
const statusClass = computed(() => {
  if (isComplete.value) return 'completed'
  if (agentLogs.value.length > 0) return 'processing'
  return 'pending'
})

const statusText = computed(() => {
  if (isComplete.value) return 'Completed'
  if (agentLogs.value.length > 0) return 'Generating...'
  return 'Waiting'
})

const totalSections = computed(() => {
  return reportOutline.value?.sections?.length || 0
})

const completedSections = computed(() => {
  return Object.keys(generatedSections.value).length
})

const progressPercent = computed(() => {
  if (totalSections.value === 0) return 0
  return Math.round((completedSections.value / totalSections.value) * 100)
})

const totalToolCalls = computed(() => {
  return agentLogs.value.filter(l => l.action === 'tool_call').length
})

const formatElapsedTime = computed(() => {
  if (!startTime.value) return '0s'
  const lastLog = agentLogs.value[agentLogs.value.length - 1]
  const elapsed = lastLog?.elapsed_seconds || 0
  if (elapsed < 60) return `${Math.round(elapsed)}s`
  const mins = Math.floor(elapsed / 60)
  const secs = Math.round(elapsed % 60)
  return `${mins}m ${secs}s`
})

const displayLogs = computed(() => {
  return agentLogs.value
})

const activeSectionIndex = computed(() => {
  if (isComplete.value) return null
  if (currentSectionIndex.value) return currentSectionIndex.value
  if (totalSections.value > 0 && completedSections.value < totalSections.value) return completedSections.value + 1
  return null
})

const isPlanningDone = computed(() => {
  return !!reportOutline.value?.sections?.length || agentLogs.value.some(l => l.action === 'planning_complete')
})

const isPlanningStarted = computed(() => {
  return agentLogs.value.some(l => l.action === 'planning_start' || l.action === 'report_start')
})

const isFinalizing = computed(() => {
  return !isComplete.value && isPlanningDone.value && totalSections.value > 0 && completedSections.value >= totalSections.value
})

const activeStep = computed(() => {
  const steps = workflowSteps.value
  const active = steps.find(s => s.status === 'active')
  if (active) return active
  const doneSteps = steps.filter(s => s.status === 'done')
  if (doneSteps.length > 0) return doneSteps[doneSteps.length - 1]
  return steps[0] || { noLabel: '--', title: 'Waiting to start', status: 'todo', meta: '' }
})

const workflowSteps = computed(() => {
  const steps = []

  const planningStatus = isPlanningDone.value ? 'done' : (isPlanningStarted.value ? 'active' : 'todo')
  steps.push({
    key: 'planning',
    noLabel: 'PL',
    title: 'Planning / Outline',
    status: planningStatus,
    meta: planningStatus === 'active' ? 'IN PROGRESS' : ''
  })

  const sections = reportOutline.value?.sections || []
  sections.forEach((section, i) => {
    const idx = i + 1
    const status = (isComplete.value || !!generatedSections.value[idx])
      ? 'done'
      : (activeSectionIndex.value === idx ? 'active' : 'todo')

    steps.push({
      key: `section-${idx}`,
      noLabel: String(idx).padStart(2, '0'),
      title: section.title,
      status,
      meta: status === 'active' ? 'IN PROGRESS' : ''
    })
  })

  const completeStatus = isComplete.value ? 'done' : (isFinalizing.value ? 'active' : 'todo')
  steps.push({
    key: 'complete',
    noLabel: 'OK',
    title: 'Complete',
    status: completeStatus,
    meta: completeStatus === 'active' ? 'FINALIZING' : ''
  })

  return steps
})

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

const isSectionCompleted = (sectionIndex) => {
  return !!generatedSections.value[sectionIndex]
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  } catch {
    return ''
  }
}

const formatParams = (params) => {
  if (!params) return ''
  try {
    return JSON.stringify(params, null, 2)
  } catch {
    return String(params)
  }
}

const formatResultSize = (length) => {
  if (!length) return ''
  if (length < 1000) return `${length} chars`
  return `${(length / 1000).toFixed(1)}k chars`
}

const truncateText = (text, maxLen) => {
  if (!text) return ''
  if (text.length <= maxLen) return text
  return text.substring(0, maxLen) + '...'
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
  
  html = html.replace(/^(\s*)- (.+)$/gm, (match, indent, text) => {
    const level = Math.floor(indent.length / 2)
    return `<li class="md-li" data-level="${level}">${text}</li>`
  })
  html = html.replace(/^(\s*)(\d+)\. (.+)$/gm, (match, indent, num, text) => {
    const level = Math.floor(indent.length / 2)
    return `<li class="md-oli" data-level="${level}">${text}</li>`
  })

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
  let olCounter = 0
  let inSequence = false
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].startsWith('<ol class="md-ol">')) {
      const liCount = (tokens[i].match(/<li class="md-oli"/g) || []).length
      if (liCount === 1) {
        olCounter++
        if (olCounter > 1) {
          tokens[i] = tokens[i].replace('<ol class="md-ol">', `<ol class="md-ol" start="${olCounter}">`)
        }
        inSequence = true
      } else {
        olCounter = 0
        inSequence = false
      }
    } else if (inSequence) {
      if (/<h[2-5]/.test(tokens[i])) {
        olCounter = 0
        inSequence = false
      }
    }
  }
  html = tokens.join('')

  return html
}

const getTimelineItemClass = (log, idx, total) => {
  const isLatest = idx === total - 1 && !isComplete.value
  const isMilestone = log.action === 'section_complete' || log.action === 'report_complete'
  return {
    'node--active': isLatest,
    'node--done': !isLatest && isMilestone,
    'node--muted': !isLatest && !isMilestone,
    'node--tool': log.action === 'tool_call' || log.action === 'tool_result'
  }
}

const getConnectorClass = (log, idx, total) => {
  const isLatest = idx === total - 1 && !isComplete.value
  if (isLatest) return 'dot-active'
  if (log.action === 'section_complete' || log.action === 'report_complete') return 'dot-done'
  return 'dot-muted'
}

const getActionLabel = (action) => {
  const labels = {
    'report_start': 'Report Started',
    'planning_start': 'Planning',
    'planning_complete': 'Plan Complete',
    'section_start': 'Section Start',
    'section_content': 'Content Ready',
    'section_complete': 'Section Done',
    'tool_call': 'Tool Call',
    'tool_result': 'Tool Result',
    'llm_response': 'LLM Response',
    'report_complete': 'Complete'
  }
  return labels[action] || action
}

const getLogLevelClass = (log) => {
  if (log.includes('ERROR') || log.includes('错误') || log.includes('Error')) return 'error'
  if (log.includes('WARNING') || log.includes('警告') || log.includes('Warning')) return 'warning'
  return ''
}

// Polling
let agentLogTimer = null
let consoleLogTimer = null

const fetchAgentLog = async () => {
  if (!props.reportId) return
  
  try {
    const res = await getAgentLog(props.reportId, agentLogLine.value)
    
    if (res.success && res.data) {
      const newLogs = res.data.logs || []
      
      if (newLogs.length > 0) {
        newLogs.forEach(log => {
          agentLogs.value.push(log)
          
          if (log.action === 'planning_complete' && log.details?.outline) {
            reportOutline.value = log.details.outline
          }
          
          if (log.action === 'section_start') {
            currentSectionIndex.value = log.section_index
          }

          if (log.action === 'section_complete') {
            if (log.details?.content) {
              generatedSections.value[log.section_index] = log.details.content
              expandedContent.value.add(log.section_index - 1)
              currentSectionIndex.value = null
            }
          }
          
          if (log.action === 'report_complete') {
            isComplete.value = true
            currentSectionIndex.value = null 
            emit('update-status', 'completed')
            stopPolling()
          }
          
          if (log.action === 'report_start') {
            startTime.value = new Date(log.timestamp)
          }
        })
        
        agentLogLine.value = res.data.from_line + newLogs.length
        
        nextTick(() => {
          if (rightPanel.value) {
            if (isComplete.value) {
              rightPanel.value.scrollTop = 0
            } else {
              rightPanel.value.scrollTop = rightPanel.value.scrollHeight
            }
          }
        })
      }
    }
  } catch (err) {
    console.warn('Failed to fetch agent log:', err)
  }
}

const extractFinalContent = (response) => {
  if (!response) return null
  
  const finalAnswerTagMatch = response.match(/<final_answer>([\s\S]*?)<\/final_answer>/)
  if (finalAnswerTagMatch) {
    return finalAnswerTagMatch[1].trim()
  }
  
  const finalAnswerMatch = response.match(/Final\s*Answer:\s*\n*([\s\S]*)$/i)
  if (finalAnswerMatch) {
    return finalAnswerMatch[1].trim()
  }
  
  const chineseFinalMatch = response.match(/最终答案[:：]\s*\n*([\s\S]*)$/i)
  if (chineseFinalMatch) {
    return chineseFinalMatch[1].trim()
  }
  
  const trimmedResponse = response.trim()
  if (trimmedResponse.match(/^[#>]/)) {
    return trimmedResponse
  }
  
  if (response.length > 300 && (response.includes('**') || response.includes('>'))) {
    const thoughtMatch = response.match(/^Thought:[\s\S]*?(?=\n\n[^T]|\n\n$)/i)
    if (thoughtMatch) {
      const afterThought = response.substring(thoughtMatch[0].length).trim()
      if (afterThought.length > 100) {
        return afterThought
      }
    }
  }
  
  return null
}

const fetchConsoleLog = async () => {
  if (!props.reportId) return
  
  try {
    const res = await getConsoleLog(props.reportId, consoleLogLine.value)
    
    if (res.success && res.data) {
      const newLogs = res.data.logs || []
      
      if (newLogs.length > 0) {
        consoleLogs.value.push(...newLogs)
        consoleLogLine.value = res.data.from_line + newLogs.length
        
        nextTick(() => {
          if (logContent.value) {
            logContent.value.scrollTop = logContent.value.scrollHeight
          }
        })
      }
    }
  } catch (err) {
    console.warn('Failed to fetch console log:', err)
  }
}

const startPolling = () => {
  if (agentLogTimer || consoleLogTimer) return
  
  fetchAgentLog()
  fetchConsoleLog()
  
  agentLogTimer = setInterval(fetchAgentLog, 2000)
  consoleLogTimer = setInterval(fetchConsoleLog, 1500)
}

const stopPolling = () => {
  if (agentLogTimer) {
    clearInterval(agentLogTimer)
    agentLogTimer = null
  }
  if (consoleLogTimer) {
    clearInterval(consoleLogTimer)
    consoleLogTimer = null
  }
}

onMounted(() => {
  if (props.reportId) {
    addLog(`Report Agent initialized: ${props.reportId}`)
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})

watch(() => props.reportId, (newId) => {
  if (newId) {
    agentLogs.value = []
    consoleLogs.value = []
    agentLogLine.value = 0
    consoleLogLine.value = 0
    reportOutline.value = null
    currentSectionIndex.value = null
    generatedSections.value = {}
    expandedContent.value = new Set()
    expandedLogs.value = new Set()
    collapsedSections.value = new Set()
    isComplete.value = false
    startTime.value = null
    
    startPolling()
  }
}, { immediate: true })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

.report-panel {
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
  --terminal-bg: #0F172A;

  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  overflow: hidden;
}

/* Main Split Layout */
.main-split-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Custom Scrollbars */
.custom-scrollbar::-webkit-scrollbar,
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track,
.left-panel::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb,
.left-panel::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover,
.left-panel:hover::-webkit-scrollbar-thumb,
.right-panel:hover::-webkit-scrollbar-thumb { background: #94A3B8; }

/* Panel Headers */
.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
  font-weight: 800;
  color: var(--text-main);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-main);
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.1);
  margin-right: 8px;
  flex-shrink: 0;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(15, 23, 42, 0.2); }
  70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(15, 23, 42, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(15, 23, 42, 0); }
}

.header-index { font-size: 12px; font-weight: 700; color: var(--text-muted); margin-right: 10px; }
.header-title { font-size: 13px; font-weight: 800; color: var(--text-main); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; letter-spacing: 0.05em; text-transform: uppercase;}
.header-meta { margin-left: auto; font-size: 10px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

.panel-header--active { background: rgba(248, 250, 252, 0.9); border-color: var(--border-focus); }
.panel-header--active .header-index, .panel-header--active .header-title, .panel-header--active .header-meta { color: var(--primary); }
.panel-header--done { background: rgba(255, 255, 255, 0.9); }
.panel-header--done .header-index { color: #10B981; }

/* Left Panel - Report Style (Linear/Notion Aesthetic) */
.left-panel.report-style {
  width: 50%;
  min-width: 500px;
  background: var(--bg-card);
  border-right: 1px solid var(--border-light);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 40px 60px 80px 60px;
}

.report-content-wrapper { max-width: 800px; margin: 0 auto; width: 100%; }
.report-header-block { margin-bottom: 40px; }

.report-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; }
.report-tag { background: var(--text-main); color: #FFFFFF; font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.05em; text-transform: uppercase; }
.report-id { font-size: 11px; color: var(--text-muted); font-weight: 700; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;}

.main-title { font-size: 32px; font-weight: 800; color: var(--text-main); line-height: 1.2; margin: 0 0 16px 0; letter-spacing: -0.02em; }
.sub-title { font-size: 16px; color: var(--text-muted); line-height: 1.6; margin: 0 0 32px 0; font-weight: 500; }
.header-divider { height: 1px; background: var(--border-light); width: 100%; }

/* Sections List */
.sections-list { display: flex; flex-direction: column; gap: 32px; }
.report-section-item { display: flex; flex-direction: column; gap: 16px; }

.section-header-row { display: flex; align-items: baseline; gap: 12px; transition: all 0.2s ease; padding: 12px 16px; margin: -12px -16px; border-radius: var(--radius-md); }
.section-header-row.clickable { cursor: pointer; }
.section-header-row.clickable:hover { background: var(--bg-main); }

.collapse-icon { margin-left: auto; color: var(--text-muted); transition: transform 0.3s ease; flex-shrink: 0; align-self: center; }
.collapse-icon.is-collapsed { transform: rotate(-90deg); }

.section-number { font-family: 'JetBrains Mono', monospace; font-size: 16px; color: var(--border-focus); font-weight: 800; }
.section-title { font-size: 20px; font-weight: 800; color: var(--text-main); margin: 0; transition: color 0.3s ease; letter-spacing: -0.01em;}

.report-section-item.is-pending .section-title { color: var(--border-focus); }
.section-body { padding-left: 36px; overflow: hidden; }

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
.generated-content :deep(.code-block) { background: var(--terminal-bg); color: #F8FAFC; padding: 16px; border-radius: var(--radius-sm); font-family: 'JetBrains Mono', monospace; font-size: 13px; overflow-x: auto; margin: 1.5em 0; }
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


/* Right Panel (Workflow & Timeline) */
.right-panel {
  flex: 1;
  background: var(--bg-main);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.mono { font-family: 'JetBrains Mono', monospace; }

/* Workflow Overview */
.workflow-overview { padding: 24px 32px 0 32px; }
.workflow-metrics { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-bottom: 20px; background: var(--bg-card); padding: 16px 20px; border-radius: var(--radius-md); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm);}
.metric { display: inline-flex; align-items: baseline; gap: 6px; }
.metric-right { margin-left: auto; }
.metric-label { font-size: 10px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { font-size: 14px; color: var(--text-main); font-weight: 800;}

.metric-pill { font-size: 10px; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-light); background: var(--bg-main); color: var(--text-muted); }
.metric-pill.pill--processing { background: #EFF6FF; border-color: #93C5FD; color: #1D4ED8; }
.metric-pill.pill--completed { background: #ECFDF5; border-color: #A7F3D0; color: #059669; }

.workflow-steps { display: flex; flex-direction: column; gap: 10px; padding-bottom: 16px; }
.wf-step { display: grid; grid-template-columns: 24px 1fr; gap: 16px; padding: 16px; border: 1px solid var(--border-light); border-radius: var(--radius-md); background: var(--bg-card); box-shadow: var(--shadow-sm); transition: all 0.2s ease;}
.wf-step--active { border-color: var(--primary); box-shadow: var(--shadow-md), var(--shadow-glow); transform: translateY(-2px);}
.wf-step--done { background: var(--bg-card); border-color: var(--border-light); }

.wf-step-connector { display: flex; flex-direction: column; align-items: center; width: 24px; flex-shrink: 0; }
.wf-step-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--border-focus); border: 2px solid var(--bg-card); z-index: 1; }
.wf-step-line { width: 2px; flex: 1; background: var(--border-light); margin-top: -2px; }
.wf-step--active .wf-step-dot { background: var(--primary); box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15); }
.wf-step--done .wf-step-dot { background: #10B981; }

.wf-step-title-row { display: flex; align-items: baseline; gap: 12px; min-width: 0; }
.wf-step-index { font-size: 12px; font-weight: 800; color: var(--text-muted); flex-shrink: 0; }
.wf-step-title { font-size: 14px; font-weight: 700; color: var(--text-main); line-height: 1.35; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.wf-step-meta { margin-left: auto; font-size: 10px; font-weight: 800; color: var(--primary); text-transform: uppercase; letter-spacing: 0.05em; flex-shrink: 0; }
.wf-step--todo .wf-step-title, .wf-step--todo .wf-step-index { color: var(--border-focus); }
.workflow-divider { height: 1px; background: var(--border-light); margin: 20px 0 0 0; }


/* ==========================================================================
   BUTTONS OVERHAUL (PREMIUM ACTION & NEXT STEP BUTTONS)
   ========================================================================== */

/* The Main "Enter Deep Interaction" Button */
.next-step-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: calc(100% - 40px);
  margin: 16px 20px 0 20px;
  padding: 16px 24px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 14px;
  font-weight: 800;
  color: #FFFFFF !important;
  background: var(--text-main);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}

.next-step-btn:hover {
  background: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
}

.next-step-btn svg {
  transition: transform 0.2s ease;
}

.next-step-btn:hover svg {
  transform: translateX(4px);
}

/* Small Contextual Actions ("Raw Output", "Show Params", "Expand All") */
.action-btn, 
.action-btn-small, 
:deep(.expand-btn) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF !important;
  border: 1px solid var(--border-focus) !important;
  padding: 8px 16px !important;
  border-radius: 8px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  color: var(--text-muted) !important;
  cursor: pointer;
  transition: all 0.2s ease !important;
  box-shadow: var(--shadow-sm) !important;
  white-space: nowrap;
}

:deep(.expand-btn) {
  width: 100% !important;
  margin-top: 16px !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.action-btn:hover, 
.action-btn-small:hover, 
:deep(.expand-btn:hover) {
  background: var(--bg-main) !important;
  color: var(--text-main) !important;
  border-color: var(--text-muted) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
}


/* Workflow Timeline (Glassmorphic Cards) */
.workflow-timeline { padding: 24px 32px 32px; flex: 1; }

.timeline-item {
  display: grid; grid-template-columns: 24px 1fr; gap: 16px; padding: 16px; margin-bottom: 16px;
  border: 1px solid var(--border-light); border-radius: var(--radius-md); background: var(--bg-card); 
  box-shadow: var(--shadow-sm); transition: all 0.2s ease;
}

.timeline-item:hover { border-color: var(--border-focus); box-shadow: var(--shadow-md); transform: translateY(-1px);}
.timeline-item.node--active { background: var(--bg-card); border-color: var(--primary); box-shadow: var(--shadow-md), var(--shadow-glow); }
.timeline-item.node--done { background: var(--bg-card); border-color: var(--border-light); }

.timeline-connector { display: flex; flex-direction: column; align-items: center; width: 24px; flex-shrink: 0; }
.connector-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--border-focus); border: 2px solid var(--bg-card); z-index: 1; }
.connector-line { width: 2px; flex: 1; background: var(--border-light); margin-top: -2px; }
.dot-active { background: var(--primary); box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15); }
.dot-done { background: #10B981; }

.timeline-content { min-width: 0; background: transparent; border: none; border-radius: 0; padding: 0; margin: 0; transition: none; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.action-label { font-size: 11px; font-weight: 800; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.05em; }
.action-time { font-size: 11px; font-weight: 600; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }

.timeline-body { font-size: 14px; color: #334155; }
.timeline-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 12px; border-top: 1px dashed var(--border-light); }
.elapsed-placeholder { flex-shrink: 0; }
.footer-actions { display: flex; gap: 8px; margin-left: auto; }
.elapsed-badge { font-size: 11px; font-weight: 700; color: var(--text-muted); background: var(--bg-main); padding: 4px 10px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; }

/* Timeline Body Elements */
.info-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: baseline;}
.info-key { font-size: 10px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); min-width: 90px; letter-spacing: 0.05em;}
.info-val { color: var(--text-main); font-weight: 600; font-size: 13px;}

.status-message { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 13px; font-weight: 500; border: 1px solid transparent; }
.status-message.planning { background: #EFF6FF; border-color: #BFDBFE; color: #1E40AF; }
.status-message.success { background: #ECFDF5; border-color: #A7F3D0; color: #065F46; }

.outline-badge { display: inline-block; margin-top: 12px; padding: 6px 12px; background: var(--bg-main); color: var(--text-muted); border: 1px solid var(--border-light); border-radius: 6px; font-size: 11px; font-weight: 700; }

.section-tag { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; background: var(--bg-main); border: 1px solid var(--border-light); border-radius: var(--radius-sm); }
.section-tag.content-ready { background: #EFF6FF; border: 1px solid #93C5FD; }
.section-tag.content-ready svg { color: var(--primary); }
.section-tag.completed { background: #ECFDF5; border: 1px solid #A7F3D0; }
.section-tag.completed svg { color: #10B981; }
.tag-num { font-size: 11px; font-weight: 800; color: var(--text-muted); }
.section-tag.completed .tag-num { color: #10B981; }
.tag-title { font-size: 13px; font-weight: 700; color: var(--text-main); }

.tool-badge { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; background: var(--bg-main); color: var(--text-main); border: 1px solid var(--border-light); border-radius: var(--radius-sm); font-size: 12px; font-weight: 700; transition: all 0.2s ease; }
.tool-icon { flex-shrink: 0; }

.tool-badge.tool-purple { background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%); border-color: #C4B5FD; color: #6D28D9; }
.tool-badge.tool-purple .tool-icon { stroke: #7C3AED; }
.tool-badge.tool-blue { background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-color: #93C5FD; color: #1D4ED8; }
.tool-badge.tool-blue .tool-icon { stroke: #2563EB; }
.tool-badge.tool-green { background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%); border-color: #86EFAC; color: #15803D; }
.tool-badge.tool-green .tool-icon { stroke: #16A34A; }
.tool-badge.tool-orange { background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%); border-color: #FDBA74; color: #C2410C; }
.tool-badge.tool-orange .tool-icon { stroke: #EA580C; }
.tool-badge.tool-cyan { background: linear-gradient(135deg, #ECFEFF 0%, #CFFAFE 100%); border-color: #67E8F9; color: #0E7490; }
.tool-badge.tool-cyan .tool-icon { stroke: #0891B2; }
.tool-badge.tool-pink { background: linear-gradient(135deg, #FDF2F8 0%, #FCE7F3 100%); border-color: #F9A8D4; color: #BE185D; }
.tool-badge.tool-pink .tool-icon { stroke: #DB2777; }
.tool-badge.tool-gray { background: linear-gradient(135deg, var(--bg-main) 0%, var(--border-light) 100%); border-color: var(--border-focus); color: var(--text-main); }
.tool-badge.tool-gray .tool-icon { stroke: var(--text-muted); }

.tool-params { margin-top: 12px; background: transparent; border-radius: 0; padding: 12px 0 0 0; border-top: 1px dashed var(--border-light); overflow-x: auto; }
.tool-params pre { margin: 0; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-muted); white-space: pre-wrap; word-break: break-all; background: var(--bg-main); border: 1px solid var(--border-light); border-radius: var(--radius-sm); padding: 16px; }

/* Result Wrapper */
.result-wrapper { background: transparent; border: none; border-top: 1px solid var(--border-light); border-radius: 0; padding: 16px 0 0 0; margin-top: 12px;}
.result-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.result-tool { font-size: 12px; font-weight: 800; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.05em;}
.result-size { font-size: 10px; font-weight: 700; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; background: var(--bg-main); padding: 2px 6px; border-radius: 4px;}
.result-raw { margin-top: 12px; max-height: 300px; overflow-y: auto; }
.result-raw pre { margin: 0; font-family: 'JetBrains Mono', monospace; font-size: 12px; white-space: pre-wrap; word-break: break-word; color: #334155; background: var(--bg-main); border: 1px solid var(--border-light); padding: 16px; border-radius: var(--radius-sm); }
.raw-preview { margin: 0; font-family: 'JetBrains Mono', monospace; font-size: 12px; white-space: pre-wrap; word-break: break-word; color: var(--text-muted); }

/* LLM Response */
.llm-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.meta-tag { font-size: 10px; padding: 4px 10px; background: var(--bg-main); color: var(--text-muted); border-radius: 6px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; border: 1px solid var(--border-light);}
.meta-tag.active { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE;}
.meta-tag.final-answer { background: #ECFDF5; color: #059669; border-color: #A7F3D0;}

.final-answer-hint { display: flex; align-items: center; gap: 10px; margin-top: 12px; padding: 12px 16px; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: var(--radius-sm); color: #065F46; font-size: 13px; font-weight: 700; }
.final-answer-hint svg { flex-shrink: 0; }
.llm-content { margin-top: 12px; max-height: 250px; overflow-y: auto; }
.llm-content pre { margin: 0; font-family: 'JetBrains Mono', monospace; font-size: 12px; white-space: pre-wrap; word-break: break-word; color: #334155; background: var(--bg-main); padding: 16px; border-radius: var(--radius-sm); border: 1px solid var(--border-light);}

/* Complete Banner */
.complete-banner { display: flex; align-items: center; gap: 12px; padding: 16px 20px; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: var(--radius-md); color: #065F46; font-weight: 800; font-size: 15px; }

/* Workflow Empty */
.workflow-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 20px; color: var(--text-muted); font-size: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em;}
.empty-pulse { width: 32px; height: 32px; background: var(--border-light); border-radius: 50%; margin-bottom: 20px; animation: pulse-ring 1.5s infinite; }
@keyframes pulse-ring { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.3); opacity: 0.5; } }

/* ==========================================================================
   DYNAMIC SUB-COMPONENTS (THE RENDER FUNCTIONS)
   Overhauled for Premium Layout & Segmented Controls
   ========================================================================== */

/* Structure & Layout */
:deep(.insight-display), :deep(.panorama-display), :deep(.quick-search-display), :deep(.interview-display) {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Headers */
:deep(.insight-header), :deep(.panorama-header), :deep(.quicksearch-header), :deep(.interview-header) {
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}

:deep(.header-main) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

:deep(.header-title) {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-main);
}

:deep(.header-stats) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  background: #FFFFFF;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-light);
}

:deep(.stat-item) { display: flex; gap: 4px; }
:deep(.stat-value) { font-weight: 800; color: var(--primary); font-family: 'JetBrains Mono', monospace; }
:deep(.stat-label) { font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-size: 10px;}

:deep(.header-topic) {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  line-height: 1.5;
}

:deep(.header-scenario) {
  margin-top: 12px;
  padding: 12px 16px;
  background: #EFF6FF;
  border-left: 3px solid var(--primary);
  border-radius: 0 8px 8px 0;
  font-size: 13px;
  color: #1E3A8A;
  line-height: 1.5;
}

:deep(.scenario-label) { font-weight: 800; margin-right: 4px; }

/* Tabs (Apple Segmented Control Style) */
:deep(.insight-tabs), :deep(.panorama-tabs), :deep(.quicksearch-tabs), :deep(.agent-tabs) {
  display: inline-flex;
  background: var(--bg-main);
  padding: 4px;
  border-radius: 10px;
  gap: 4px;
  overflow-x: auto;
  border: 1px solid var(--border-light);
  width: fit-content;
  max-width: 100%;
}

:deep(.insight-tab), :deep(.panorama-tab), :deep(.quicksearch-tab), :deep(.agent-tab) {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

:deep(.insight-tab:hover), :deep(.panorama-tab:hover), :deep(.quicksearch-tab:hover), :deep(.agent-tab:hover) {
  color: var(--text-main);
}

:deep(.insight-tab.active), :deep(.panorama-tab.active), :deep(.quicksearch-tab.active), :deep(.agent-tab.active) {
  background: #FFFFFF;
  color: var(--primary);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Tab Content Panels */
:deep(.insight-content), :deep(.panorama-content), :deep(.quicksearch-content), :deep(.interview-detail) {
  background: #FFFFFF;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}

:deep(.panel-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--bg-main);
}

:deep(.panel-title) {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-main);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

:deep(.panel-count) {
  font-size: 11px;
  font-weight: 800;
  color: var(--text-muted);
  background: var(--bg-main);
  padding: 4px 10px;
  border-radius: 6px;
}

/* Lists */
:deep(.facts-list), :deep(.relations-list), :deep(.edges-list), :deep(.subqueries-list) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Fact Items */
:deep(.fact-item), :deep(.subquery-item) {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  transition: all 0.2s;
}

:deep(.fact-item:hover), :deep(.subquery-item:hover) {
  border-color: var(--border-focus);
  background: #F1F5F9;
}

:deep(.fact-number), :deep(.subquery-number) {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border: 1px solid var(--border-light);
  border-radius: 50%;
  font-size: 11px;
  font-weight: 800;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

:deep(.fact-content), :deep(.subquery-text) {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  padding-top: 4px;
  font-weight: 500;
}

/* Relationship & Edge Chains (FIXED MASHED TEXT) */
:deep(.relation-item), :deep(.edge-item) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-main);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  flex-wrap: wrap;
}

:deep(.rel-source), :deep(.rel-target), :deep(.edge-source), :deep(.edge-target) {
  padding: 6px 12px;
  background: #FFFFFF;
  border: 1px solid var(--border-focus);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-main);
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

:deep(.rel-arrow), :deep(.edge-arrow) {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

:deep(.rel-line), :deep(.edge-line) {
  flex: 1;
  height: 2px;
  background: var(--border-focus);
}

:deep(.rel-label), :deep(.edge-label) {
  padding: 4px 10px;
  background: #EEF2FF;
  border: 1px solid #C7D2FE;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 800;
  color: #4F46E5;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

/* Entities & Nodes Grid */
:deep(.entities-grid), :deep(.nodes-grid) {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

:deep(.entity-tag), :deep(.node-tag) {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #FFFFFF;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

:deep(.entity-name), :deep(.node-name) {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
}

:deep(.entity-type), :deep(.node-type) {
  font-size: 10px;
  font-weight: 800;
  color: #8B5CF6;
  background: #F5F3FF;
  padding: 4px 8px;
  border-radius: 6px;
  text-transform: uppercase;
}

:deep(.entity-fact-count) {
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 700;
  margin-left: 4px;
}

/* Empty States */
:deep(.empty-state) {
  padding: 32px;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-main);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border-light);
}

/* ----------------------------------------------------
   SOLID DARK TERMINAL (LOCKED TO STEP 3 STYLE)
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
  text-transform: uppercase;
}

.log-id {
  color: #475569;
  font-weight: 600;
}

.log-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  height: 120px;
  overflow-y: auto;
  padding-right: 8px;
  scroll-behavior: smooth;
}

.log-content::-webkit-scrollbar { width: 6px; }
.log-content::-webkit-scrollbar-track { background: transparent; }
.log-content::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
.log-content::-webkit-scrollbar-thumb:hover { background: #475569; }

.log-line {
  font-size: 12px;
  line-height: 1.5;
}

.log-msg {
  color: #F8FAFC !important;
  word-break: break-all;
}

.log-msg.error { color: #EF4444 !important; }
.log-msg.warning { color: #F59E0B !important; }
.log-msg.success { color: #10B981 !important; }
</style>