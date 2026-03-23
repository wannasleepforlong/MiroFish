<template>
  <div class="trends-heatmap-container">
    <div class="heatmap-header">
      <div class="header-left">
        <h3 class="title">{{ $t('trends.title') }}</h3>
        <div class="mode-switch">
          <button 
            v-for="m in ['actions', 'agents']" 
            :key="m"
            class="mode-btn"
            :class="{ active: mode === m }"
            @click="mode = m"
          >
            {{ $t(`trends.${m}`).toUpperCase() }}
          </button>
        </div>
      </div>
      <div class="header-right">
        <div class="legend" v-if="processedData.length > 0">
          <span class="legend-label">{{ $t('trends.intensity') }}:</span>
          <div class="legend-cells">
            <div class="legend-cell level-0"></div>
            <div class="legend-cell level-1"></div>
            <div class="legend-cell level-2"></div>
            <div class="legend-cell level-3"></div>
            <div class="legend-cell level-4"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Heatmap Grid -->
    <div class="heatmap-body" v-if="processedData.length > 0">
      <div class="y-axis">
        <div v-for="row in processedData" :key="row.id" class="y-label">
          {{ row.name }}
        </div>
      </div>
      
      <div class="grid-wrapper scrollbar-thin overflow-x-auto" ref="gridWrapper">
        <div class="grid-container" :style="gridStyle">
          <!-- Column Labels (Rounds) -->
          <div class="grid-col-labels" :style="gridStyle">
            <div v-for="c in maxRoundsDisplay" :key="c" class="x-label">
              R{{ c }}
            </div>
          </div>

          <!-- Grid Cells -->
          <div v-for="(row, idx) in processedData" :key="row.id" class="grid-row" :style="gridStyle">
            <div 
              v-for="round_num in maxRoundsDisplay" 
              :key="round_num" 
              class="grid-cell"
              :class="getCellClass(row.activity[round_num])"
              @mouseover="hoverCell = { row: row.name, round: round_num, count: row.activity[round_num] || 0 }"
              @mouseleave="hoverCell = null"
            >
              <div class="cell-tooltip" v-if="hoverCell && hoverCell.row === row.name && hoverCell.round === round_num">
                <div class="tooltip-val">{{ hoverCell.count }} {{ $t('trends.acts') }}</div>
                <div class="tooltip-meta">{{ $t('trends.round_label') }} {{ round_num }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="loader-pulse" v-if="loading"></div>
      <p v-else>{{ $t('trends.noData') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  actions: {
    type: Array, // Array of AgentAction objects
    default: () => []
  },
  rounds: {
    type: Number,
    default: 1
  },
  loading: Boolean
})

const mode = ref('actions') // 'actions' | 'agents'
const hoverCell = ref(null)
const gridWrapper = ref(null)

const normalizedActions = computed(() => {
  return (props.actions || []).filter(action => {
    return action && typeof action.round_num === 'number' && action.round_num > 0
  })
})

const maxRoundsDisplay = computed(() => {
  return props.rounds || 1
})

const processedData = computed(() => {
  const totalRounds = maxRoundsDisplay.value
  
  if (normalizedActions.value.length === 0) {
    if (mode.value === 'actions') {
      return ['POST', 'REPOST', 'LIKE', 'COMMENT', 'FOLLOW'].map(name => ({
        id: name,
        name,
        activity: {}
      }))
    }
    return []
  }
  
  if (mode.value === 'actions') {
    // Action Types as rows
    const actionTypes = [
      'CREATE_POST', 'QUOTE_POST', 'REPOST', 'LIKE_POST', 
      'CREATE_COMMENT', 'LIKE_COMMENT', 'SEARCH_POSTS', 'FOLLOW',
      'UPVOTE_POST', 'DOWNVOTE_POST', 'DO_NOTHING'
    ]
    
    return actionTypes.map(type => {
      const activity = {}
      for (let r = 1; r <= totalRounds; r++) {
        activity[r] = normalizedActions.value.filter(a => a.action_type === type && a.round_num === r).length
      }
      return {
        id: type,
        name: simplifyActionName(type),
        activity
      }
    }).filter(row => Object.values(row.activity).some(v => v > 0)) // Only show types that occurred
  } else {
    // Agents as rows (Top 15 most active)
    const agentActivity = {}
    normalizedActions.value.forEach(a => {
      if (!agentActivity[a.agent_id]) {
        agentActivity[a.agent_id] = { id: a.agent_id, name: a.agent_name || `Agent ${a.agent_id}`, total: 0, activity: {} }
      }
      agentActivity[a.agent_id].total++
      agentActivity[a.agent_id].activity[a.round_num] = (agentActivity[a.agent_id].activity[a.round_num] || 0) + 1
    })

    const topAgents = Object.values(agentActivity)
      .sort((a, b) => b.total - a.total)
      .slice(0, 15)
    
    return topAgents.map(ag => {
      const activity = {}
      for (let r = 1; r <= totalRounds; r++) {
        activity[r] = ag.activity[r] || 0
      }
      return {
        id: ag.id,
        name: ag.name,
        activity
      }
    })
  }
})

const gridStyle = computed(() => {
  return {
    gridTemplateColumns: `repeat(${maxRoundsDisplay.value}, 30px)`
  }
})

const simplifyActionName = (type) => {
  const map = {
    'CREATE_POST': t('trends.post'),
    'QUOTE_POST': t('trends.quote'),
    'REPOST': t('trends.repost'),
    'LIKE_POST': t('trends.like'),
    'CREATE_COMMENT': t('trends.comment'),
    'LIKE_COMMENT': t('trends.like'),
    'SEARCH_POSTS': t('trends.search'),
    'FOLLOW': t('trends.follow'),
    'UPVOTE_POST': t('trends.upvote'),
    'DOWNVOTE_POST': t('trends.downvote'),
    'DO_NOTHING': 'IDLE'
  }
  return map[type] || type
}

const getCellClass = (count) => {
  if (!count || count === 0) return 'level-0'
  if (count < 3) return 'level-1'
  if (count < 6) return 'level-2'
  if (count < 10) return 'level-3'
  return 'level-4'
}

// Auto-scroll to current round
watch(maxRoundsDisplay, (newVal) => {
  if (newVal > 0) {
    nextTick(() => {
      if (gridWrapper.value) {
        gridWrapper.value.scrollLeft = gridWrapper.value.scrollWidth
      }
    })
  }
}, { immediate: true })

</script>

<style scoped>
.trends-heatmap-container {
  background: #FFF;
  border: 1px solid #EAEAEA;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 24px;
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 800;
  color: #999;
  letter-spacing: 0.1em;
  margin: 0;
}

.mode-switch {
  display: flex;
  background: #F5F5F5;
  padding: 2px;
  border-radius: 4px;
  margin-top: 6px;
}

.mode-btn {
  border: none;
  background: transparent;
  padding: 4px 12px;
  font-size: 10px;
  font-weight: 800;
  color: #666;
  border-radius: 3px;
  cursor: pointer;
  font-family: 'JetBrains Mono', monospace;
}

.mode-btn.active {
  background: #FFF;
  color: #000;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.legend {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-label {
  font-size: 10px;
  color: #999;
  font-weight: 600;
}

.legend-cells {
  display: flex;
  gap: 2px;
}

.legend-cell {
  width: 12px;
  height: 12px;
  border-radius: 1px;
}

.heatmap-body {
  display: flex;
  position: relative;
}

.y-axis {
  flex-shrink: 0;
  width: 100px;
  display: flex;
  flex-direction: column;
  padding-top: 24px; /* Align with cells */
}

.y-label {
  height: 24px;
  display: flex;
  align-items: center;
  font-size: 10px;
  font-weight: 600;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 8px;
  font-family: 'JetBrains Mono', monospace;
}

.grid-wrapper {
  flex: 1;
  cursor: grab;
}

.grid-container {
  display: grid;
  gap: 2px;
}

.grid-col-labels {
  display: grid;
  height: 24px;
}

.x-label {
  font-size: 9px;
  font-weight: 700;
  color: #999;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
}

.grid-row {
  display: grid;
  height: 24px;
}

.grid-cell {
  width: 30px;
  height: 22px;
  border-radius: 2px;
  position: relative;
  transition: transform 0.1s;
}

.grid-cell:hover {
  transform: scale(1.1);
  z-index: 10;
  box-shadow: 0 0 8px rgba(0,0,0,0.2);
}

/* Intensity levels - B&W/Monochrome palette matching Project Style */
.level-0 { background: #F5F5F5; }
.level-1 { background: #D0D0D0; }
.level-2 { background: #888888; }
.level-3 { background: #333333; }
.level-4 { background: #000000; }

.cell-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: #FFF;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  pointer-events: none;
  margin-bottom: 6px;
  z-index: 100;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.tooltip-val {
  font-weight: 800;
}

.tooltip-meta {
  color: #AAA;
  font-size: 9px;
}

/* Loader / Empty States */
.empty-state {
  height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
}

.loader-pulse {
  width: 40px;
  height: 4px;
  background: #EEE;
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}

.loader-pulse::after {
  content: '';
  position: absolute;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, #000, transparent);
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { left: -100%; }
  100% { left: 100%; }
}

.scrollbar-thin::-webkit-scrollbar {
  height: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: #F5F5F5;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #CCC;
}
</style>
