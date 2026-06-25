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
  <div class="glass p-6 flex flex-col justify-between transition-transform transform hover:-translate-y-1 hover:shadow-2xl hover:border-apex-red/50">
    <div>
      <div class="flex justify-between items-start mb-4">
        <div>
          <h2 class="text-xs uppercase tracking-widest text-apex-red font-bold mb-1">{{ role }}</h2>
          <h3 class="text-2xl font-black text-white">{{ legend.Name }}</h3>
        </div>
        <span class="px-3 py-1 bg-white/10 rounded-full text-xs font-semibold backdrop-blur-sm border border-white/5">
          {{ legend.Class }}
        </span>
      </div>

      <div class="space-y-2 mt-4">
        <div v-for="[statName, val] in topStats" :key="statName" class="flex items-center">
          <div class="w-24 text-xs text-gray-400 capitalize">{{ statName.replace('_', ' ') }}</div>
          <div class="flex-1 bg-black/40 h-2 rounded-full overflow-hidden border border-white/5">
            <div class="bg-gradient-to-r from-apex-red to-orange-500 h-full rounded-full" :style="{ width: `${val * 10}%` }"></div>
          </div>
          <div class="w-8 text-right text-xs font-bold text-white">{{ val }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
