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

export function generateSeasons(): SeasonData[] {
    const seasons: SeasonData[] = [];
    
    const weapons1to21 = [
        "Havoc", "R-301", "Peacekeeper", "Flatline", "Wingman", "G7 Scout", 
        "R-99", "Longbow", "Devotion", "Volt", "Prowler", "Hemlok", 
        "Spitfire", "Triple Take", "Charge Rifle", "Mastiff", "C.A.R. SMG", 
        "EVA-8", "Rampage", "R-99", "30-30 Repeater"
    ];

    for (let i = 1; i <= 21; i++) {
        seasons.push({
            id: `s${i}`,
            name: `Saison ${i}`,
            level: 0,
            maxLevel: 110,
            purchased: false,
            weaponSkin: `Skin: ${weapons1to21[i - 1]}`
        });
    }

    const recentWeapons: Record<string, string> = {
        "s22_1": "P2020",
        "s22_2": "Alternator",
        "s26_1": "L-Star",
        "s26_2": "L-Star",
        "s28_1": "Bocek",
        "s28_2": "Bocek",
        "s29_1": "RE-45",
        "s29_2": "RE-45"
    };

    for (let i = 22; i <= 29; i++) {
        for (let split = 1; split <= 2; split++) {
            const id = `s${i}_${split}`;
            seasons.push({
                id: id,
                name: `Saison ${i} (S${split})`,
                level: 0,
                maxLevel: 60,
                purchased: false,
                weaponSkin: `Skin: ${recentWeapons[id] || "Arme Premium"}`
            });
        }
    }
    
    return seasons;
}

const seasonDataFiles: Record<string, any> = import.meta.glob('../../data/season_pass/*.json', { eager: true });

export function calculateSeasonPacks(seasonId: string, level: number, purchased: boolean, maxLevel: number): number {
    if (maxLevel === 110) {
        // Extract season number from seasonId (e.g., 's1' -> 1)
        const seasonNum = parseInt(seasonId.replace('s', ''), 10);
        const jsonPath = `../../data/season_pass/season_${seasonNum}.json`;
        
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
