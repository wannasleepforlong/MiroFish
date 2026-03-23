<template>
  <div class="live-news-ticker" v-if="news.length > 0">
    <div class="ticker-header">
      <span class="live-dot"></span>
      <span class="ticker-label">LIVE WAR NEWS</span>
    </div>
    <div class="ticker-content-wrapper">
      <div class="ticker-content" :style="{ animationDuration: animationDuration }">
        <div v-for="(item, index) in displayNews" :key="index" class="ticker-item">
          <span class="item-source">[{{ item.source }}]</span>
          <span class="item-title">{{ item.title }}</span>
          <span class="item-divider">/</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { globalState } from '../store/globalSettings'

const news = ref([])
const displayNews = computed(() => [...news.value, ...news.value]) // Duplicate for infinite scroll
const animationDuration = computed(() => `${news.value.length * 5}s`)

const fetchNews = async () => {
  const countries = globalState.selectedCountries
  if (countries.length === 0) return
  
  try {
    const res = await fetch(`/api/news/live?countries=${countries.join(',')}`)
    const data = await res.json()
    if (data.success) {
      news.value = data.data
    }
  } catch (e) {
    console.error('Failed to fetch ticker news:', e)
  }
}

let timer = null

onMounted(() => {
  fetchNews()
  timer = setInterval(fetchNews, 60000) // Update every minute
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

watch(() => globalState.selectedCountries, () => {
  fetchNews()
}, { deep: true })
</script>

<style scoped>
.live-news-ticker {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 400px;
  height: 40px;
  background: black;
  color: white;
  display: flex;
  align-items: center;
  z-index: 1000;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-family: 'JetBrains Mono', monospace;
  overflow: hidden;
}

.ticker-header {
  background: var(--orange, #ff5722);
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 10px;
  gap: 8px;
  font-size: 0.7rem;
  font-weight: 800;
  white-space: nowrap;
  flex-shrink: 0;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.ticker-content-wrapper {
  overflow: hidden;
  flex: 1;
}

.ticker-content {
  display: flex;
  white-space: nowrap;
  animation: scroll linear infinite;
}

@keyframes scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.ticker-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 15px;
  font-size: 0.75rem;
}

.item-source {
  color: var(--orange, #ff5722);
  font-weight: 700;
}

.item-divider {
  color: #555;
  margin-left: 10px;
}
</style>
