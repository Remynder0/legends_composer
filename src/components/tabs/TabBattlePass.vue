<script setup lang="ts">
import { ref, computed } from 'vue'
import { generateSeasons, getParsedSeasonData } from '../../logic/packCalculator'
import type { SeasonData } from '../../logic/packCalculator'

const seasons = ref<SeasonData[]>(generateSeasons().reverse())
const selectedSeasonId = ref<string>(seasons.value[0]?.id || '')

const selectedSeasonData = computed(() => {
    if (!selectedSeasonId.value) return null
    return getParsedSeasonData(selectedSeasonId.value)
})

const selectedSeasonMeta = computed(() => {
    return seasons.value.find(s => s.id === selectedSeasonId.value)
})

const levels = computed(() => {
    const data = selectedSeasonData.value
    if (!data || !data.rewards) return []
    
    const maxLevel = selectedSeasonMeta.value?.maxLevel || 110
    const result = []
    
    for (let i = 1; i <= maxLevel; i++) {
        const levelData = data.rewards[`level_${i}`]
        if (levelData) {
            result.push({
                level: i,
                free: levelData.free || [],
                premium: levelData.premium || []
            })
        } else {
            result.push({
                level: i,
                free: [],
                premium: []
            })
        }
    }
    return result
})
</script>

<template>
  <div class="h-full flex flex-col space-y-6">
    <div class="flex justify-between items-end border-b border-titan-border pb-4">
      <div>
        <h2 class="text-2xl font-black text-white font-mono uppercase tracking-widest">Consultation Battle Pass</h2>
        <p class="text-gray-400 text-sm mt-1">Archive des récompenses de saisons</p>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex gap-4 items-center bg-black/40 p-4 border border-titan-border">
      <label class="text-sm font-bold text-titan-cyan uppercase tracking-wider">Sélectionner une Saison</label>
      <select 
        v-model="selectedSeasonId" 
        class="bg-titan-panel border border-titan-border text-white px-4 py-2 font-mono outline-none focus:border-titan-cyan transition-colors min-w-[200px]"
      >
        <option v-for="season in seasons" :key="season.id" :value="season.id">
          {{ season.name }}
        </option>
      </select>
    </div>

    <!-- Rewards List -->
    <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar">
      <div v-if="levels.length === 0" class="text-center py-12 text-gray-500 font-mono italic">
        Données introuvables pour cette saison.
      </div>
      <div v-else class="grid grid-cols-1 gap-2 pb-8">
        <!-- Header -->
        <div class="grid grid-cols-12 gap-4 px-4 py-2 bg-titan-cyan/10 border-y border-titan-cyan/30 text-xs font-bold text-titan-cyan uppercase tracking-wider sticky top-0 z-10 backdrop-blur-sm">
          <div class="col-span-2 text-center">Niveau</div>
          <div class="col-span-5">Premium</div>
          <div class="col-span-5">Gratuit</div>
        </div>
        
        <!-- Rows -->
        <template v-for="item in levels" :key="item.level">
          <div 
            v-if="item.level < 101 || item.level > 109"
            class="grid grid-cols-12 gap-4 px-4 py-3 bg-black/20 border border-titan-border/50 hover:border-titan-cyan/50 hover:bg-black/40 transition-colors items-center group"
          >
            <div class="col-span-2 flex justify-center">
              <div class="w-10 h-10 bg-titan-panel border border-titan-border flex items-center justify-center font-black font-mono text-lg text-white group-hover:text-titan-cyan group-hover:border-titan-cyan transition-colors">
                {{ item.level }}
              </div>
            </div>
            
            <div class="col-span-5 flex flex-col gap-1">
              <span v-if="item.premium.length === 0" class="text-gray-600 italic text-sm">-</span>
              <span 
                v-else 
                v-for="(r, idx) in item.premium" 
                :key="idx"
                class="text-sm font-medium"
                :class="r.includes('Apex Pack') ? 'text-yellow-400' : 'text-gray-200'"
              >
                {{ r }}
              </span>
            </div>
            
            <div class="col-span-5 flex flex-col gap-1 border-l border-titan-border/50 pl-4">
              <span v-if="item.free.length === 0" class="text-gray-600 italic text-sm">-</span>
              <span 
                v-else 
                v-for="(r, idx) in item.free" 
                :key="idx"
                class="text-sm font-medium"
                :class="r.includes('Apex Pack') ? 'text-yellow-400' : 'text-gray-300'"
              >
                {{ r }}
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #00e5ff;
  opacity: 0.5;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #00b3cc;
}
</style>
