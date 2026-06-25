<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { buildTeam, getTeamArchetype, checkSpecialSynergies, evaluateTeam, calculatePickProbabilities, type Legend, type AntiSynergy, type SpecialSynergy, type ProbResult } from './logic/composer'
import LegendCard from './components/LegendCard.vue'

const legends = ref<Legend[]>([])
const specialSynergies = ref<SpecialSynergy[]>([])
const antiSynergies = ref<AntiSynergy[]>([])

const currentTeam = ref<Legend[]>([])
const currentArchetype = ref<string>('')
const currentSpecialSynergies = ref<SpecialSynergy[]>([])
const currentScore = ref<number>(0)
const loading = ref(true)

const teamSize = ref<number>(3)

const probTarget = ref<string>('')
const probResults = ref<ProbResult[]>([])

async function loadData() {
  try {
    const response = await fetch('/Legends.json')
    const data = await response.json()
    legends.value = data.Legends
    specialSynergies.value = data.SPECIAL_SYNERGIES || []
    antiSynergies.value = data.ANTI_SYNERGIES || []
    loading.value = false
    generateTeam()
  } catch (e) {
    console.error("Failed to load data", e)
  }
}

function generateTeam() {
  if (legends.value.length === 0) return
  
  currentTeam.value = buildTeam(legends.value, antiSynergies.value, teamSize.value)
  
  const evalResult = evaluateTeam(currentTeam.value)
  currentScore.value = evalResult.totalSynergyScore
  currentArchetype.value = getTeamArchetype(evalResult.teamStats)
  currentSpecialSynergies.value = checkSpecialSynergies(currentTeam.value, specialSynergies.value)
}

function updateProbs() {
  if (!probTarget.value) {
    probResults.value = []
    return
  }
  probResults.value = calculatePickProbabilities(probTarget.value, legends.value, antiSynergies.value)
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="max-w-6xl mx-auto p-8 relative z-10">
    <header class="text-center mb-10">
      <h1 class="text-5xl font-black tracking-tighter mb-2 bg-gradient-to-r from-apex-red to-orange-500 bg-clip-text text-transparent">LEGENDS COMPOSER</h1>
      <p class="text-gray-400 font-medium">Générateur d'Équipe Synergique</p>
    </header>

    <div v-if="loading" class="text-center py-20 text-xl font-bold animate-pulse">
      Initialisation de l'arène...
    </div>

    <div v-else>
      <div class="flex flex-col md:flex-row justify-center items-center gap-6 mb-10">
        
        <div class="glass px-6 py-4 flex items-center gap-4">
          <span class="text-gray-300 font-bold text-sm uppercase tracking-wider">Taille d'équipe :</span>
          <div class="flex bg-black/50 rounded-lg p-1 border border-white/5">
            <button @click="teamSize = 2; generateTeam()" :class="teamSize === 2 ? 'bg-apex-red text-white' : 'text-gray-400 hover:text-white'" class="px-4 py-1 rounded-md font-bold transition-colors">Duos (2)</button>
            <button @click="teamSize = 3; generateTeam()" :class="teamSize === 3 ? 'bg-apex-red text-white' : 'text-gray-400 hover:text-white'" class="px-4 py-1 rounded-md font-bold transition-colors">Trios (3)</button>
          </div>
        </div>

        <button @click="generateTeam" class="bg-apex-red hover:bg-red-600 text-white font-bold py-4 px-8 rounded-xl shadow-lg shadow-red-500/30 transition-all transform hover:scale-105 active:scale-95 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          GÉNÉRER
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 justify-center">
        <LegendCard 
          v-for="(legend, index) in currentTeam" 
          :key="legend.Name" 
          :legend="legend" 
          :role="index === 0 ? 'Joueur 1' : index === 1 ? 'Joueur 2' : 'Flex'" 
          :class="teamSize === 2 && index === 1 ? 'md:col-start-2' : ''"
        />
      </div>

      <div class="glass p-8 text-center max-w-3xl mx-auto mb-12">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-2">Analyse de l'Équipe</h2>
        <div class="text-4xl font-black text-white mb-6">
          Archétype : <span class="text-apex-red">{{ currentArchetype }}</span>
        </div>
        
        <div class="inline-block bg-black/50 rounded-lg px-6 py-3 border border-white/5 mb-6">
          <span class="text-gray-400 text-sm mr-2">Score Global de Synergie :</span>
          <span class="text-xl font-bold text-white">{{ currentScore.toFixed(1) }}</span>
        </div>

        <div v-if="currentSpecialSynergies.length > 0" class="space-y-3">
          <div v-for="syn in currentSpecialSynergies" :key="syn.name" class="bg-gradient-to-r from-yellow-500/20 to-orange-500/5 border border-yellow-500/30 rounded-lg p-4 text-left">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-xl">⚡</span>
              <h4 class="font-bold text-yellow-500">SUPER SYNERGIE : {{ syn.name }}</h4>
            </div>
            <p class="text-sm text-gray-300 ml-7">{{ syn.description }}</p>
          </div>
        </div>
      </div>

      <div class="glass p-8 max-w-3xl mx-auto mb-12">
        <h2 class="text-xl font-bold text-white uppercase tracking-widest mb-4 flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-apex-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          Calculateur de Probabilités
        </h2>
        <div class="flex flex-col md:flex-row gap-4 mb-6">
          <select v-model="probTarget" @change="updateProbs" class="bg-black/50 border border-white/10 text-white rounded-lg p-3 w-full md:w-1/2 focus:outline-none focus:border-apex-red">
            <option value="">Sélectionnez une Légende...</option>
            <option v-for="l in legends" :key="l.Name" :value="l.Name">{{ l.Name }}</option>
          </select>
          <p class="text-sm text-gray-400 md:w-1/2 flex items-center">
            Sélectionnez une légende pour voir avec qui elle a le plus de chances d'être associée par l'algorithme.
          </p>
        </div>

        <div v-if="probResults.length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-3 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
          <div v-for="res in probResults" :key="res.name" class="bg-black/30 border border-white/5 rounded p-3 flex justify-between items-center">
            <span class="font-bold text-gray-300">{{ res.name }}</span>
            <span class="text-apex-red font-mono">{{ res.prob.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(218, 41, 42, 0.5);
  border-radius: 4px;
}
</style>
