export function calculatePrestige0Packs(level: number): number {
    let packs = 0;
    if (level >= 2) {
        packs += Math.min(level, 20) - 1;
    }
    if (level >= 22) {
        packs += Math.floor((Math.min(level, 300) - 20) / 2);
    }
    if (level >= 305) {
        packs += Math.floor((Math.min(level, 500) - 300) / 5);
    }
    return packs;
}

export function calculatePrestigePacks(level: number): number {
    let packs = 0;
    const l = Math.min(level, 500);
    if (l > 0) packs += Math.floor(Math.min(l, 100) / 10);
    if (l > 100) packs += Math.round((Math.min(l, 200) - 100) * 0.13);
    if (l > 200) packs += Math.round((Math.min(l, 300) - 200) * 0.17);
    if (l > 300) packs += Math.round((Math.min(l, 400) - 300) * 0.25);
    if (l > 400) packs += Math.round((Math.min(l, 500) - 400) * 0.50);
    return packs;
}

export function calculateAccountLevelPacks(level: number, prestige: number): number {
    let totalPacks = 0;
    if (prestige === 0) {
        totalPacks += calculatePrestige0Packs(level);
    } else {
        totalPacks += 199;
        for (let i = 1; i < prestige; i++) {
            totalPacks += 115;
        }
        totalPacks += calculatePrestigePacks(level);
    }
    return totalPacks;
}

export interface SeasonData {
    id: string;
    name: string;
    level: number;
    maxLevel: number;
    purchased: boolean;
    weaponSkin: string;
}

export function getParsedSeasonData(seasonId: string): any {
    const cleanId = seasonId.replace('s', '');
    const jsonPath = `../../data/seasons/season_${cleanId}.json`;
    return seasonDataFiles[jsonPath]?.default || seasonDataFiles[jsonPath];
}

const LEVEL_1_WEAPON_SKINS: Record<string, string> = {
    "1": "R-301: Honored Prey",
    "2": "Spitfire: The Intimidator",
    "3": "Longbow: Reckoner",
    "4": "R-99: Zero Point",
    "5": "Hemlok: Retrofitted",
    "6": "Sentinel: Rollcage",
    "7": "Prowler: Polished Perfection",
    "8": "Flatline: Chained Beast",
    "9": "Spitfire: Way of the Serpent",
    "10": "30-30: Winged Sun",
    "11": "Triple Take: Compound Fracture",
    "12": "EVA-8: Rolling Thunder",
    "13": "Spitfire: Wyrmborn",
    "14": "Triple Take: Lucky Draw",
    "15": "Havoc: Obsidian Night",
    "16": "R-301: Frenzied Frequency",
    "17": "Devotion: Technomancer",
    "18": "L-STAR: Advanced Reign",
    "19": "Triple Take: Copper Conductor",
    "20": "Triple Take: Teal Energizer",
    "21": "Volt: Void Touched",
    "22_1": "Devotion: Arcade Space",
    "22_2": "Prowler: Night Beasts",
    "23_1": "Spitfire: Under the Ice",
    "23_2": "R-301: Happy Valley Adventure",
    "24_1": "Havoc: WELCOME TO THE GUN SHOW",
    "24_2": "Inconnu",
    "25_1": "Mastiff: Don't Get Under Foot",
    "25_2": "Havoc: Here Comes the Heat",
    "26_1": "L-Star: Let's Go",
    "26_2": "Peacekeeper: Thorn in Your Side",
    "27_1": "P2020: Big Regrets",
    "27_2": "Alternator: Locked In",
    "28_1": "Bocek: Final Approach",
    "28_2": "Bocek: Echo Location",
    "29_1": "RE-45: Cell Signal",
    "29_2": "RE-45: Time to Improvise"
};

export function generateSeasons(): SeasonData[] {
    const seasons: SeasonData[] = [];
    
    for (let i = 1; i <= 21; i++) {
        const id = `s${i}`;
        const skinName = LEVEL_1_WEAPON_SKINS[`${i}`] || "Inconnu";
        const weaponSkin = `Skin: ${skinName}`;

        seasons.push({
            id,
            name: `Saison ${i}`,
            level: 0,
            maxLevel: 110,
            purchased: false,
            weaponSkin
        });
    }

    for (let i = 22; i <= 29; i++) {
        for (let split = 1; split <= 2; split++) {
            const id = `s${i}_${split}`;
            const key = `${i}_${split}`;
            const skinName = LEVEL_1_WEAPON_SKINS[key] || "Arme Premium";
            const weaponSkin = `Skin: ${skinName}`;

            seasons.push({
                id: id,
                name: `Saison ${i} (S${split})`,
                level: 0,
                maxLevel: 60,
                purchased: false,
                weaponSkin
            });
        }
    }
    
    return seasons;
}

const seasonDataFiles: Record<string, any> = import.meta.glob('../../data/seasons/*.json', { eager: true });

export function calculateSeasonPacks(seasonId: string, level: number, purchased: boolean, maxLevel: number): number {
    const cleanId = seasonId.replace('s', '');
    const jsonPath = `../../data/seasons/season_${cleanId}.json`;
    
    if (seasonDataFiles[jsonPath]) {
        const data = seasonDataFiles[jsonPath].default || seasonDataFiles[jsonPath];
        const rewards = data.rewards;
        let total = 0;
        
        for (let l = 1; l <= level; l++) {
            const levelData = rewards[`level_${l}`];
            if (levelData) {
                if (levelData.free) {
                    total += levelData.free.filter((r: string) => r.includes('Apex Pack')).length;
                }
                if (purchased && levelData.premium) {
                    total += levelData.premium.filter((r: string) => r.includes('Apex Pack')).length;
                }
            }
        }
        return total;
    }

    if (maxLevel === 110) {
        const freeLevels = [3, 7, 13, 27, 33, 43, 53];
        const premiumLevels = [5, 12, 25, 41, 57, 63, 85];
        
        let total = 0;
        for(const l of freeLevels) {
            if (level >= l) total++;
        }
        if (purchased) {
            for(const l of premiumLevels) {
                if (level >= l) total++;
            }
        }
        return total;
    } else {
        const freeLevels = [5, 15, 25, 35, 45];
        const premiumLevels = [10, 20, 30, 40, 50];
        
        let total = 0;
        for(const l of freeLevels) {
            if (level >= l) total++;
        }
        if (purchased) {
            for(const l of premiumLevels) {
                if (level >= l) total++;
            }
        }
        return total;
    }
}

