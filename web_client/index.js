/* index.js */

document.addEventListener('DOMContentLoaded', () => {
    const activateBtn = document.getElementById('activate-btn');
    const tagListBody = document.getElementById('tag-list');
    const probabilityInput = document.getElementById('probability');
    const powerLimitInput = document.getElementById('power-limit');

    // Configuration and Labels (based on the original theme and RPG depth)
    const RANK_COLORS = {
        'S': 'rank-s',
        'A': 'rank-a',
        'B': 'rank-b',
        'C': 'rank-c',
        'D': 'rank-d'
    };

    // Helper: Random integer
    const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

    // Logic: Touch Probability
    function checkTouchProbability(prob) {
        return Math.random() < (prob / 100);
    }

    // Logic: Tag Maker (Rank, Category, Index)
    function createTag() {
        let rankRoll = randInt(1, 5);
        let rank;
        switch (rankRoll) {
            case 1: rank = 1; break;
            case 2: rank = 4; break;
            case 3: rank = 8; break;
            case 4: rank = 12; break;
            case 5:
                rank = (randInt(1, 10) === 1) ? 18 : 8;
                break;
            default: rank = 1;
        }
        return [rank, randInt(1, 10), randInt(1, 10)];
    }

    // Logic: Tag Checker (Value vs Power Limit, and Duplicates)
    function isTagValid(tag, tagList, powerLimit) {
        if (tag[0] > powerLimit) return false;
        // Check for duplicate category + index
        return !tagList.find(t => t[1] === tag[1] && t[2] === tag[2]);
    }

    // Logic: Tag Module (Bias towards same categories)
    function applyTagModule(tag, tagList, powerLimit) {
        if (tagList.length === 0) return tag;

        const lastTag = tagList[tagList.length - 1];
        const newTag = [tag[0], lastTag[1], tag[2]]; // Keep last category

        return isTagValid(newTag, tagList, powerLimit) ? newTag : tag;
    }

    // Logic: Random Power Level Generation (if not provided)
    function generatePowerLevel() {
        let pl = randInt(1, 50);
        if (pl >= 45) {
            pl += randInt(1, 50);
            if (pl >= 95) {
                pl += randInt(1, 100);
                if (pl >= 195) {
                    pl += randInt(1, 999);
                }
            }
        }
        return pl;
    }

    // Logic: Rank Conversions
    function convertRank(rankValue) {
        if (rankValue >= 18) return "S";
        if (rankValue >= 12) return "A";
        if (rankValue >= 8) return "B";
        if (rankValue >= 4) return "C";
        return "D";
    }

    // Logic: Sorting (Category then Index)
    function sortTags(tagList) {
        return tagList.sort((a, b) => {
            if (a[1] !== b[1]) return a[1] - b[1];
            return a[2] - b[2];
        });
    }

    // UI: Impact Description Generator (Thematic)
    function getImpact(rank) {
        const impacts = {
            'S': 'Alteración de la realidad / Destino',
            'A': 'Influencia masiva / Psicoquinesis',
            'B': 'Proyección táctica / Clarividencia',
            'C': 'Percepción aguda / Empatía',
            'D': 'Intuición residual / Susurro'
        };
        return impacts[rank] || 'Influencia sutil';
    }

    // MAIN ACTION: Activate Machine
    activateBtn.addEventListener('click', () => {
        const prob = parseInt(probabilityInput.value) || 0;
        let powerLimit = parseInt(powerLimitInput.value);

        // Reset Table
        tagListBody.innerHTML = '';

        if (!checkTouchProbability(prob)) {
            tagListBody.innerHTML = '<tr class="empty-row"><td colspan="3">No tienes el Resplandor... El Haz se diluye.</td></tr>';
            return;
        }

        // If no power limit provided, generate random high-level one
        if (!powerLimit || isNaN(powerLimit)) {
            powerLimit = generatePowerLevel();
        }

        let currentTags = [];
        let remainingPower = powerLimit;
        let attempts = 0;
        const MAX_ATTEMPTS = 500; // Prevent infinite loops

        while (remainingPower > 0 && attempts < MAX_ATTEMPTS) {
            attempts++;
            let tag = createTag();
            tag = applyTagModule(tag, currentTags, remainingPower);

            if (isTagValid(tag, currentTags, remainingPower)) {
                currentTags.push(tag);
                remainingPower -= tag[0];
            }
        }

        // Sort and Display
        const sortedTags = sortTags(currentTags);

        if (sortedTags.length === 0) {
            tagListBody.innerHTML = '<tr class="empty-row"><td colspan="3">La máquina no detectó habilidades compatibles...</td></tr>';
        } else {
            sortedTags.forEach(tag => {
                const rank = convertRank(tag[0]);
                const row = document.createElement('tr');
                row.className = 'skill-row';
                row.innerHTML = `
                    <td><span class="rank ${RANK_COLORS[rank]}">${rank}</span></td>
                    <td>Tag ${tag[1]}-${tag[2]}</td>
                    <td>${getImpact(rank)}</td>
                `;
                tagListBody.appendChild(row);
            });
        }
    });

    // Check session on load
    const userSession = localStorage.getItem('user');
    if (!userSession) {
        // Optional: Redirect to login if sensitive, 
        // but for a rolling machine we can just stay here.
        console.warn("No hay sesión activa. Los resultados no se guardarán.");
    }
});
