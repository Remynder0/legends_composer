<script setup lang="ts">
import { ref, computed } from 'vue'
import { legendsData, loadLegendDetails, currentLegendDetails, isLoadingLegendDetails } from '../../logic/store'

const searchQuery = ref('')
const selectedLegendName = ref<string | null>(null)

const filteredLegends = computed(() => {
    if (!searchQuery.value) return legendsData.value
    return legendsData.value.filter(l => l.Name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

async function selectLegend(name: string) {
    selectedLegendName.value = name
    await loadLegendDetails(name)
}

function closeModal() {
    selectedLegendName.value = null
}

const formatImgName = (name: string) => name.toLowerCase().replace(/ /g, '_')

const portraitError = ref(false)
const ability1Error = ref(false)
const ability2Error = ref(false)
const ability3Error = ref(false)

function handleSelectLegend(name: string) {
    portraitError.value = false;
    ability1Error.value = false;
    ability2Error.value = false;
    ability3Error.value = false;
    selectLegend(name);
}

function handleImageError(event: Event, fallbackSrc: string, errorFlagRef: 'portraitError' | 'ability1Error' | 'ability2Error' | 'ability3Error') {
    const img = event.target as HTMLImageElement;
    img.src = fallbackSrc;
    img.onerror = () => {
        if (errorFlagRef === 'portraitError') portraitError.value = true;
        if (errorFlagRef === 'ability1Error') ability1Error.value = true;
        if (errorFlagRef === 'ability2Error') ability2Error.value = true;
        if (errorFlagRef === 'ability3Error') ability3Error.value = true;
    };
}

function handleGridPortraitError(event: Event, fallbackSrc: string) {
    const img = event.target as HTMLImageElement;
    img.src = fallbackSrc;
}
</script>

<template>
  <div class="h-full flex flex-col overflow-hidden relative">
    <!-- Top Search Bar & Header -->
    <div class="p-6 border-b border-titan-border bg-black/60 shrink-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <h2 class="text-2xl font-black text-white tracking-widest uppercase font-mono flex items-center">
            <span class="text-titan-cyan mr-3 block w-3 h-3 bg-titan-cyan"></span> 
            Archives Légendes
        </h2>
        <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="RECHERCHER UNE LÉGENDE..." 
            class="w-full md:w-96 bg-black/50 border border-titan-border text-white px-4 py-2 font-mono text-sm focus:outline-none focus:border-titan-cyan transition-colors"
        />
    </div>

    <!-- Legends Grid -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-black/40">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 content-start">
            <button 
                v-for="legend in filteredLegends" 
                :key="legend.Name"
                @click="handleSelectLegend(legend.Name)"
                class="flex flex-col items-center justify-end p-0 border border-titan-border/50 bg-black/30 hover:border-titan-cyan transition-all relative group h-80 overflow-hidden"
            >
                <!-- Because some are .jpg and some are .png, we try .jpg first based on user instruction, fallback to .png -->
                <img 
                    :src="`/images/legends/portraits/${formatImgName(legend.Name)}.jpg`" 
                    @error="handleGridPortraitError($event, `/images/legends/portraits/${formatImgName(legend.Name)}.png`)"
                    :alt="legend.Name"
                    class="absolute inset-0 w-full h-full object-cover object-top opacity-70 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500"
                />
                <!-- Gradient overlay to make text readable -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent"></div>
                
                <div class="relative z-10 w-full p-4 text-center transform translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
                    <span class="font-black text-2xl uppercase tracking-widest font-sans text-white group-hover:text-titan-cyan transition-colors drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
                        {{ legend.Name }}
                    </span>
                    <div class="w-8 h-1 bg-titan-cyan mx-auto mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 delay-100"></div>
                </div>
            </button>
        </div>
    </div>

    <!-- Modal for Legend Details -->
    <div v-if="selectedLegendName" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 md:p-12">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="closeModal"></div>
        
        <!-- Modal Content -->
        <div class="relative w-full max-w-5xl h-full max-h-[90vh] bg-black border border-titan-cyan shadow-[0_0_50px_rgba(45,212,191,0.15)] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <!-- Close Button -->
            <button @click="closeModal" class="absolute top-4 right-4 z-50 w-12 h-12 flex items-center justify-center bg-black/80 border border-titan-border text-gray-400 hover:text-white hover:border-titan-orange transition-colors group">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 group-hover:rotate-90 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>

            <!-- Loading State -->
            <div v-if="isLoadingLegendDetails" class="flex-1 flex items-center justify-center">
                <div class="text-titan-orange font-mono animate-pulse flex items-center gap-3">
                    <span class="block w-3 h-3 bg-titan-orange"></span> EXTRACTION DES DONNÉES...
                </div>
            </div>

            <!-- Detail Content -->
            <div v-else-if="currentLegendDetails" class="flex-1 overflow-y-auto custom-scrollbar flex flex-col">
                <!-- Header / Portrait Area -->
                <div class="relative h-72 shrink-0 bg-gradient-to-b from-black/80 to-black border-b border-titan-border overflow-hidden">
                    <img 
                        v-show="!portraitError"
                        :src="`/images/legends/portraits/${formatImgName(currentLegendDetails.name)}.jpg`"
                        @error="handleImageError($event, `/images/legends/portraits/${formatImgName(currentLegendDetails.name)}.png`, 'portraitError')"
                        class="absolute top-0 right-0 h-[150%] object-contain object-top opacity-40 pointer-events-none transform translate-x-1/4 -translate-y-10 mask-image-gradient"
                    />
                    <div class="absolute inset-0 p-8 flex flex-col justify-end z-10 bg-gradient-to-r from-black via-black/90 to-transparent">
                        <h1 class="text-6xl md:text-7xl font-black text-white uppercase tracking-tighter drop-shadow-lg">{{ currentLegendDetails.name }}</h1>
                        <div class="text-titan-cyan font-mono tracking-widest uppercase mt-4 text-sm flex items-center gap-6">
                            <span class="flex items-center gap-2"><div class="w-1.5 h-1.5 bg-titan-cyan"></div> {{ currentLegendDetails.lore.real_name || 'IDENTITÉ INCONNUE' }}</span>
                            <span v-if="currentLegendDetails.lore.age" class="flex items-center gap-2"><div class="w-1.5 h-1.5 bg-titan-cyan"></div> ÂGE: {{ currentLegendDetails.lore.age }}</span>
                        </div>
                    </div>
                </div>

                <!-- Body Area -->
                <div class="p-8 md:p-10 flex-1 flex flex-col lg:flex-row gap-12 bg-black/60">
                    <!-- Lore -->
                    <div class="flex-1 space-y-8">
                        <div>
                            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono mb-3 flex items-center gap-2">
                                <span class="w-1.5 h-1.5 bg-gray-400 block"></span> Origine
                            </h3>
                            <p class="text-white font-mono text-lg tracking-wide">{{ currentLegendDetails.lore.home_world || 'Classification Secrète' }}</p>
                        </div>

                        <div v-if="currentLegendDetails.lore.bio">
                            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono mb-3 flex items-center gap-2">
                                <span class="w-1.5 h-1.5 bg-gray-400 block"></span> Biographie
                            </h3>
                            <p class="text-gray-300 font-sans leading-relaxed text-justify">{{ currentLegendDetails.lore.bio }}</p>
                        </div>
                    </div>

                    <!-- Abilities -->
                    <div class="flex-1 space-y-8 lg:border-l lg:border-titan-border/50 lg:pl-12">
                        <div class="relative">
                            <div class="absolute -left-12 top-1 bottom-1 w-px bg-titan-cyan/30 hidden lg:block"></div>
                            <h3 class="text-xs font-bold text-titan-cyan uppercase tracking-widest font-mono mb-6 flex items-center gap-2">
                                <span class="w-2 h-2 bg-titan-cyan block"></span> Capacités Tactiques
                            </h3>

                            <div class="space-y-8">
                                <!-- Passive -->
                                <div class="flex gap-5 items-start group">
                                    <div class="w-14 h-14 bg-black/80 border border-titan-border shrink-0 flex items-center justify-center group-hover:border-titan-cyan group-hover:bg-titan-cyan/5 transition-colors">
                                        <img 
                                            :src="`/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_2.svg`"
                                            @error="handleImageError($event, `/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_2.png`, 'ability2Error')"
                                            v-show="!ability2Error"
                                            class="w-8 h-8 invert opacity-80 group-hover:opacity-100 transition-opacity"
                                        />
                                        <span v-if="ability2Error" class="text-gray-600 font-mono text-xs">PAS</span>
                                    </div>
                                    <div>
                                        <div class="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">Passif</div>
                                        <h4 class="font-bold text-white uppercase tracking-wider text-lg">{{ currentLegendDetails.abilities.passive.name || 'Inconnu' }}</h4>
                                    </div>
                                </div>

                                <!-- Tactical -->
                                <div class="flex gap-5 items-start group">
                                    <div class="w-14 h-14 bg-black/80 border border-titan-border shrink-0 flex items-center justify-center group-hover:border-titan-cyan group-hover:bg-titan-cyan/5 transition-colors">
                                        <img 
                                            :src="`/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_1.svg`"
                                            @error="handleImageError($event, `/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_1.png`, 'ability1Error')"
                                            v-show="!ability1Error"
                                            class="w-8 h-8 invert opacity-80 group-hover:opacity-100 transition-opacity"
                                        />
                                        <span v-if="ability1Error" class="text-gray-600 font-mono text-xs">TAC</span>
                                    </div>
                                    <div>
                                        <div class="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">Tactique</div>
                                        <h4 class="font-bold text-white uppercase tracking-wider text-lg">{{ currentLegendDetails.abilities.tactical.name || 'Inconnu' }}</h4>
                                    </div>
                                </div>

                                <!-- Ultimate -->
                                <div class="flex gap-5 items-start group">
                                    <div class="w-14 h-14 bg-black/80 border border-titan-orange shrink-0 flex items-center justify-center group-hover:bg-titan-orange/10 transition-colors">
                                        <img 
                                            :src="`/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_3.svg`"
                                            @error="handleImageError($event, `/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_3.png`, 'ability3Error')"
                                            v-show="!ability3Error"
                                            class="w-8 h-8 invert opacity-90 group-hover:opacity-100 transition-opacity"
                                        />
                                        <span v-if="ability3Error" class="text-titan-orange/50 font-mono text-xs">ULT</span>
                                    </div>
                                    <div>
                                        <div class="text-[10px] text-titan-orange font-mono uppercase tracking-widest mb-1">Ultime</div>
                                        <h4 class="font-bold text-white uppercase tracking-wider text-lg">{{ currentLegendDetails.abilities.ultimate.name || 'Inconnu' }}</h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Error State -->
            <div v-else class="flex-1 flex items-center justify-center text-red-500 font-mono">
                ERREUR LORS DE L'EXTRACTION DES DONNÉES.
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.mask-image-gradient {
    mask-image: linear-gradient(to right, transparent, black 60%);
    -webkit-mask-image: linear-gradient(to right, transparent, black 60%);
}
</style>
