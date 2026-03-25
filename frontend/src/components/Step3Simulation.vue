<template>
  <div class="simulation-panel">
    
    <div class="control-bar">
      <div class="status-group">
        <div class="platform-status twitter" :class="{ active: runStatus.twitter_running, completed: runStatus.twitter_completed }">
          <div class="platform-bg-glow"></div>
          <div class="platform-header">
            <div class="icon-wrapper">
              <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
            </div>
            <span class="platform-name">Info Plaza</span>
            <span v-if="runStatus.twitter_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">ROUND</span>
              <span class="stat-value mono">{{ runStatus.twitter_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">ELAPSED</span>
              <span class="stat-value mono">{{ twitterElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">ACTS</span>
              <span class="stat-value mono">{{ runStatus.twitter_actions_count || 0 }}</span>
            </span>
          </div>
        </div>
        
        <div class="platform-status reddit" :class="{ active: runStatus.reddit_running, completed: runStatus.reddit_completed }">
          <div class="platform-bg-glow"></div>
          <div class="platform-header">
            <div class="icon-wrapper">
              <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
              </svg>
            </div>
            <span class="platform-name">Topic Community</span>
            <span v-if="runStatus.reddit_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">ROUND</span>
              <span class="stat-value mono">{{ runStatus.reddit_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">ELAPSED</span>
              <span class="stat-value mono">{{ redditElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">ACTS</span>
              <span class="stat-value mono">{{ runStatus.reddit_actions_count || 0 }}</span>
            </span>
          </div>
        </div>

        <div
          v-if="linkedinEnabled"
          class="platform-status linkedin"
          :class="{ active: runStatus.linkedin_running, completed: runStatus.linkedin_completed }"
        >
          <div class="platform-bg-glow"></div>
          <div class="platform-header">
            <div class="icon-wrapper">
              <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
                <rect x="3" y="3" width="18" height="18" rx="2"></rect><line x1="8" y1="10" x2="8" y2="16"></line><line x1="12" y1="10" x2="12" y2="16"></line><path d="M16 16v-3.5a2 2 0 0 0-4 0V16"></path><circle cx="8" cy="7.5" r="0.8" fill="currentColor" stroke="none"></circle>
              </svg>
            </div>
            <span class="platform-name">Professional Network</span>
            <span v-if="runStatus.linkedin_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">ROUND</span>
              <span class="stat-value mono">{{ runStatus.linkedin_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">ELAPSED</span>
              <span class="stat-value mono">{{ linkedinElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">ACTS</span>
              <span class="stat-value mono">{{ runStatus.linkedin_actions_count || 0 }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content-area custom-scrollbar" ref="scrollContainer">
      
      <div class="trends-accordion" v-if="allActions.length > 0">
        <button class="trends-toggle-btn" @click="showTrends = !showTrends">
          <div class="toggle-left">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            <span>Trends & Analytics</span>
          </div>
          <svg class="chevron-icon" :class="{ 'open': showTrends }" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <Transition name="expand">
          <div v-show="showTrends" class="trends-body">
            <TrendsHeatmap 
              :actions="allActions"
              :rounds="runStatus.total_rounds || maxRounds"
              :loading="isStarting"
            />
          </div>
        </Transition>
      </div>

      <div class="timeline-header glass-panel" v-if="allActions.length > 0">
        <div class="timeline-stats">
          <span class="total-count">TOTAL EVENTS <span class="mono badge-count">{{ allActions.length }}</span></span>
          <div class="stats-divider"></div>
          <span class="platform-breakdown">
            <span class="breakdown-item twitter">
              <svg class="mini-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
              <span class="mono">{{ twitterActionsCount }}</span>
            </span>
            <span class="breakdown-item reddit">
              <svg class="mini-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
              <span class="mono">{{ redditActionsCount }}</span>
            </span>
            <template v-if="linkedinEnabled">
              <span class="breakdown-item linkedin">
                <svg class="mini-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2"></rect><line x1="8" y1="10" x2="8" y2="16"></line><line x1="12" y1="10" x2="12" y2="16"></line><path d="M16 16v-3.5a2 2 0 0 0-4 0V16"></path><circle cx="8" cy="7.5" r="0.8" fill="currentColor" stroke="none"></circle></svg>
                <span class="mono">{{ linkedinActionsCount }}</span>
              </span>
            </template>
          </span>
        </div>
      </div>
      
      <div class="timeline-feed">
        <div class="timeline-axis"></div>
        
        <TransitionGroup name="timeline-item" tag="div" class="timeline-wrapper">
          <div 
            v-for="action in chronologicalActions" 
            :key="action._uniqueId || action.id || `${action.timestamp}-${action.agent_id}`" 
            class="timeline-item"
            :class="action.platform"
          >
            <div class="timeline-marker">
              <div class="marker-dot"></div>
              <div class="marker-glow"></div>
            </div>
            
            <div class="timeline-card">
              <div class="card-header">
                <div class="agent-info">
                  <div class="avatar-placeholder mesh-gradient">{{ (action.agent_name || 'A')[0] }}</div>
                  <span class="agent-name">{{ action.agent_name }}</span>
                </div>
                
                <div class="header-meta">
                  <div class="action-badge" :class="getActionTypeClass(action.action_type)">
                    {{ getActionTypeLabel(action.action_type) }}
                  </div>
                </div>
              </div>
              
              <div class="card-body">
                <div v-if="action.action_type === 'CREATE_POST' && action.action_args?.content" class="content-text main-text">
                  {{ action.action_args.content }}
                </div>

                <template v-if="action.action_type === 'QUOTE_POST'">
                  <div v-if="action.action_args?.quote_content" class="content-text main-text">
                    {{ action.action_args.quote_content }}
                  </div>
                  <div v-if="action.action_args?.original_content" class="quoted-block">
                    <div class="quote-header">
                      <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                      <span class="quote-label">@{{ action.action_args.original_author_name || 'User' }}</span>
                    </div>
                    <div class="quote-text">
                      {{ truncateContent(action.action_args.original_content, 150) }}
                    </div>
                  </div>
                </template>

                <template v-if="action.action_type === 'REPOST'">
                  <div class="repost-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
                    <span class="repost-label">Reposted from <span class="highlight-user">@{{ action.action_args?.original_author_name || 'User' }}</span></span>
                  </div>
                  <div v-if="action.action_args?.original_content" class="repost-content">
                    {{ truncateContent(action.action_args.original_content, 200) }}
                  </div>
                </template>

                <template v-if="action.action_type === 'LIKE_POST'">
                  <div class="like-info">
                    <svg class="icon-small filled pink" viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                    <span class="like-label">Liked <span class="highlight-user">@{{ action.action_args?.post_author_name || 'User' }}</span>'s post</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="liked-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <template v-if="action.action_type === 'CREATE_COMMENT'">
                  <div v-if="action.action_args?.content" class="content-text main-text">
                    {{ action.action_args.content }}
                  </div>
                  <div v-if="action.action_args?.post_id" class="comment-context">
                    <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                    <span>Reply to post <span class="mono-id">#{{ action.action_args.post_id }}</span></span>
                  </div>
                </template>

                <template v-if="action.action_type === 'SEARCH_POSTS'">
                  <div class="search-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span class="search-label">Searched for:</span>
                    <span class="search-query">"{{ action.action_args?.query || '' }}"</span>
                  </div>
                </template>

                <template v-if="action.action_type === 'FOLLOW'">
                  <div class="follow-info">
                    <svg class="icon-small blue" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                    <span class="follow-label">Started following <span class="highlight-user">@{{ action.action_args?.target_user || action.action_args?.user_id || 'User' }}</span></span>
                  </div>
                </template>

                <template v-if="action.action_type === 'UPVOTE_POST' || action.action_type === 'DOWNVOTE_POST'">
                  <div class="vote-info">
                    <svg v-if="action.action_type === 'UPVOTE_POST'" class="icon-small green" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15"></polyline></svg>
                    <svg v-else class="icon-small red" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    <span class="vote-label">{{ action.action_type === 'UPVOTE_POST' ? 'Upvoted' : 'Downvoted' }} Post</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="voted-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <template v-if="action.action_type === 'DO_NOTHING'">
                  <div class="idle-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span class="idle-label">Action Skipped</span>
                  </div>
                </template>

                <div v-if="!['CREATE_POST', 'QUOTE_POST', 'REPOST', 'LIKE_POST', 'CREATE_COMMENT', 'SEARCH_POSTS', 'FOLLOW', 'UPVOTE_POST', 'DOWNVOTE_POST', 'DO_NOTHING'].includes(action.action_type) && action.action_args?.content" class="content-text main-text">
                  {{ action.action_args.content }}
                </div>
              </div>

              <div class="card-footer">
                <div class="footer-left">
                  <div class="platform-indicator" :class="action.platform">
                    <svg v-if="action.platform === 'twitter'" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                    <svg v-else-if="action.platform === 'reddit'" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                    <svg v-else viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2"></rect><line x1="8" y1="10" x2="8" y2="16"></line><line x1="12" y1="10" x2="12" y2="16"></line><path d="M16 16v-3.5a2 2 0 0 0-4 0V16"></path><circle cx="8" cy="7.5" r="0.8" fill="currentColor" stroke="none"></circle></svg>
                    <span>{{ getPlatformDisplayName(action.platform) }}</span>
                  </div>
                </div>
                <div class="footer-right">
                  <span class="round-tag">R{{ action.round_num }}</span>
                  <span class="time-tag">{{ formatActionTime(action.timestamp) }}</span>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>

        <div v-if="allActions.length === 0" class="waiting-state">
          <div class="radar-container">
            <div class="radar-core"></div>
            <div class="radar-ring ring-1"></div>
            <div class="radar-ring ring-2"></div>
            <div class="radar-ring ring-3"></div>
          </div>
          <span class="waiting-text">Awaiting Entity Actions...</span>
        </div>
      </div>
    </div>

    <div class="action-footer">
      <div class="footer-hint">
        <span v-if="phase < 2" class="hint-waiting">
          <span class="spinner-tiny"></span> Simulation in progress. Report generation will be available upon completion.
        </span>
        <span v-else class="hint-ready">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
          Simulation complete. Ready to synthesize report.
        </span>
      </div>

      <button 
        class="action-btn primary"
        :disabled="phase !== 2 || isGeneratingReport"
        @click="handleNextStep"
      >
        <span class="btn-content">
          <span v-if="isGeneratingReport" class="loading-spinner-small"></span>
          {{ isGeneratingReport ? 'Launching...' : 'Generate Synthesis Report' }} 
          <svg v-if="!isGeneratingReport" class="arrow-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </span>
      </button>
    </div>

    <div class="system-logs">
      <div class="log-header">
        <div class="log-title-group">
          <div class="status-dot pulsing"></div>
          <span class="log-title">SIMULATION ENGINE TERMINAL</span>
        </div>
        <span class="log-id">{{ simulationId || 'NO_SIMULATION' }}</span>
      </div>
      <div class="log-content custom-scrollbar" ref="logContent">
        <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
          <span class="log-time">[{{ log.time }}]</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import TrendsHeatmap from './TrendsHeatmap.vue'
import { 
  startSimulation, 
  stopSimulation,
  getRunStatus, 
  getRunStatusDetail
} from '../api/simulation'
import { generateReport } from '../api/report'

const props = defineProps({
  simulationId: String,
  simulationData: Object,
  maxRounds: Number, 
  minutesPerRound: {
    type: Number,
    default: 30 
  },
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])
const router = useRouter()

const isGeneratingReport = ref(false)
const showTrends = ref(false) // Toggle state for Trends Dropdown
const phase = ref(0) 
const isStarting = ref(false)
const isStopping = ref(false)
const startError = ref(null)
const runStatus = ref({})
const allActions = ref([]) 
const actionIds = ref(new Set()) 
const scrollContainer = ref(null)

const chronologicalActions = computed(() => {
  return allActions.value
})

const twitterActionsCount = computed(() => allActions.value.filter(a => a.platform === 'twitter').length)
const redditActionsCount = computed(() => allActions.value.filter(a => a.platform === 'reddit').length)
const linkedinActionsCount = computed(() => allActions.value.filter(a => a.platform === 'linkedin').length)

const linkedinEnabled = computed(() => {
  return Boolean(
    props.simulationData?.enable_linkedin ||
    runStatus.value.linkedin_running ||
    runStatus.value.linkedin_completed ||
    (runStatus.value.linkedin_actions_count || 0) > 0 ||
    linkedinActionsCount.value > 0
  )
})

const formatElapsedTime = (currentRound) => {
  if (!currentRound || currentRound <= 0) return '0h 0m'
  const totalMinutes = currentRound * props.minutesPerRound
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h ${minutes}m`
}

const twitterElapsedTime = computed(() => formatElapsedTime(runStatus.value.twitter_current_round || 0))
const redditElapsedTime = computed(() => formatElapsedTime(runStatus.value.reddit_current_round || 0))
const linkedinElapsedTime = computed(() => formatElapsedTime(runStatus.value.linkedin_current_round || 0))

const addLog = (msg) => emit('add-log', msg)

const resetAllState = () => {
  phase.value = 0
  runStatus.value = {}
  allActions.value = []
  actionIds.value = new Set()
  prevTwitterRound.value = 0
  prevRedditRound.value = 0
  prevLinkedinRound.value = 0
  startError.value = null
  isStarting.value = false
  isStopping.value = false
  stopPolling()  
}

const doStartSimulation = async () => {
  if (!props.simulationId) {
    addLog('Error: Missing simulationId')
    return
  }

  resetAllState()
  
  isStarting.value = true
  startError.value = null
  addLog('Starting dual-platform parallel sim...')
  emit('update-status', 'processing')
  
  try {
    const params = {
      simulation_id: props.simulationId,
      platform: 'parallel',
      force: true, 
      enable_graph_memory_update: true 
    }
    
    if (props.maxRounds) {
      params.max_rounds = props.maxRounds
      addLog(`Max simulation rounds set: ${props.maxRounds}`)
    }
    
    addLog('Dynamic graph updating enabled')
    
    const res = await startSimulation(params)
    
    if (res.success && res.data) {
      if (res.data.force_restarted) addLog('✓ Cleared old logs, starting fresh.')
      addLog('✓ Simulation Engine started successfully')
      addLog(`  ├─ PID: ${res.data.process_pid || '-'}`)
      
      phase.value = 1
      runStatus.value = res.data
      
      startStatusPolling()
      startDetailPolling()
    } else {
      startError.value = res.error || 'Unknown error'
      addLog(`✗ Start failed: ${res.error || 'Unknown error'}`)
      emit('update-status', 'error')
    }
  } catch (err) {
    startError.value = err.message
    addLog(`✗ Start error: ${err.message}`)
    emit('update-status', 'error')
  } finally {
    isStarting.value = false
  }
}

const handleStopSimulation = async () => {
  if (!props.simulationId) return
  isStopping.value = true
  addLog('Stopping simulation...')
  
  try {
    const res = await stopSimulation({ simulation_id: props.simulationId })
    if (res.success) {
      addLog('✓ Simulation stopped')
      phase.value = 2
      stopPolling()
      emit('update-status', 'completed')
    } else {
      addLog(`Stop failed: ${res.error || 'Unknown error'}`)
    }
  } catch (err) {
    addLog(`Stop error: ${err.message}`)
  } finally {
    isStopping.value = false
  }
}

let statusTimer = null
let detailTimer = null

const startStatusPolling = () => statusTimer = setInterval(fetchRunStatus, 2000)
const startDetailPolling = () => detailTimer = setInterval(fetchRunStatusDetail, 3000)

const stopPolling = () => {
  if (statusTimer) { clearInterval(statusTimer); statusTimer = null }
  if (detailTimer) { clearInterval(detailTimer); detailTimer = null }
}

const prevTwitterRound = ref(0)
const prevRedditRound = ref(0)
const prevLinkedinRound = ref(0)

const fetchRunStatus = async () => {
  if (!props.simulationId) return
  try {
    const res = await getRunStatus(props.simulationId)
    if (res.success && res.data) {
      const data = res.data
      runStatus.value = data
      
      if (data.twitter_current_round > prevTwitterRound.value) {
        addLog(`[Info Plaza] R${data.twitter_current_round}/${data.total_rounds} | T:${data.twitter_simulated_hours || 0}h | A:${data.twitter_actions_count}`)
        prevTwitterRound.value = data.twitter_current_round
      }
      if (data.reddit_current_round > prevRedditRound.value) {
        addLog(`[Topic Community] R${data.reddit_current_round}/${data.total_rounds} | T:${data.reddit_simulated_hours || 0}h | A:${data.reddit_actions_count}`)
        prevRedditRound.value = data.reddit_current_round
      }
      if (data.linkedin_current_round > prevLinkedinRound.value) {
        addLog(`[Professional Network] R${data.linkedin_current_round}/${data.total_rounds} | T:${data.linkedin_simulated_hours || 0}h | A:${data.linkedin_actions_count || 0}`)
        prevLinkedinRound.value = data.linkedin_current_round
      }
      
      const isCompleted = data.runner_status === 'completed' || data.runner_status === 'stopped'
      const platformsCompleted = checkPlatformsCompleted(data)
      
      if (isCompleted || platformsCompleted) {
        if (platformsCompleted && !isCompleted) addLog('✓ All platforms have completed their simulation cycles.')
        addLog('✓ Simulation Complete')
        phase.value = 2
        stopPolling()
        emit('update-status', 'completed')
      }
    }
  } catch (err) { console.warn('Run status fetch failed:', err) }
}

const checkPlatformsCompleted = (data) => {
  if (!data) return false
  const twitterCompleted = data.twitter_completed === true
  const redditCompleted = data.reddit_completed === true
  const linkedinCompleted = data.linkedin_completed === true
  
  const twitterEnabled = (data.twitter_actions_count > 0) || data.twitter_running || twitterCompleted
  const redditEnabled = (data.reddit_actions_count > 0) || data.reddit_running || redditCompleted
  const linkedinEnabled = (data.linkedin_actions_count > 0) || data.linkedin_running || linkedinCompleted || props.simulationData?.enable_linkedin
  
  if (!twitterEnabled && !redditEnabled && !linkedinEnabled) return false
  if (twitterEnabled && !twitterCompleted) return false
  if (redditEnabled && !redditCompleted) return false
  if (linkedinEnabled && !linkedinCompleted) return false
  return true
}

const fetchRunStatusDetail = async () => {
  if (!props.simulationId) return
  try {
    const res = await getRunStatusDetail(props.simulationId)
    if (res.success && res.data) {
      const serverActions = res.data.all_actions || []
      serverActions.forEach(action => {
        const actionId = action.id || `${action.timestamp}-${action.platform}-${action.agent_id}-${action.action_type}`
        if (!actionIds.value.has(actionId)) {
          actionIds.value.add(actionId)
          allActions.value.push({ ...action, _uniqueId: actionId })
        }
      })
    }
  } catch (err) { console.warn('Detail status fetch failed:', err) }
}

const getActionTypeLabel = (type) => {
  const labels = {
    'CREATE_POST': 'POST', 'REPOST': 'REPOST', 'LIKE_POST': 'LIKE',
    'CREATE_COMMENT': 'COMMENT', 'LIKE_COMMENT': 'LIKE', 'DO_NOTHING': 'IDLE',
    'FOLLOW': 'FOLLOW', 'SEARCH_POSTS': 'SEARCH', 'QUOTE_POST': 'QUOTE',
    'UPVOTE_POST': 'UPVOTE', 'DOWNVOTE_POST': 'DOWNVOTE'
  }
  return labels[type] || type || 'UNKNOWN'
}

const getActionTypeClass = (type) => {
  const classes = {
    'CREATE_POST': 'badge-post', 'REPOST': 'badge-repost', 'LIKE_POST': 'badge-like',
    'CREATE_COMMENT': 'badge-comment', 'LIKE_COMMENT': 'badge-like', 'QUOTE_POST': 'badge-quote',
    'FOLLOW': 'badge-follow', 'SEARCH_POSTS': 'badge-search', 'UPVOTE_POST': 'badge-upvote',
    'DOWNVOTE_POST': 'badge-downvote', 'DO_NOTHING': 'badge-idle'
  }
  return classes[type] || 'badge-default'
}

const truncateContent = (content, maxLength = 100) => {
  if (!content) return ''
  if (content.length > maxLength) return content.substring(0, maxLength) + '...'
  return content
}

const getPlatformDisplayName = (platform) => {
  if (platform === 'twitter') return 'Info Plaza'
  if (platform === 'reddit') return 'Topic Community'
  if (platform === 'linkedin') return 'Professional Network'
  return platform || 'Unknown'
}

const formatActionTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const handleNextStep = async () => {
  if (!props.simulationId) { addLog('Error: Missing simulationId'); return }
  if (isGeneratingReport.value) { addLog('Starting report generation...'); return }

  isGeneratingReport.value = true
  addLog('Starting report generation...')
  
  try {
    const res = await generateReport({ simulation_id: props.simulationId, force_regenerate: true })
    if (res.success && res.data) {
      const reportId = res.data.report_id
      addLog(`✓ Report task started: ${reportId}`)
      router.push({ name: 'Report', params: { reportId } })
    } else {
      addLog(`✗ Report start failed: ${res.error || 'Unknown error'}`)
      isGeneratingReport.value = false
    }
  } catch (err) {
    addLog(`✗ Report start exception: ${err.message}`)
    isGeneratingReport.value = false
  }
}

const logContent = ref(null)
watch(() => props.systemLogs?.length, () => {
  nextTick(() => { if (logContent.value) logContent.value.scrollTop = logContent.value.scrollHeight })
})

onMounted(() => {
  addLog('Step 3 Run Initialization')
  if (props.simulationId) doStartSimulation()
})
onUnmounted(() => stopPolling())
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

/* Design System Colors */
.simulation-panel {
  --color-plaza: #3B82F6;
  --color-community: #F97316;
  --color-pro: #06B6D4;
  
  --bg-main: #F8FAFC;
  --bg-card: #FFFFFF;
  --text-main: #0F172A;
  --text-muted: #64748B;
  --border-light: #E2E8F0;
  
  --primary-gradient: linear-gradient(135deg, #2563EB, #7C3AED);
  --success: #10B981;
  
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  background-image: radial-gradient(#CBD5E1 1px, transparent 1px);
  background-size: 24px 24px;
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  overflow: hidden;
}

/* --- Control Bar (Top) --- */
.control-bar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 16px 24px;
  display: flex;
  border-bottom: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  z-index: 20;
}

.status-group { 
  display: flex; 
  gap: 16px; 
  width: 100%;
}

/* Platform Status Cards */
.platform-status {
  flex: 1; /* Makes them stretch evenly */
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.platform-bg-glow {
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  opacity: 0.3; transition: opacity 0.3s;
}

.platform-status.twitter .platform-bg-glow { background: var(--color-plaza); }
.platform-status.reddit .platform-bg-glow { background: var(--color-community); }
.platform-status.linkedin .platform-bg-glow { background: var(--color-pro); }

.platform-status.active {
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
  transform: translateY(-2px);
}
.platform-status.active .platform-bg-glow { opacity: 1; }

.platform-status.twitter.active { border-color: rgba(59, 130, 246, 0.3); box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12); }
.platform-status.reddit.active { border-color: rgba(249, 115, 22, 0.3); box-shadow: 0 8px 24px rgba(249, 115, 22, 0.12); }
.platform-status.linkedin.active { border-color: rgba(6, 182, 212, 0.3); box-shadow: 0 8px 24px rgba(6, 182, 212, 0.12); }

.platform-status.completed {
  border-color: var(--success);
  background: #F0FDF4;
}
.platform-status.completed .platform-bg-glow { background: var(--success); opacity: 1; }

.platform-header { display: flex; align-items: center; gap: 10px; margin-bottom: 2px; }
.icon-wrapper { display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 6px; background: #F1F5F9; color: var(--text-muted); transition: all 0.3s; }
.platform-status.active.twitter .icon-wrapper { background: #EFF6FF; color: var(--color-plaza); }
.platform-status.active.reddit .icon-wrapper { background: #FFF7ED; color: var(--color-community); }
.platform-status.active.linkedin .icon-wrapper { background: #ECFEFF; color: var(--color-pro); }

.platform-name { font-size: 13px; font-weight: 800; color: var(--text-main); letter-spacing: 0.05em; text-transform: uppercase; }
.status-badge { margin-left: auto; color: var(--success); display: flex; align-items: center; filter: drop-shadow(0 0 4px rgba(16, 185, 129, 0.4)); }

.platform-stats { display: flex; gap: 14px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-label { font-size: 9px; color: var(--text-muted); font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-value { font-size: 14px; font-weight: 800; color: var(--text-main); font-family: 'JetBrains Mono', monospace; }
.stat-total { font-size: 10px; color: #94A3B8; font-weight: 600; }

/* --- Action Footer (Bottom) --- */
.action-footer {
  padding: 16px 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 20;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.02);
}

.footer-hint {
  display: flex;
  align-items: center;
}

.hint-waiting {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #64748B;
}

.hint-ready {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #059669; /* Emerald */
}

/* Spinner Tiny */
.spinner-tiny {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #CBD5E1;
  border-top-color: #3B82F6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Action Button inside Footer */
.action-btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 14px 32px; font-size: 14px; font-weight: 800; border: none; border-radius: 999px;
  cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #FFF; box-shadow: 0 4px 14px rgba(0,0,0,0.1); text-transform: uppercase; letter-spacing: 0.05em;
  background: #0F172A; /* Solid Dark Slate */
}

.action-btn.primary:hover:not(:disabled) { 
  background: #2563EB; /* Clean vibrant blue on hover */
  transform: translateY(-2px); 
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25); 
}

/* Disabled State */
.action-btn:disabled { 
  background: #F1F5F9; 
  color: #94A3B8; 
  cursor: not-allowed; 
  transform: none; 
  box-shadow: none; 
  border: 1px solid #E2E8F0;
}

.btn-content { position: relative; z-index: 1; display: flex; align-items: center; gap: 8px; }
.arrow-icon { transition: transform 0.2s; }
.action-btn:hover:not(:disabled) .arrow-icon { transform: translateX(4px); }


/* --- Main Content Area --- */
.main-content-area { flex: 1; overflow-y: auto; position: relative; }

/* Trends Dropdown (Accordion) */
.trends-accordion {
  margin: 24px 24px 0 24px;
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  overflow: hidden;
  transition: all 0.3s ease;
}

.trends-toggle-btn {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 14px;
  font-weight: 800;
  color: var(--text-main);
  transition: background 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.trends-toggle-btn:hover {
  background: #F8FAFC;
}

.toggle-left {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--color-plaza);
}

.chevron-icon {
  color: var(--text-muted);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.chevron-icon.open {
  transform: rotate(180deg);
}

.trends-body {
  border-top: 1px solid var(--border-light);
  background: #FAFAFA;
  padding: 16px;
}

/* Expand Transition */
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  max-height: 500px;
  opacity: 1;
}
.expand-enter-from, .expand-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0 16px;
  border-top-color: transparent;
}


/* Timeline Header */
.timeline-header {
  position: sticky; top: 0;
  padding: 16px 24px; border-bottom: 1px solid var(--border-light); z-index: 15;
  display: flex; justify-content: center;
  background: rgba(248, 250, 252, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.timeline-stats {
  display: flex; align-items: center; gap: 16px;
  background: #FFF; padding: 8px 20px; border-radius: 999px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04); border: 1px solid var(--border-light);
}
.total-count { font-size: 11px; font-weight: 800; color: var(--text-muted); display: flex; align-items: center; gap: 8px; letter-spacing: 0.05em; }
.badge-count { background: #0F172A; color: #FFF; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
.stats-divider { width: 1px; height: 16px; background: var(--border-light); }
.platform-breakdown { display: flex; align-items: center; gap: 12px; }
.breakdown-item { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.breakdown-item.twitter { color: var(--color-plaza); }
.breakdown-item.reddit { color: var(--color-community); }
.breakdown-item.linkedin { color: var(--color-pro); }

/* --- Timeline Feed --- */
.timeline-feed { padding: 40px 0; position: relative; min-height: 100%; max-width: 900px; margin: 0 auto; }
.timeline-axis { position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: linear-gradient(to bottom, transparent, var(--border-light) 5%, var(--border-light) 95%, transparent); transform: translateX(-50%); z-index: 0; }
.timeline-item { display: flex; justify-content: center; margin-bottom: 40px; position: relative; width: 100%; z-index: 1; }

.timeline-marker {
  position: absolute; left: 50%; top: 24px;
  width: 14px; height: 14px; background: #FFF;
  border: 2px solid var(--border-light); border-radius: 50%;
  transform: translateX(-50%); z-index: 2;
  display: flex; align-items: center; justify-content: center;
}
.marker-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); position: relative; z-index: 2; }
.marker-glow { position: absolute; inset: -4px; border-radius: 50%; opacity: 0.3; z-index: 1; }

.timeline-item.twitter .marker-dot { background: var(--color-plaza); }
.timeline-item.twitter .timeline-marker { border-color: var(--color-plaza); }
.timeline-item.twitter .marker-glow { background: var(--color-plaza); filter: blur(4px); }

.timeline-item.reddit .marker-dot { background: var(--color-community); }
.timeline-item.reddit .timeline-marker { border-color: var(--color-community); }
.timeline-item.reddit .marker-glow { background: var(--color-community); filter: blur(4px); }

.timeline-item.linkedin .marker-dot { background: var(--color-pro); }
.timeline-item.linkedin .timeline-marker { border-color: var(--color-pro); }
.timeline-item.linkedin .marker-glow { background: var(--color-pro); filter: blur(4px); }

/* Card Layout */
.timeline-card {
  width: calc(100% - 64px); background: #FFF; border-radius: 16px; padding: 20px;
  border: 1px solid var(--border-light); box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  position: relative; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.timeline-card:hover { box-shadow: 0 10px 30px rgba(0,0,0,0.08); transform: translateY(-2px); border-color: var(--border-focus); }

/* Directional Alignment */
.timeline-item.twitter { justify-content: flex-start; padding-right: 50%; }
.timeline-item.twitter .timeline-card { margin-left: auto; margin-right: 40px; }
.timeline-item.reddit { justify-content: flex-end; padding-left: 50%; }
.timeline-item.reddit .timeline-card { margin-right: auto; margin-left: 40px; }
.timeline-item.linkedin { justify-content: center; }
.timeline-item.linkedin .timeline-card { width: min(640px, calc(100% - 120px)); margin: 0 auto; }

/* Card Content Styles */
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #F1F5F9; }
.agent-info { display: flex; align-items: center; gap: 12px; }

.mesh-gradient { background: linear-gradient(135deg, #3B82F6, #8B5CF6, #EC4899); color: #FFF; }
.avatar-placeholder { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.agent-name { font-size: 15px; font-weight: 800; color: var(--text-main); }
.header-meta { display: flex; align-items: center; gap: 8px; }

/* Action Badges */
.action-badge { font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 4px 10px; border-radius: 6px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
.badge-post { background: #EFF6FF; color: #2563EB; }
.badge-repost { background: #F3E8FF; color: #7C3AED; }
.badge-quote { background: #F0FDF4; color: #059669; }
.badge-comment { background: #F8FAFC; color: #475569; border: 1px solid #E2E8F0; }
.badge-like { background: #FDF2F8; color: #DB2777; }
.badge-follow { background: #ECFEFF; color: #0891B2; }
.badge-search { background: #FEF3C7; color: #D97706; }
.badge-upvote { background: #DCFCE7; color: #16A34A; }
.badge-downvote { background: #FEE2E2; color: #DC2626; }
.badge-idle { background: #F1F5F9; color: #94A3B8; }
.badge-default { background: #F1F5F9; color: #64748B; }

.content-text { font-size: 14px; line-height: 1.6; color: #334155; margin-bottom: 12px; word-break: break-word; }
.content-text.main-text { font-size: 15px; color: var(--text-main); }

/* Info Blocks (Quote, Repost, etc) */
.quoted-block, .repost-content { background: #F8FAFC; border: 1px solid var(--border-light); border-left: 3px solid var(--border-focus); padding: 12px 16px; border-radius: 0 8px 8px 0; margin-top: 12px; font-size: 13px; color: #475569; }
.quote-header, .repost-info, .like-info, .search-info, .follow-info, .vote-info, .idle-info, .comment-context { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.highlight-user { color: var(--text-main); font-weight: 800; font-family: 'JetBrains Mono', monospace; text-transform: none; letter-spacing: 0;}
.icon-small { color: #94A3B8; }
.icon-small.pink { color: #EC4899; }
.icon-small.blue { color: #3B82F6; }
.icon-small.green { color: #10B981; }
.icon-small.red { color: #EF4444; }

.search-query { font-family: 'JetBrains Mono', monospace; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; color: var(--text-main); text-transform: none; letter-spacing: 0;}
.mono-id { font-family: 'JetBrains Mono', monospace; color: var(--primary); text-transform: none; letter-spacing: 0;}

.card-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px dashed var(--border-light); }
.footer-left { display: flex; align-items: center; }
.platform-indicator { display: flex; align-items: center; gap: 6px; font-size: 10px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.platform-indicator.twitter { color: var(--color-plaza); }
.platform-indicator.reddit { color: var(--color-community); }
.platform-indicator.linkedin { color: var(--color-pro); }

.footer-right { display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #94A3B8; font-weight: 600;}
.round-tag { background: #F1F5F9; padding: 2px 6px; border-radius: 4px; font-weight: 800; color: var(--text-main); }
.time-tag { color: var(--text-muted); font-weight: 600; }

/* Waiting State (Radar) */
.waiting-state {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center; gap: 24px; color: var(--text-muted);
}
.waiting-text { font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; color: #64748B; }

.radar-container { position: relative; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; }
.radar-core { width: 12px; height: 12px; border-radius: 50%; background: var(--primary); z-index: 5; box-shadow: 0 0 10px var(--primary); }
.radar-ring { position: absolute; border-radius: 50%; border: 2px solid var(--primary); opacity: 0; animation: radar-ripple 3s cubic-bezier(0.165, 0.84, 0.44, 1) infinite; }
.ring-1 { animation-delay: 0s; }
.ring-2 { animation-delay: 1s; }
.ring-3 { animation-delay: 2s; }
@keyframes radar-ripple { 0% { width: 0; height: 0; opacity: 1; border-width: 3px; } 100% { width: 80px; height: 80px; opacity: 0; border-width: 0px; } }

/* Animation */
.timeline-item-enter-active, .timeline-item-leave-active { transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }
.timeline-item-enter-from { opacity: 0; transform: translateY(30px) scale(0.98); }
.timeline-item-leave-to { opacity: 0; }

/* ----------------------------------------------------
   SOLID DARK TERMINAL
   Forced !important overrides to prevent transparency
------------------------------------------------------- */
.system-logs {
  background-color: #0F172A !important; /* Forces solid dark slate */
  color: #94A3B8; 
  padding: 16px 24px;
  font-family: 'JetBrains Mono', ui-monospace, monospace; 
  border-top: 1px solid #1E293B; 
  flex-shrink: 0;
  box-shadow: 0 -4px 10px rgba(0,0,0,0.1); /* Slight shadow to lift it off the grid */
  position: relative;
  z-index: 30;
}
.log-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 11px; }
.log-title-group { display: flex; align-items: center; gap: 8px; }
.status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; }
.status-dot.pulsing { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); animation: pulse-green 2s infinite; }
@keyframes pulse-green { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }

.log-title { color: #38BDF8; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
.log-id { color: #475569; font-weight: 600; }
.log-content { display: flex; flex-direction: column; gap: 6px; height: 120px; overflow-y: auto; padding-right: 8px; scroll-behavior: smooth; }

/* Custom Scrollbars */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
.main-content-area::-webkit-scrollbar { width: 8px; }
.main-content-area::-webkit-scrollbar-track { background: transparent; }
.main-content-area::-webkit-scrollbar-thumb { background: var(--border-focus); border-radius: 4px; }
.main-content-area::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

.log-line { font-size: 12px; display: flex; gap: 12px; line-height: 1.5; }
.log-time { color: var(--success); min-width: 95px; opacity: 0.8; }
.log-msg { color: #F8FAFC !important; word-break: break-all; } /* Made log text brighter */
.mono { font-family: 'JetBrains Mono', monospace; }

/* Loading spinner */
.loading-spinner-small {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3); border-top-color: #FFF;
  border-radius: 50%; animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite; margin-right: 8px;
}
</style>