<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { loadGameData, isLoaded } from './logic/store'

import TabTeamGen from './components/tabs/TabTeamGen.vue'
import TabPackCalculator from './components/tabs/TabPackCalculator.vue'
import TabProbabilities from './components/tabs/TabProbabilities.vue'
import TabSimulation from './components/tabs/TabSimulation.vue'
import TabStats from './components/tabs/TabStats.vue'
import TabSort from './components/tabs/TabSort.vue'

const currentTab = ref('TeamGen')

const tabs = [
  { id: 'TeamGen', name: 'Liaison & Déploie.', component: TabTeamGen },
  { id: 'PackCalculator', name: 'Heirloom Tracker', component: TabPackCalculator },
  { id: 'Probabilities', name: 'Analyse Prédic.', component: TabProbabilities },
  { id: 'Simulation', name: 'Simulation', component: TabSimulation },
  { id: 'Stats', name: 'Data Logs', component: TabStats },
  { id: 'Sort', name: 'Tri Tactique', component: TabSort },
]

onMounted(async () => {
  await loadGameData()
})
</script>

<template>
  <div class="flex h-screen bg-apex-darker overflow-hidden text-gray-200 font-sans">
    
    <!-- Sidebar -->
    <aside class="w-64 flex-shrink-0 bg-titan-panel border-r border-titan-border flex flex-col relative z-20 shadow-2xl">
      <div class="p-6 border-b border-titan-border">
        <h1 class="text-3xl font-black text-white font-mono uppercase tracking-tighter leading-none">
          LEGENDS<br/><span class="text-titan-orange">COMPOSER</span>
        </h1>
        <div class="text-titan-cyan text-[10px] font-mono mt-2 tracking-widest uppercase">OS.Titan_Link // v2.0</div>
      </div>

      <nav class="flex-1 overflow-y-auto py-6 space-y-3 px-4">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="currentTab = tab.id"
          class="w-full text-left px-4 py-3 font-mono text-sm uppercase tracking-wider transition-all relative group titan-beveled"
          :class="currentTab === tab.id ? 'bg-titan-cyan text-black font-bold' : 'text-gray-400 bg-black/30 border border-titan-border hover:border-titan-cyan hover:text-white'"
        >
          <span v-if="currentTab === tab.id" class="absolute left-2 top-1/2 transform -translate-y-1/2 w-1.5 h-1.5 bg-black"></span>
          <span :class="currentTab === tab.id ? 'pl-3' : ''" class="transition-all">{{ tab.name }}</span>
        </button>
      </nav>

      <div class="p-4 border-t border-titan-border text-xs font-mono text-gray-600 text-center">
        SYSTEM ONLINE
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 relative z-10 flex flex-col h-full bg-black/20">
      <div v-if="!isLoaded" class="flex-1 flex items-center justify-center">
        <div class="text-titan-cyan font-mono text-xl animate-pulse flex items-center gap-4 border border-titan-cyan p-6 bg-titan-cyan/5">
            <span class="w-4 h-4 bg-titan-orange block"></span>
            ÉTABLISSEMENT DE LA CONNEXION...
        </div>
      </div>
      
      <div v-else class="flex-1 p-8 overflow-hidden h-full">
        <KeepAlive>
            <component :is="tabs.find(t => t.id === currentTab)?.component" />
        </KeepAlive>
      </div>
    </main>

  </div>
</template>
