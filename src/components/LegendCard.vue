<script setup lang="ts">
import { computed } from 'vue'
import type { Legend } from '../logic/composer'

const props = defineProps<{
  legend: Legend
  role: string
}>()

const topStats = computed(() => {
  return Object.entries(props.legend.stats)
    .filter(([_, val]) => val > 0)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5) // Show top 5 stats
})
</script>

<template>
  <div class="glass-panel p-6 flex flex-col justify-between transition-transform transform hover:-translate-y-1 hover:border-titan-cyan group">
    <div class="absolute top-0 left-0 w-1 h-full bg-titan-border group-hover:bg-titan-cyan transition-colors"></div>
    <div class="pl-2">
      <div class="flex justify-between items-start mb-4">
        <div>
          <h2 class="text-[10px] uppercase tracking-widest text-titan-orange font-mono font-bold mb-1">{{ role }}</h2>
          <h3 class="text-2xl font-black text-white font-sans uppercase tracking-wider">{{ legend.Name }}</h3>
        </div>
        <span class="px-2 py-1 bg-black/50 text-[10px] font-mono text-titan-cyan uppercase border border-titan-border">
          {{ legend.Class }}
        </span>
      </div>

      <div class="space-y-2 mt-6">
        <div v-for="[statName, val] in topStats" :key="statName" class="flex items-center">
          <div class="w-24 text-[10px] text-gray-400 capitalize font-mono">{{ statName.replace('_', ' ') }}</div>
          <div class="flex-1 bg-black/60 h-1 overflow-hidden border border-titan-border/50">
            <div class="bg-titan-cyan h-full transition-all" :style="{ width: `${val * 10}%` }"></div>
          </div>
          <div class="w-6 text-right text-[10px] font-bold text-white font-mono">{{ val }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
