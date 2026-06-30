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
</script>

<template>
  <div class="h-full flex flex-col md:flex-row gap-6 overflow-hidden">
    <!-- Left List -->
    <div class="w-full md:w-1/2 lg:w-1/3 flex flex-col h-full bg-black/40 border border-titan-border glass-panel">
        <div class="p-4 border-b border-titan-border bg-black/60">
            <h2 class="text-xl font-black text-white tracking-widest uppercase font-mono mb-4 flex items-center">
                <span class="text-titan-cyan mr-2 block w-2 h-2 bg-titan-cyan"></span> 
                Archives Légendes
            </h2>
            <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="RECHERCHER..." 
                class="w-full bg-black/50 border border-titan-border text-white px-4 py-2 font-mono text-sm focus:outline-none focus:border-titan-cyan transition-colors"
            />
        </div>
        
        <div class="flex-1 overflow-y-auto custom-scrollbar p-4 grid grid-cols-2 gap-3 content-start">
            <button 
                v-for="legend in filteredLegends" 
                :key="legend.Name"
                @click="handleSelectLegend(legend.Name)"
                class="flex flex-col items-center justify-center p-4 border transition-all relative group"
                :class="selectedLegendName === legend.Name ? 'border-titan-cyan bg-titan-cyan/10' : 'border-titan-border/50 bg-black/30 hover:border-titan-orange hover:bg-black/50'"
            >
                <div class="w-16 h-16 bg-black/50 border border-titan-border mb-3 overflow-hidden relative">
                    <img 
                        :src="`/images/legends/icons/${formatImgName(legend.Name)}.png`" 
                        :alt="legend.Name"
                        class="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity"
                        onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                    />
                    <div class="absolute inset-0 hidden items-center justify-center text-2xl font-bold font-mono text-gray-600">?</div>
                </div>
                <span class="font-black text-sm uppercase tracking-wider font-sans" :class="selectedLegendName === legend.Name ? 'text-titan-cyan' : 'text-gray-300'">
                    {{ legend.Name }}
                </span>
            </button>
        </div>
    </div>

    <!-- Right Detail Panel -->
    <div class="flex-1 h-full bg-black/40 border border-titan-border glass-panel overflow-hidden flex flex-col relative">
        <div v-if="!selectedLegendName" class="flex-1 flex flex-col items-center justify-center text-gray-500 font-mono p-8 text-center">
            <div class="w-16 h-16 border border-gray-600 mb-4 flex items-center justify-center opacity-50">
                <div class="w-8 h-8 border border-gray-500 rotate-45"></div>
            </div>
            SÉLECTIONNEZ UNE LÉGENDE POUR<br/>AFFICHER SES DONNÉES SÉCURISÉES
        </div>

        <div v-else-if="isLoadingLegendDetails" class="flex-1 flex items-center justify-center">
            <div class="text-titan-orange font-mono animate-pulse flex items-center gap-3">
                <span class="block w-3 h-3 bg-titan-orange"></span> EXTRACTION DES DONNÉES...
            </div>
        </div>
        
        <div v-else-if="currentLegendDetails" class="flex-1 overflow-y-auto custom-scrollbar flex flex-col">
            <!-- Header / Portrait Area -->
            <div class="relative h-64 shrink-0 bg-gradient-to-b from-black/80 to-black/20 border-b border-titan-border overflow-hidden">
                <img 
                    v-show="!portraitError"
                    :src="`/images/legends/portraits/${formatImgName(currentLegendDetails.name)}.png`"
                    @error="handleImageError($event, `/images/legends/portraits/${formatImgName(currentLegendDetails.name)}.jpg`, 'portraitError')"
                    class="absolute top-0 right-0 h-[150%] object-contain object-top opacity-50 pointer-events-none transform translate-x-1/4 -translate-y-10 mask-image-gradient"
                />
                <div class="absolute inset-0 p-8 flex flex-col justify-end z-10 bg-gradient-to-r from-black via-black/80 to-transparent">
                    <h1 class="text-5xl md:text-6xl font-black text-white uppercase tracking-tighter">{{ currentLegendDetails.name }}</h1>
                    <div class="text-titan-cyan font-mono tracking-widest uppercase mt-2 text-sm flex items-center gap-4">
                        <span>// {{ currentLegendDetails.lore.real_name || 'INCONNU' }}</span>
                        <span v-if="currentLegendDetails.lore.age">ÂGE: {{ currentLegendDetails.lore.age }}</span>
                    </div>
                </div>
            </div>

            <!-- Body Area -->
            <div class="p-8 flex-1 flex flex-col lg:flex-row gap-12">
                
                <!-- Lore -->
                <div class="flex-1 space-y-6">
                    <div>
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono mb-3 flex items-center gap-2">
                            <span class="w-1.5 h-1.5 bg-gray-400 block"></span> Origine
                        </h3>
                        <p class="text-white font-mono text-lg">{{ currentLegendDetails.lore.home_world || 'Classification Secrète' }}</p>
                    </div>

                    <div v-if="currentLegendDetails.lore.bio">
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest font-mono mb-3 flex items-center gap-2">
                            <span class="w-1.5 h-1.5 bg-gray-400 block"></span> Biographie
                        </h3>
                        <p class="text-gray-300 font-sans leading-relaxed">{{ currentLegendDetails.lore.bio }}</p>
                    </div>
                </div>

                <!-- Abilities -->
                <div class="flex-1 space-y-8 lg:border-l lg:border-titan-border/50 lg:pl-12">
                    
                    <div class="relative">
                        <div class="absolute -left-12 top-1 bottom-1 w-px bg-titan-cyan/30 hidden lg:block"></div>
                        <h3 class="text-xs font-bold text-titan-cyan uppercase tracking-widest font-mono mb-4 flex items-center gap-2">
                            <span class="w-2 h-2 bg-titan-cyan block"></span> Capacités Tactiques
                        </h3>

                        <div class="space-y-6">
                            <!-- Passive -->
                            <div class="flex gap-4 items-start group">
                                <div class="w-12 h-12 bg-black/60 border border-titan-border shrink-0 flex items-center justify-center group-hover:border-titan-cyan transition-colors">
                                    <img 
                                        :src="`/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_2.svg`"
                                        @error="handleImageError($event, `/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_2.png`, 'ability2Error')"
                                        v-show="!ability2Error"
                                        class="w-8 h-8 invert"
                                    />
                                    <span v-if="ability2Error" class="text-gray-600 font-mono text-xs">PAS</span>
                                </div>
                                <div>
                                    <div class="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">Passif</div>
                                    <h4 class="font-bold text-white uppercase tracking-wider">{{ currentLegendDetails.abilities.passive.name || 'Inconnu' }}</h4>
                                </div>
                            </div>

                            <!-- Tactical -->
                            <div class="flex gap-4 items-start group">
                                <div class="w-12 h-12 bg-black/60 border border-titan-border shrink-0 flex items-center justify-center group-hover:border-titan-cyan transition-colors">
                                    <img 
                                        :src="`/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_1.svg`"
                                        @error="handleImageError($event, `/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_1.png`, 'ability1Error')"
                                        v-show="!ability1Error"
                                        class="w-8 h-8 invert"
                                    />
                                    <span v-if="ability1Error" class="text-gray-600 font-mono text-xs">TAC</span>
                                </div>
                                <div>
                                    <div class="text-[10px] text-gray-500 font-mono uppercase tracking-widest mb-1">Tactique</div>
                                    <h4 class="font-bold text-white uppercase tracking-wider">{{ currentLegendDetails.abilities.tactical.name || 'Inconnu' }}</h4>
                                </div>
                            </div>

                            <!-- Ultimate -->
                            <div class="flex gap-4 items-start group">
                                <div class="w-12 h-12 bg-black/60 border border-titan-orange shrink-0 flex items-center justify-center group-hover:bg-titan-orange/10 transition-colors">
                                    <img 
                                        :src="`/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_3.svg`"
                                        @error="handleImageError($event, `/images/legends/abilities/${formatImgName(currentLegendDetails.name)}_ability_3.png`, 'ability3Error')"
                                        v-show="!ability3Error"
                                        class="w-8 h-8 invert"
                                    />
                                    <span v-if="ability3Error" class="text-titan-orange/50 font-mono text-xs">ULT</span>
                                </div>
                                <div>
                                    <div class="text-[10px] text-titan-orange font-mono uppercase tracking-widest mb-1">Ultime</div>
                                    <h4 class="font-bold text-white uppercase tracking-wider">{{ currentLegendDetails.abilities.ultimate.name || 'Inconnu' }}</h4>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div v-else class="flex-1 flex items-center justify-center text-red-500 font-mono">
            ERREUR LORS DE L'EXTRACTION DES DONNÉES.
        </div>
    </div>
  </div>
</template>

<style scoped>
.mask-image-gradient {
    mask-image: linear-gradient(to right, transparent, black 50%);
    -webkit-mask-image: linear-gradient(to right, transparent, black 50%);
}
</style>
