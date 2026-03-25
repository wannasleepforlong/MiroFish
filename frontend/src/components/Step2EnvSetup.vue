<template>
  <div class="workbench-panel">
    <div class="scroll-container custom-scrollbar">
      <div class="step-card" :class="{ 'active': phase === 0, 'completed': phase > 0 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">01</span>
            <span class="step-title">Simulation Initialization</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 0" class="badge success">COMPLETED</span>
            <span v-else class="badge processing">INITIALIZING</span>
          </div>
        </div>
        
        <div class="card-content">
          <p class="api-note">POST /api/simulation/create</p>
          <p class="description">
            Creating new simulation instance and loading parameters...
          </p>

          <div v-if="simulationId" class="info-card">
            <div class="info-row">
              <span class="info-label">Project ID</span>
              <span class="info-value mono">{{ projectData?.project_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Graph ID</span>
              <span class="info-value mono">{{ projectData?.graph_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Simulation ID</span>
              <span class="info-value mono">{{ simulationId }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Task ID</span>
              <span class="info-value mono">{{ taskId || 'Async task completed' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="step-card" :class="{ 'active': phase === 1, 'completed': phase > 1 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">02</span>
            <span class="step-title">Generate Agent Personas</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 1" class="badge success">COMPLETED</span>
            <span v-else-if="phase === 1" class="badge processing">{{ prepareProgress }}%</span>
            <span v-else class="badge pending">PENDING</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            Automatically extract entities from graph and initialize simulated personas.
          </p>

          <div v-if="profiles.length > 0" class="stats-grid">
            <div class="stat-card">
              <span class="stat-value">{{ profiles.length }}</span>
              <span class="stat-label">Current Agents</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ expectedTotal || '-' }}</span>
              <span class="stat-label">Expected Agents</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ totalTopicsCount }}</span>
              <span class="stat-label">Related Topics</span>
            </div>
          </div>

          <div v-if="profiles.length > 0" class="profiles-preview">
            <div class="preview-header">
              <span class="preview-title">Generated Personas</span>
            </div>
            <div class="profiles-list custom-scrollbar">
              <div 
                v-for="(profile, idx) in profiles" 
                :key="idx" 
                class="profile-card"
                @click="selectProfile(profile)"
              >
                <div class="profile-header">
                  <span class="profile-realname">{{ profile.username || 'Unknown' }}</span>
                  <span class="profile-username">@{{ profile.name || `agent_${idx}` }}</span>
                </div>
                <div class="profile-meta">
                  <span class="profile-profession">{{ profile.profession || 'Unknown Profession' }}</span>
                </div>
                <p class="profile-bio">{{ profile.bio || 'No bio available' }}</p>
                <div v-if="profile.interested_topics?.length" class="profile-topics">
                  <span 
                    v-for="topic in profile.interested_topics.slice(0, 3)" 
                    :key="topic" 
                    class="topic-tag"
                  >{{ topic }}</span>
                  <span v-if="profile.interested_topics.length > 3" class="topic-more">
                    +{{ profile.interested_topics.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="step-card" :class="{ 'active': phase === 2, 'completed': phase > 2 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">03</span>
            <span class="step-title">Generate Dual-Platform Config</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 2" class="badge success">COMPLETED</span>
            <span v-else-if="phase === 2" class="badge processing">GENERATING</span>
            <span v-else class="badge pending">PENDING</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            LLM configures timeflow, algorithms, active hours, and triggers.
          </p>
          
          <div v-if="simulationConfig" class="config-detail-panel">
            <div class="config-block">
              <div class="config-grid">
                <div class="config-item">
                  <span class="config-item-label">Sim Duration</span>
                  <span class="config-item-value">{{ simulationConfig.time_config?.total_simulation_hours || '-' }} Hours</span>
                </div>
                <div class="config-item">
                  <span class="config-item-label">Round Length</span>
                  <span class="config-item-value">{{ simulationConfig.time_config?.minutes_per_round || '-' }} Minutes</span>
                </div>
                <div class="config-item">
                  <span class="config-item-label">Total Rounds</span>
                  <span class="config-item-value">{{ Math.floor((simulationConfig.time_config?.total_simulation_hours * 60 / simulationConfig.time_config?.minutes_per_round)) || '-' }} Rounds</span>
                </div>
                <div class="config-item">
                  <span class="config-item-label">Active / Hr</span>
                  <span class="config-item-value">{{ simulationConfig.time_config?.agents_per_hour_min }}-{{ simulationConfig.time_config?.agents_per_hour_max }}</span>
                </div>
              </div>
              <div class="time-periods">
                <div class="period-item">
                  <span class="period-label">Peak Hours</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.peak_hours?.join(':00, ') }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.peak_activity_multiplier }}</span>
                </div>
                <div class="period-item">
                  <span class="period-label">Work Hours</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.work_hours?.[0] }}:00-{{ simulationConfig.time_config?.work_hours?.slice(-1)[0] }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.work_activity_multiplier }}</span>
                </div>
                <div class="period-item">
                  <span class="period-label">Morning Hours</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.morning_hours?.[0] }}:00-{{ simulationConfig.time_config?.morning_hours?.slice(-1)[0] }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.morning_activity_multiplier }}</span>
                </div>
                <div class="period-item">
                  <span class="period-label">Off-Peak Hours</span>
                  <span class="period-hours">{{ simulationConfig.time_config?.off_peak_hours?.[0] }}:00-{{ simulationConfig.time_config?.off_peak_hours?.slice(-1)[0] }}:00</span>
                  <span class="period-multiplier">×{{ simulationConfig.time_config?.off_peak_activity_multiplier }}</span>
                </div>
              </div>
            </div>

            <div class="config-block">
              <div class="config-block-header">
                <span class="config-block-title">Agent Config</span>
                <span class="config-block-badge">{{ simulationConfig.agent_configs?.length || 0 }} Count</span>
              </div>
              <div class="agents-cards custom-scrollbar">
                <div 
                  v-for="agent in simulationConfig.agent_configs" 
                  :key="agent.agent_id" 
                  class="agent-card"
                >
                  <div class="agent-card-header">
                    <div class="agent-identity">
                      <span class="agent-id">Agent {{ agent.agent_id }}</span>
                      <span class="agent-name">{{ agent.entity_name }}</span>
                    </div>
                    <div class="agent-tags">
                      <span class="agent-type">{{ agent.entity_type }}</span>
                      <span class="agent-stance" :class="'stance-' + agent.stance">{{ agent.stance }}</span>
                    </div>
                  </div>
                  
                  <div class="agent-timeline">
                    <span class="timeline-label">Active Hours</span>
                    <div class="mini-timeline">
                      <div 
                        v-for="hour in 24" 
                        :key="hour - 1" 
                        class="timeline-hour"
                        :class="{ 'active': agent.active_hours?.includes(hour - 1) }"
                        :title="`${hour - 1}:00`"
                      ></div>
                    </div>
                    <div class="timeline-marks">
                      <span>0</span>
                      <span>6</span>
                      <span>12</span>
                      <span>18</span>
                      <span>24</span>
                    </div>
                  </div>

                  <div class="agent-params">
                    <div class="param-group">
                      <div class="param-item">
                        <span class="param-label">Posts / Hr</span>
                        <span class="param-value">{{ agent.posts_per_hour }}</span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">Comments / Hr</span>
                        <span class="param-value">{{ agent.comments_per_hour }}</span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">Response Delay</span>
                        <span class="param-value">{{ agent.response_delay_min }}-{{ agent.response_delay_max }}min</span>
                      </div>
                    </div>
                    <div class="param-group">
                      <div class="param-item">
                        <span class="param-label">Activity Level</span>
                        <span class="param-value with-bar">
                          <span class="mini-bar" :style="{ width: (agent.activity_level * 100) + '%' }"></span>
                          {{ (agent.activity_level * 100).toFixed(0) }}%
                        </span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">Sentiment Bias</span>
                        <span class="param-value" :class="agent.sentiment_bias > 0 ? 'positive' : agent.sentiment_bias < 0 ? 'negative' : 'neutral'">
                          {{ agent.sentiment_bias > 0 ? '+' : '' }}{{ agent.sentiment_bias?.toFixed(1) }}
                        </span>
                      </div>
                      <div class="param-item">
                        <span class="param-label">Influence</span>
                        <span class="param-value highlight">{{ agent.influence_weight?.toFixed(1) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="config-block">
              <div class="config-block-header">
                <span class="config-block-title">Platform Config</span>
              </div>
              <div class="platforms-grid">
                <div v-if="simulationConfig.twitter_config" class="platform-card">
                  <div class="platform-card-header">
                    <span class="platform-name">Info Plaza (Twitter)</span>
                  </div>
                  <div class="platform-params">
                    <div class="param-row">
                      <span class="param-label">Recency Weight</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.recency_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Popularity Weight</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.popularity_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Relevance Weight</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.relevance_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Viral Threshold</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.viral_threshold }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Echo Chamber</span>
                      <span class="param-value">{{ simulationConfig.twitter_config.echo_chamber_strength }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="simulationConfig.reddit_config" class="platform-card">
                  <div class="platform-card-header">
                    <span class="platform-name">Topic Community (Reddit)</span>
                  </div>
                  <div class="platform-params">
                    <div class="param-row">
                      <span class="param-label">Recency Weight</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.recency_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Popularity Weight</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.popularity_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Relevance Weight</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.relevance_weight }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Viral Threshold</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.viral_threshold }}</span>
                    </div>
                    <div class="param-row">
                      <span class="param-label">Echo Chamber</span>
                      <span class="param-value">{{ simulationConfig.reddit_config.echo_chamber_strength }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="simulationConfig.generation_reasoning" class="config-block">
              <div class="config-block-header">
                <span class="config-block-title">LLM Config Reasoning</span>
              </div>
              <div class="reasoning-content">
                <div 
                  v-for="(reason, idx) in simulationConfig.generation_reasoning.split('|').slice(0, 2)" 
                  :key="idx" 
                  class="reasoning-item"
                >
                  <p class="reasoning-text">{{ reason.trim() }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="step-card" :class="{ 'active': phase === 3, 'completed': phase > 3 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">04</span>
            <span class="step-title">Initial Orchestration</span>
          </div>
          <div class="step-status">
            <span v-if="phase > 3" class="badge success">COMPLETED</span>
            <span v-else-if="phase === 3" class="badge processing">ORCHESTRATING</span>
            <span v-else class="badge pending">PENDING</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/prepare</p>
          <p class="description">
            Weaving narrative directions, initial hot topics, and seed posts.
          </p>

          <div v-if="simulationConfig?.event_config" class="orchestration-content">
            <div class="narrative-box">
              <span class="box-label narrative-label">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="special-icon">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="url(#paint0_linear)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M16.24 7.76L14.12 14.12L7.76 16.24L9.88 9.88L16.24 7.76Z" fill="url(#paint0_linear)" stroke="url(#paint0_linear)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <defs>
                    <linearGradient id="paint0_linear" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#3B82F6"/>
                      <stop offset="1" stop-color="#8B5CF6"/>
                    </linearGradient>
                  </defs>
                </svg>
                Narrative Direction
              </span>
              <p class="narrative-text">{{ simulationConfig.event_config.narrative_direction }}</p>
            </div>

            <div class="topics-section">
              <span class="box-label">Initial Hot Topics</span>
              <div class="hot-topics-grid">
                <span v-for="topic in simulationConfig.event_config.hot_topics" :key="topic" class="hot-topic-tag">
                  # {{ topic }}
                </span>
              </div>
            </div>

            <div class="initial-posts-section">
              <span class="box-label">Initial Activation Sequence ({{ simulationConfig.event_config.initial_posts.length }})</span>
              <div class="posts-timeline">
                <div v-for="(post, idx) in simulationConfig.event_config.initial_posts" :key="idx" class="timeline-item">
                  <div class="timeline-marker"></div>
                  <div class="timeline-content">
                    <div class="post-header">
                      <span class="post-role">{{ post.poster_type }}</span>
                      <span class="post-agent-info">
                        <span class="post-id">Agent {{ post.poster_agent_id }}</span>
                        <span class="post-username">@{{ getAgentUsername(post.poster_agent_id) }}</span>
                      </span>
                    </div>
                    <p class="post-text">{{ post.content }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="step-card" :class="{ 'active': phase === 4 }">
        <div class="card-header">
          <div class="step-info">
            <span class="step-num">05</span>
            <span class="step-title">Ready to Start</span>
          </div>
          <div class="step-status">
            <span v-if="phase >= 4" class="badge processing">IN PROGRESS</span>
            <span v-else class="badge pending">PENDING</span>
          </div>
        </div>

        <div class="card-content">
          <p class="api-note">POST /api/simulation/start</p>
          <p class="description">Configuration complete. Click below to launch dual-platform sim.</p>
          
          <div v-if="simulationConfig && autoGeneratedRounds" class="rounds-config-section">
            <div class="rounds-header">
              <div class="header-left">
                <span class="section-title">Simulation Rounds</span>
                <span class="section-desc">Duration: {{ simulationConfig?.time_config?.total_simulation_hours || '-' }} hours, {{ simulationConfig?.time_config?.minutes_per_round || '-' }} min per round</span>
              </div>
              <label class="switch-control">
                <input type="checkbox" v-model="useCustomRounds">
                <span class="switch-track"></span>
                <span class="switch-label">Custom</span>
              </label>
            </div>
            
            <Transition name="fade" mode="out-in">
              <div v-if="useCustomRounds" class="rounds-content custom" key="custom">
                <div class="slider-display">
                  <div class="slider-main-value">
                    <span class="val-num">{{ customMaxRounds }}</span>
                    <span class="val-unit">Rounds</span>
                  </div>
                  <div class="slider-meta-info">
                    <span>Estimated: {{ Math.round(customMaxRounds * 0.6) }} minutes</span>
                  </div>
                </div>

                <div class="range-wrapper">
                  <input 
                    type="range" 
                    v-model.number="customMaxRounds" 
                    min="1" 
                    :max="autoGeneratedRounds"
                    step="1"
                    class="minimal-slider"
                    :style="{ '--percent': ((customMaxRounds - 1) / (autoGeneratedRounds - 1)) * 100 + '%' }"
                  />
                  <div class="range-marks">
                    <span>1</span>
                    <span 
                      class="mark-recommend" 
                      :class="{ active: customMaxRounds === 40 }"
                      @click="customMaxRounds = 40"
                      :style="{ position: 'absolute', left: `calc(${(40 - 1) / (autoGeneratedRounds - 1) * 100}% - 30px)` }"
                    >40 (Recommended)</span>
                    <span>{{ autoGeneratedRounds }}</span>
                  </div>
                </div>
              </div>
              
              <div v-else class="rounds-content auto" key="auto">
                <div class="auto-info-card">
                  <div class="auto-value">
                    <span class="val-num">{{ autoGeneratedRounds }}</span>
                    <span class="val-unit">Rounds</span>
                  </div>
                  <div class="auto-content">
                    <div class="auto-meta-row">
                      <span class="duration-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <circle cx="12" cy="12" r="10"></circle>
                          <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        Estimated: {{ Math.round(autoGeneratedRounds * 0.6) }} minutes
                      </span>
                    </div>
                    <div class="auto-desc">
                      <p class="highlight-tip" @click="useCustomRounds = true">First run? Try a quick 40-round preview ➝</p>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <div class="action-group dual">
            <button 
              class="action-btn secondary"
              @click="$emit('go-back')"
            >
              ← Back to Graph
            </button>
            <button 
              class="action-btn primary"
              :disabled="phase < 4"
              @click="handleStartSimulation"
            >
              Start Dual-Platform Sim ➝
            </button>
          </div>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <div v-if="selectedProfile" class="profile-modal-overlay" @click.self="selectedProfile = null">
        <div class="profile-modal">
          <div class="modal-header">
            <div class="modal-header-info">
              <div class="modal-name-row">
                <span class="modal-realname">{{ selectedProfile.username }}</span>
                <span class="modal-username">@{{ selectedProfile.name }}</span>
              </div>
              <span class="modal-profession">{{ selectedProfile.profession }}</span>
            </div>
            <button class="close-btn" @click="selectedProfile = null">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        
          <div class="modal-body custom-scrollbar">
            <div class="modal-info-grid">
              <div class="info-item">
                <span class="info-label">Age</span>
                <span class="info-value">{{ selectedProfile.age || '-' }} yo</span>
              </div>
              <div class="info-item">
                <span class="info-label">Gender</span>
                <span class="info-value">{{ { male: 'M', female: 'F', other: 'Other' }[selectedProfile.gender?.toLowerCase()] || selectedProfile.gender }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Country</span>
                <span class="info-value">{{ selectedProfile.country || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">MBTI</span>
                <span class="info-value mbti">{{ selectedProfile.mbti || '-' }}</span>
              </div>
            </div>

            <div class="modal-section">
              <span class="section-label">Persona Bio</span>
              <p class="section-bio">{{ selectedProfile.bio || 'No bio available' }}</p>
            </div>

            <div class="modal-section" v-if="selectedProfile.interested_topics?.length">
              <span class="section-label">Seed Related Topics</span>
              <div class="topics-grid">
                <span 
                  v-for="topic in selectedProfile.interested_topics" 
                  :key="topic" 
                  class="topic-item"
                >{{ topic }}</span>
              </div>
            </div>

            <div class="modal-section" v-if="selectedProfile.persona">
              <span class="section-label">Detailed Persona</span>
              
              <div class="persona-dimensions">
                <div class="dimension-card">
                  <span class="dim-title">Event Experience</span>
                  <span class="dim-desc">Key experiences and their behavioral impact</span>
                </div>
                <div class="dimension-card">
                  <span class="dim-title">Behavioral Profile</span>
                  <span class="dim-desc">Typical patterns, communication styles, and biases</span>
                </div>
                <div class="dimension-card">
                  <span class="dim-title">Memory Imprint</span>
                  <span class="dim-desc">Core memories shaping the worldview</span>
                </div>
                <div class="dimension-card">
                  <span class="dim-title">Social Network</span>
                  <span class="dim-desc">Key relationships and influences</span>
                </div>
              </div>

              <div class="persona-content">
                <p class="section-persona">{{ selectedProfile.persona }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <div class="system-logs">
      <div class="log-header">
        <div class="log-title-group">
          <div class="status-dot pulsing"></div>
          <span class="log-title">SYSTEM DASHBOARD</span>
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
import {
  prepareSimulation,
  getPrepareStatus,
  getSimulationProfilesRealtime,
  getSimulationConfigRealtime
} from '../api/simulation'

const props = defineProps({
  simulationId: String,
  simulationData: Object,
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])

// State
const phase = ref(0)
const taskId = ref(null)
const prepareProgress = ref(0)
const currentStage = ref('')
const progressMessage = ref('')
const profiles = ref([])
const entityTypes = ref([])
const expectedTotal = ref(null)
const simulationConfig = ref(null)
const selectedProfile = ref(null)
const showProfilesDetail = ref(true)

let lastLoggedMessage = ''
let lastLoggedProfileCount = 0
let lastLoggedConfigStage = ''

const useCustomRounds = ref(false)
const customMaxRounds = ref(40)

watch(currentStage, (newStage) => {
  if (newStage === '生成Agent人设' || newStage === 'generating_profiles') {
    phase.value = 1
  } else if (newStage === '生成模拟配置' || newStage === 'generating_config') {
    phase.value = 2
    if (!configTimer) {
      addLog('Starting config generation...')
      startConfigPolling()
    }
  } else if (newStage === '准备模拟脚本' || newStage === 'copying_scripts') {
    phase.value = 2
  }
})

const autoGeneratedRounds = computed(() => {
  if (!simulationConfig.value?.time_config) return null
  const totalHours = simulationConfig.value.time_config.total_simulation_hours
  const minutesPerRound = simulationConfig.value.time_config.minutes_per_round
  if (!totalHours || !minutesPerRound) return null
  const calculatedRounds = Math.floor((totalHours * 60) / minutesPerRound)
  return Math.max(calculatedRounds, 40)
})

let pollTimer = null
let profilesTimer = null
let configTimer = null

const displayProfiles = computed(() => {
  if (showProfilesDetail.value) return profiles.value
  return profiles.value.slice(0, 6)
})

const getAgentUsername = (agentId) => {
  if (profiles.value && profiles.value.length > agentId && agentId >= 0) {
    const profile = profiles.value[agentId]
    return profile?.username || `agent_${agentId}`
  }
  return `agent_${agentId}`
}

const totalTopicsCount = computed(() => {
  return profiles.value.reduce((sum, p) => sum + (p.interested_topics?.length || 0), 0)
})

const addLog = (msg) => {
  emit('add-log', msg)
}

const handleStartSimulation = () => {
  const params = {}
  if (useCustomRounds.value) {
    params.maxRounds = customMaxRounds.value
    addLog('Starting simulation with custom rounds: ' + customMaxRounds.value)
  } else {
    addLog('Starting simulation with auto rounds: ' + autoGeneratedRounds.value)
  }
  emit('next-step', params)
}

const selectProfile = (profile) => {
  selectedProfile.value = profile
}

const startPrepareSimulation = async () => {
  if (!props.simulationId) {
    addLog('Error: Missing Simulation ID')
    emit('update-status', 'error')
    return
  }
  
  phase.value = 1
  addLog('Simulation instance created: ' + props.simulationId)
  addLog('Preparing simulation environment...')
  if (props.simulationData?.discover_related_entities) {
    addLog('LLM related-entity discovery is enabled (max 5 extra entities).')
  }
  if (props.simulationData?.custom_entities?.length) {
    addLog(`Custom entities queued: ${props.simulationData.custom_entities.length}`)
  }
  emit('update-status', 'processing')
  
  try {
    const payload = {
      simulation_id: props.simulationId,
      use_llm_for_profiles: true,
      parallel_profile_count: 5
    }
    if (props.simulationData?.discover_related_entities !== undefined) {
      payload.discover_related_entities = props.simulationData.discover_related_entities
    }

    const res = await prepareSimulation(payload)
    
    if (res.success && res.data) {
      if (res.data.already_prepared) {
        addLog('Environment prepared, loading existing data...')
        await loadPreparedData()
        return
      }
      
      taskId.value = res.data.task_id
      addLog('Preparation task started')
      addLog(`  └─ Task ID: ${res.data.task_id}`)
      
      if (res.data.expected_entities_count) {
        expectedTotal.value = res.data.expected_entities_count
        addLog('Found ' + res.data.expected_entities_count + ' entities to generate')
        if (res.data.entity_types && res.data.entity_types.length > 0) {
          addLog(`  └─ Entity Types: ${res.data.entity_types.join(', ')}`)
        }
      }
      
      addLog('Polling for progress...')
      startPolling()
      startProfilesPolling()
    } else {
      addLog('Preparation failed: ' + (res.error || 'Unknown error'))
      emit('update-status', 'error')
    }
  } catch (err) {
    addLog('Preparation exception: ' + err.message)
    emit('update-status', 'error')
  }
}

const startPolling = () => { pollTimer = setInterval(pollPrepareStatus, 2000) }
const stopPolling = () => { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }
const startProfilesPolling = () => { profilesTimer = setInterval(fetchProfilesRealtime, 3000) }
const stopProfilesPolling = () => { if (profilesTimer) { clearInterval(profilesTimer); profilesTimer = null } }

const pollPrepareStatus = async () => {
  if (!taskId.value && !props.simulationId) return
  try {
    const res = await getPrepareStatus({ task_id: taskId.value, simulation_id: props.simulationId })
    if (res.success && res.data) {
      const data = res.data
      prepareProgress.value = data.progress || 0
      progressMessage.value = data.message || ''
      
      if (data.progress_detail) {
        currentStage.value = data.progress_detail.current_stage_name || ''
        const detail = data.progress_detail
        const logKey = `${detail.current_stage}-${detail.current_item}-${detail.total_items}`
        if (logKey !== lastLoggedMessage && detail.item_description) {
          lastLoggedMessage = logKey
          const stageInfo = `[${detail.stage_index}/${detail.total_stages}]`
          if (detail.total_items > 0) {
            addLog(`${stageInfo} ${detail.current_stage_name}: ${detail.current_item}/${detail.total_items} - ${detail.item_description}`)
          } else {
            addLog(`${stageInfo} ${detail.current_stage_name}: ${detail.item_description}`)
          }
        }
      } else if (data.message) {
        const match = data.message.match(/\[(\d+)\/(\d+)\]\s*([^:]+)/)
        if (match) currentStage.value = match[3].trim()
        if (data.message !== lastLoggedMessage) {
          lastLoggedMessage = data.message
          addLog(data.message)
        }
      }
      
      if (data.status === 'completed' || data.status === 'ready' || data.already_prepared) {
        addLog('Environment preparation complete')
        stopPolling()
        stopProfilesPolling()
        await loadPreparedData()
      } else if (data.status === 'failed') {
        addLog(`✗ Preparation failed: ${data.error || 'Unknown error'}`)
        stopPolling()
        stopProfilesPolling()
      }
    }
  } catch (err) {
    console.warn('Poll status failed:', err)
  }
}

const fetchProfilesRealtime = async () => {
  if (!props.simulationId) return
  try {
    const res = await getSimulationProfilesRealtime(props.simulationId, 'reddit')
    if (res.success && res.data) {
      profiles.value = res.data.profiles || []
      if (res.data.total_expected) expectedTotal.value = res.data.total_expected
      
      const types = new Set()
      profiles.value.forEach(p => { if (p.entity_type) types.add(p.entity_type) })
      entityTypes.value = Array.from(types)
      
      const currentCount = profiles.value.length
      if (currentCount > 0 && currentCount !== lastLoggedProfileCount) {
        lastLoggedProfileCount = currentCount
        const total = expectedTotal.value || '?'
        const latestProfile = profiles.value[currentCount - 1]
        const profileName = latestProfile?.name || latestProfile?.username || `Agent_${currentCount}`
        if (currentCount === 1) addLog('Starting Agent Persona generation...')
        addLog(`→ [${currentCount}/${total}] Generated: ${profileName} - ${latestProfile?.profession || 'Unknown Profession'}`)
        
        if (expectedTotal.value && currentCount >= expectedTotal.value) {
          addLog(`All ${currentCount} Agent Personas generated`)
        }
      }
    }
  } catch (err) {
    console.warn('Fetch profiles failed:', err)
  }
}

const startConfigPolling = () => { configTimer = setInterval(fetchConfigRealtime, 2000) }
const stopConfigPolling = () => { if (configTimer) { clearInterval(configTimer); configTimer = null } }

const fetchConfigRealtime = async () => {
  if (!props.simulationId) return
  try {
    const res = await getSimulationConfigRealtime(props.simulationId)
    if (res.success && res.data) {
      const data = res.data
      if (data.generation_stage && data.generation_stage !== lastLoggedConfigStage) {
        lastLoggedConfigStage = data.generation_stage
        if (data.generation_stage === 'generating_profiles') {
          addLog('Generating Agent configs...')
        } else if (data.generation_stage === 'generating_config') {
          addLog('Generating World configs...')
        }
      }
      
      if (data.config_generated && data.config) {
        simulationConfig.value = data.config
        addLog('Simulation configs complete')

        if (data.summary) {
          addLog(`  ├─ Agent Count: ${data.summary.total_agents}`)
          addLog(`  ├─ Simulation Duration: ${data.summary.simulation_hours} Hours`)
          addLog(`  ├─ Initial Posts: ${data.summary.initial_posts_count}`)
          addLog(`  ├─ Hot Topics: ${data.summary.hot_topics_count}`)
          addLog(`  └─ Platform Config: Twitter ${data.summary.has_twitter_config ? '✓' : '✗'}, Reddit ${data.summary.has_reddit_config ? '✓' : '✗'}`)
        }

        if (data.config.time_config) {
          const tc = data.config.time_config
          addLog(`Time Config: ${tc.minutes_per_round} min/round, ${Math.floor((tc.total_simulation_hours * 60) / tc.minutes_per_round)} rounds total`)
        }

        if (data.config.event_config?.narrative_direction) {
          const narrative = data.config.event_config.narrative_direction
          addLog(`Narrative Direction: ${narrative.length > 50 ? narrative.substring(0, 50) + '...' : narrative}`)
        }

        stopConfigPolling()
        phase.value = 4
        addLog('Environment setup complete, ready to launch')
        emit('update-status', 'completed')
      }
    }
  } catch (err) {
    console.warn('Fetch config failed:', err)
  }
}

const loadPreparedData = async () => {
  phase.value = 2
  addLog('Loading simulation configs...')

  await fetchProfilesRealtime()
  addLog(`Loaded ${profiles.value.length} Agent personas`)

  try {
    const res = await getSimulationConfigRealtime(props.simulationId)
    if (res.success && res.data) {
      if (res.data.config_generated && res.data.config) {
        simulationConfig.value = res.data.config
        addLog('Configs loaded successfully')

        if (res.data.summary) {
          addLog(`  ├─ Agent Count: ${res.data.summary.total_agents}`)
          addLog(`  ├─ Simulation Duration: ${res.data.summary.simulation_hours} Hours`)
          addLog(`  └─ Initial Posts: ${res.data.summary.initial_posts_count}`)
        }

        addLog('Environment setup complete, ready to launch')
        phase.value = 4
        emit('update-status', 'completed')
      } else {
        addLog('Configs not ready, polling...')
        startConfigPolling()
      }
    }
  } catch (err) {
    addLog(`Config load failed: ${err.message}`)
    emit('update-status', 'error')
  }
}

const logContent = ref(null)
watch(() => props.systemLogs?.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})

onMounted(() => {
  if (props.simulationId) {
    addLog('Step 2 Initialization')
    startPrepareSimulation()
  }
})

onUnmounted(() => {
  stopPolling()
  stopProfilesPolling()
  stopConfigPolling()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

.workbench-panel {
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
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.02);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.05);
  --shadow-glow: 0 0 0 4px rgba(37, 99, 235, 0.1);
  --terminal-bg: #020617;
  
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  overflow: hidden;
}

.scroll-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* Step Card */
.step-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
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
  line-height: 1;
}

.step-card.active .step-num { color: var(--primary); }
.step-card.completed .step-num { color: #10B981; }

.step-title {
  font-weight: 800;
  font-size: 16px;
  letter-spacing: -0.01em;
  color: var(--text-main);
}

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
.badge.pending { background: #F1F5F9; color: #64748B; }
.badge.accent { background: var(--primary); color: #FFF; }

@keyframes pulse-opacity {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.api-note {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #64748B;
  background: #F8FAFC;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #E2E8F0;
  display: inline-block;
  margin-bottom: 12px;
}

.description {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
}

/* Action Section */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.02em;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);
}

.action-btn.primary { background: #0F172A; color: #FFF; }
.action-btn.primary:hover:not(:disabled) { background: #1E293B; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(15, 23, 42, 0.2); }
.action-btn.secondary { background: #F1F5F9; color: #334155; box-shadow: none; border: 1px solid #E2E8F0; }
.action-btn.secondary:hover:not(:disabled) { background: #E2E8F0; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }

.action-group.dual {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 24px;
}

/* Info Card */
.info-card {
  background: #F8FAFC;
  border-radius: var(--radius-md);
  padding: 20px;
  margin-top: 16px;
  border: 1px solid var(--border-light);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px dashed var(--border-focus);
}
.info-row:last-child { border-bottom: none; padding-bottom: 0; }
.info-row:first-child { padding-top: 0; }

.info-label { font-size: 12px; font-weight: 600; color: #64748B; }
.info-value { font-size: 13px; font-weight: 600; color: #0F172A; }
.info-value.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; }

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #F8FAFC;
  padding: 20px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  text-align: center;
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

/* Profiles Preview */
.profiles-preview { margin-top: 24px; border-top: 1px solid #E2E8F0; padding-top: 24px; }
.preview-header { margin-bottom: 16px; }
.preview-title { font-size: 13px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; }

.profiles-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

/* PROFILE CARD OVERHAUL FOR LONG NAMES */
.profile-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: var(--radius-md);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.profile-card:hover {
  border-color: #94A3B8;
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.profile-header { 
  display: flex; 
  flex-direction: column; /* Stack vertically to prevent overlap */
  align-items: flex-start;
  gap: 4px; 
  margin-bottom: 12px; 
}
.profile-realname { 
  font-size: 15px; 
  font-weight: 700; 
  color: #0F172A; 
  word-break: break-word; /* Ensure long names break safely */
  line-height: 1.3;
}
.profile-username { 
  font-family: 'JetBrains Mono', monospace; 
  font-size: 11px; 
  color: #64748B; 
  word-break: break-all; /* Ensure massive twitter handles break safely */
}

.profile-meta { margin-bottom: 12px; }
.profile-profession { 
  display: inline-block; /* Allows proper wrapping */
  font-size: 11px; 
  font-weight: 600; 
  color: #475569; 
  background: #F1F5F9; 
  padding: 4px 8px; 
  border-radius: 6px; 
  line-height: 1.4;
  word-break: break-word;
}

.profile-bio { font-size: 13px; color: #334155; line-height: 1.6; margin: 0 0 12px 0; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

.profile-topics { display: flex; flex-wrap: wrap; gap: 8px; }
.topic-tag { font-size: 10px; font-weight: 600; color: #1D4ED8; background: #DBEAFE; padding: 4px 8px; border-radius: 6px; }
.topic-more { font-size: 10px; font-weight: 600; color: #64748B; padding: 4px; }

/* Config Preview */
.config-detail-panel { margin-top: 24px; }
.config-block { margin-top: 24px; border-top: 1px solid #E2E8F0; padding-top: 24px; }
.config-block:first-child { margin-top: 0; border-top: none; padding-top: 0; }

.config-block-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.config-block-title { font-size: 13px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; }
.config-block-badge { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; background: #F1F5F9; color: #475569; padding: 4px 10px; border-radius: 6px; }

/* Config Grid */
.config-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.config-item { background: #F8FAFC; padding: 16px; border-radius: var(--radius-sm); border: 1px solid var(--border-light); display: flex; flex-direction: column; gap: 6px; }
.config-item-label { font-size: 10px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
.config-item-value { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; color: #0F172A; }

/* Time Periods */
.time-periods { margin-top: 16px; display: flex; flex-direction: column; gap: 8px; }
.period-item { display: flex; align-items: center; gap: 16px; padding: 12px 16px; background: #F8FAFC; border-radius: var(--radius-sm); border: 1px solid var(--border-light); }
.period-label { font-size: 12px; font-weight: 600; color: #0F172A; min-width: 90px; }
.period-hours { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #475569; flex: 1; }
.period-multiplier { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #4F46E5; background: #E0E7FF; padding: 4px 8px; border-radius: 6px; }

/* Agents Cards */
.agents-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; max-height: 500px; overflow-y: auto; padding-right: 4px; }
.agent-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: var(--radius-md); padding: 20px; transition: all 0.2s ease; box-shadow: var(--shadow-sm); }
.agent-card:hover { border-color: #94A3B8; box-shadow: var(--shadow-md); }

.agent-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #F1F5F9; }
.agent-identity { display: flex; flex-direction: column; gap: 4px; }
.agent-id { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; color: #64748B; }
.agent-name { font-size: 15px; font-weight: 700; color: #0F172A; word-break: break-word; }

.agent-tags { display: flex; gap: 8px; }
.agent-type { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #475569; background: #F1F5F9; padding: 4px 8px; border-radius: 6px; }
.agent-stance { font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 4px 8px; border-radius: 6px; }

.stance-neutral { background: #F1F5F9; color: #475569; }
.stance-supportive { background: #D1FAE5; color: #059669; }
.stance-opposing { background: #FEE2E2; color: #DC2626; }
.stance-observer { background: #FEF3C7; color: #D97706; }

/* Agent Timeline */
.agent-timeline { margin-bottom: 20px; }
.timeline-label { display: block; font-size: 10px; font-weight: 800; color: #64748B; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.mini-timeline { display: flex; gap: 2px; height: 20px; background: #F8FAFC; border-radius: 6px; padding: 4px; border: 1px solid #E2E8F0; }
.timeline-hour { flex: 1; background: #E2E8F0; border-radius: 2px; transition: all 0.2s; }
.timeline-hour.active { background: linear-gradient(180deg, #3B82F6, #60A5FA); }
.timeline-marks { display: flex; justify-content: space-between; margin-top: 6px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; color: #94A3B8; }

/* Agent Params */
.agent-params { display: flex; flex-direction: column; gap: 12px; }
.param-group { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.param-item { display: flex; flex-direction: column; gap: 4px; }
.param-item .param-label { font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; }
.param-item .param-value { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: #0F172A; }

.param-value.with-bar { display: flex; align-items: center; gap: 8px; }
.mini-bar { height: 6px; background: linear-gradient(90deg, #3B82F6, #8B5CF6); border-radius: 3px; min-width: 6px; max-width: 40px; }
.param-value.positive { color: #10B981; }
.param-value.negative { color: #EF4444; }
.param-value.neutral { color: #64748B; }
.param-value.highlight { color: #3B82F6; }

/* Platforms Grid */
.platforms-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.platform-card { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 20px; border-radius: var(--radius-md); box-shadow: var(--shadow-sm); }
.platform-card-header { margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #F1F5F9; }
.platform-name { font-size: 14px; font-weight: 700; color: #0F172A; }
.platform-params { display: flex; flex-direction: column; gap: 12px; }
.param-row { display: flex; justify-content: space-between; align-items: center; }

/* Reasoning Content */
.reasoning-content { display: flex; flex-direction: column; gap: 12px; }
.reasoning-item { padding: 16px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: var(--radius-sm); }
.reasoning-text { font-size: 13px; color: #334155; line-height: 1.6; margin: 0; }

/* Profile Modal (Glassmorphism + Long Name Support) */
.profile-modal-overlay {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 1000;
}

.profile-modal {
  background: #FFFFFF; border-radius: 24px; width: 90%; max-width: 600px;
  max-height: 85vh; overflow: hidden; display: flex; flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; padding: 24px 32px; background: #F8FAFC; border-bottom: 1px solid #F1F5F9; }
.modal-header-info { flex: 1; padding-right: 16px; }
.modal-name-row { 
  display: flex; 
  flex-direction: column; /* Stacked for extremely long names */
  align-items: flex-start; 
  gap: 6px; 
  margin-bottom: 12px; 
}
.modal-realname { 
  font-size: 22px; 
  font-weight: 800; 
  color: #0F172A; 
  word-break: break-word; 
  line-height: 1.2;
}
.modal-username { 
  font-family: 'JetBrains Mono', monospace; 
  font-size: 13px; 
  font-weight: 600; 
  color: #64748B; 
  word-break: break-all;
}
.modal-profession { 
  font-size: 12px; 
  font-weight: 700; 
  color: #475569; 
  background: #E2E8F0; 
  padding: 6px 12px; 
  border-radius: 6px; 
  display: inline-block; 
  max-width: 100%; /* Prevent overflow */
  word-break: break-word;
  white-space: normal;
  line-height: 1.4;
}

.close-btn {
  width: 32px; height: 32px; border: 1px solid #E2E8F0; background: #FFF; color: #64748B;
  border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; box-shadow: var(--shadow-sm); flex-shrink: 0;
}
.close-btn:hover { background: #F1F5F9; color: #0F172A; }

.modal-body { padding: 32px; overflow-y: auto; flex: 1; }

.modal-info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-bottom: 32px; }
.modal-section { margin-bottom: 32px; }
.section-label { display: block; font-size: 11px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
.section-bio { font-size: 14px; color: #334155; line-height: 1.6; margin: 0; padding: 20px; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0; }

.topics-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.topic-item { font-size: 12px; font-weight: 600; color: #1D4ED8; background: #DBEAFE; padding: 6px 12px; border-radius: 8px; }

.persona-dimensions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px; }
.dimension-card { background: #F8FAFC; padding: 16px; border-radius: 12px; border: 1px solid #E2E8F0; border-left: 4px solid #3B82F6; transition: all 0.2s; }
.dimension-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.dim-title { display: block; font-size: 12px; font-weight: 800; color: #0F172A; margin-bottom: 6px; }
.dim-desc { display: block; font-size: 11px; font-weight: 500; color: #64748B; line-height: 1.5; }

.persona-content { padding: 0; background: transparent; border: none; }
.section-persona { font-size: 14px; color: #334155; line-height: 1.8; margin: 0; text-align: justify; }

/* Orchestration Content */
.orchestration-content { display: flex; flex-direction: column; gap: 24px; margin-top: 24px; }
.box-label { display: block; font-size: 12px; font-weight: 800; color: #0F172A; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px; }

.narrative-box { background: #FFFFFF; padding: 24px; border-radius: var(--radius-md); border: 1px solid #E2E8F0; box-shadow: var(--shadow-sm); }
.narrative-box .box-label { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.special-icon { color: #3B82F6; }
.narrative-text { font-size: 14px; color: #334155; line-height: 1.8; margin: 0; }

.topics-section { background: transparent; }
.hot-topics-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.hot-topic-tag { font-size: 13px; font-weight: 700; color: #C2410C; background: #FFEDD5; padding: 6px 14px; border-radius: 8px; }

.initial-posts-section { border-top: 1px solid #E2E8F0; padding-top: 24px; }
.posts-timeline { display: flex; flex-direction: column; gap: 20px; padding-left: 12px; border-left: 2px solid #E2E8F0; margin-top: 16px; }
.timeline-item { position: relative; padding-left: 24px; }
.timeline-marker { position: absolute; left: -1px; top: 16px; width: 16px; height: 2px; background: #CBD5E1; }
.timeline-content { background: #F8FAFC; padding: 16px; border-radius: var(--radius-sm); border: 1px solid #E2E8F0; }
.post-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.post-role { font-size: 10px; font-weight: 800; color: #FFFFFF; background: #0F172A; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
.post-agent-info { display: flex; align-items: center; gap: 8px; }
.post-id { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; color: #64748B; }
.post-username { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #3B82F6; word-break: break-all; }
.post-text { font-size: 13px; color: #334155; line-height: 1.6; margin: 0; }

/* Simulation rounds config styles */
.rounds-config-section { margin: 32px 0; padding-top: 32px; border-top: 1px solid #E2E8F0; }
.rounds-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header-left { display: flex; flex-direction: column; gap: 6px; }
.section-title { font-size: 15px; font-weight: 800; color: #0F172A; }
.section-desc { font-size: 13px; color: #64748B; }

.switch-control { display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 6px; border-radius: 20px; transition: background 0.2s; }
.switch-control:hover { background: #F8FAFC; }
.switch-control input { display: none; }
.switch-track { width: 44px; height: 24px; background: #E2E8F0; border-radius: 12px; position: relative; transition: all 0.3s; }
.switch-track::after { content: ''; position: absolute; left: 2px; top: 2px; width: 20px; height: 20px; background: #FFF; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s; }
.switch-control input:checked + .switch-track { background: #0F172A; }
.switch-control input:checked + .switch-track::after { transform: translateX(20px); }
.switch-label { font-size: 13px; font-weight: 600; color: #475569; }
.switch-control input:checked ~ .switch-label { color: #0F172A; }

.slider-display { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }
.slider-main-value { display: flex; align-items: baseline; gap: 8px; }
.val-num { font-family: 'JetBrains Mono', monospace; font-size: 32px; font-weight: 800; color: #0F172A; line-height: 1; }
.val-unit { font-size: 13px; font-weight: 600; color: #64748B; }
.slider-meta-info { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: #3B82F6; background: #EFF6FF; padding: 6px 12px; border-radius: 6px; }

.range-wrapper { position: relative; padding: 0 4px; }
.minimal-slider { -webkit-appearance: none; width: 100%; height: 6px; background: #E2E8F0; border-radius: 3px; outline: none; background-image: linear-gradient(#3B82F6, #3B82F6); background-size: var(--percent, 0%) 100%; background-repeat: no-repeat; cursor: pointer; }
.minimal-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #FFF; border: 3px solid #3B82F6; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.15); transition: transform 0.1s; margin-top: -7px; }
.minimal-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.minimal-slider::-webkit-slider-runnable-track { height: 6px; border-radius: 3px; }

.range-marks { display: flex; justify-content: space-between; margin-top: 12px; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; color: #94A3B8; position: relative; }
.mark-recommend { cursor: pointer; transition: color 0.2s; position: relative; }
.mark-recommend:hover, .mark-recommend.active { color: #0F172A; font-weight: 700; }
.mark-recommend::after { content: ''; position: absolute; top: -14px; left: 50%; transform: translateX(-50%); width: 2px; height: 6px; background: #94A3B8; }

.auto-info-card { display: flex; align-items: center; gap: 32px; background: #F8FAFC; padding: 20px 24px; border-radius: 12px; border: 1px solid #E2E8F0; }
.auto-value { display: flex; align-items: baseline; gap: 8px; padding-right: 32px; border-right: 1px solid #E2E8F0; }
.auto-content { flex: 1; display: flex; flex-direction: column; gap: 12px; justify-content: center; }
.duration-badge { display: inline-flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: #3B82F6; background: #EFF6FF; border: 1px solid #BFDBFE; padding: 6px 12px; border-radius: 8px; }
.auto-desc p { margin: 0; font-size: 14px; color: #64748B; }
.highlight-tip { margin-top: 4px !important; font-size: 13px !important; color: #0F172A !important; font-weight: 600; cursor: pointer; transition: color 0.2s; }
.highlight-tip:hover { color: #3B82F6 !important; }

/* ----------------------------------------------------
   SOLID DARK TERMINAL
   Forced overrides to prevent transparency
------------------------------------------------------- */
.system-logs {
  background-color: #0F172A !important; /* Force solid dark slate */
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
.status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; }
.status-dot.pulsing { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); animation: pulse-green 2s infinite; }
@keyframes pulse-green { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }

.log-title { color: #38BDF8; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
.log-id { color: #475569; font-weight: 600; }
.log-content { display: flex; flex-direction: column; gap: 6px; height: 120px; overflow-y: auto; padding-right: 8px; scroll-behavior: smooth; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .profile-modal { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-leave-active .profile-modal { transition: all 0.3s ease-in; }
.modal-enter-from .profile-modal, .modal-leave-to .profile-modal { transform: scale(0.95) translateY(10px); opacity: 0; }
</style>