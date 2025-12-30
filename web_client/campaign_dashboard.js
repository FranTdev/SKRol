/* campaign_dashboard.js */

document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const campaignId = localStorage.getItem('currentCampaign');

    if (!user || !campaignId) {
        window.location.href = 'campaigns.html';
        return;
    }

    // Elements
    const campaignTitle = document.getElementById('campaign-title');
    const userSearchInput = document.getElementById('user-search-input');
    const searchBtn = document.getElementById('search-btn');
    const searchResults = document.getElementById('search-results');
    const participantList = document.getElementById('participant-list');
    const charList = document.getElementById('char-list');
    const charForm = document.getElementById('char-form');
    const charUserSelect = document.getElementById('char-user-select');

    // Global state
    let participants = [];

    // --- NAVIGATION ---
    window.showTab = (tabId) => {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

        document.getElementById(tabId).classList.add('active');
        event.currentTarget.classList.add('active');

        // Reload data depending on tab
        if (tabId === 'participantes') fetchParticipants();
        if (tabId === 'personajes') fetchCharacters();
    };

    // --- CAMPAIGN INFO ---
    async function fetchCampaignInfo() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${user.id}`);
            const data = await response.json();
            const current = data.find(c => c.id === campaignId);
            if (current) {
                campaignTitle.textContent = current.name.toUpperCase();
                document.getElementById('campaign-date').textContent = "Iniciado: " + new Date(current.created_at).toLocaleDateString();

                const adminName = current.admin ? current.admin.username : 'Desconocido';
                document.getElementById('campaign-admin').textContent = "Maestro: " + adminName;

                // Set global admin status
                window.isAdmin = current.admin_id === user.id;

                // Hide/Show admin-only elements
                if (!window.isAdmin) {
                    document.getElementById('participantes-tab-btn').style.display = 'none';
                    // We also hide the User Select in character creation
                    charUserSelect.parentElement.style.display = 'none';
                    // Also hide the participants section if user manages to navigate there
                    document.getElementById('search-panel').style.display = 'none';
                }
            }
        } catch (e) { console.error(e); }
    }

    // --- PARTICIPANTS ---
    async function fetchParticipants() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/participants`);
            participants = await response.json();

            participantList.innerHTML = '';
            charUserSelect.innerHTML = '<option value="">Sin asignar (NPC)</option>';

            participants.forEach(p => {
                const item = document.createElement('div');
                item.className = 'participant-item';
                const pUsername = p.users ? p.users.username : 'Usuario Desconocido';
                const pId = p.user_id;

                item.innerHTML = `
                    <span><strong>${pUsername}</strong> (${p.role})</span>
                    <button class="btn" style="border-color: #444; color: #888; padding: 0.2rem 0.5rem;" onclick="removeParticipant('${pId}')">Expulsar</button>
                `;
                participantList.appendChild(item);

                // Add to select for characters
                const opt = document.createElement('option');
                opt.value = pId;
                opt.textContent = pUsername;
                charUserSelect.appendChild(opt);
            });

            // Add self as well if not already there or just as owner
            if (!participants.find(p => p.user_id === user.id)) {
                const opt = document.createElement('option');
                opt.value = user.id;
                opt.textContent = user.username + " (Tú)";
                charUserSelect.appendChild(opt);
            }

        } catch (e) { console.error(e); }
    }

    searchBtn.onclick = async () => {
        const query = userSearchInput.value;
        if (query.length < 3) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/auth/users/search?username=${query}`);
            const data = await response.json();

            searchResults.innerHTML = '';
            searchResults.style.display = 'block';

            if (data.length === 0) {
                searchResults.innerHTML = '<div class="result-item">No se hallaron almas con ese nombre.</div>';
            }

            data.forEach(u => {
                if (u.id === user.id) return; // Don't add yourself
                const item = document.createElement('div');
                item.className = 'result-item';
                item.innerHTML = `
                    <span>${u.username}</span>
                    <button class="btn btn-small" onclick="addParticipant('${u.id}')">Añadir</button>
                `;
                searchResults.appendChild(item);
            });
        } catch (e) { console.error(e); }
    };

    window.addParticipant = async (targetUserId) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/participants?user_id=${targetUserId}`, {
                method: 'POST'
            });
            if (response.ok) {
                searchResults.style.display = 'none';
                userSearchInput.value = '';
                fetchParticipants();
            }
        } catch (e) { console.error(e); }
    };

    window.removeParticipant = async (targetUserId) => {
        if (!confirm('¿Expulsar a este integrante del Círculo?')) return;
        try {
            await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/participants/${targetUserId}`, { method: 'DELETE' });
            fetchParticipants();
        } catch (e) { console.error(e); }
    };

    // --- CHARACTERS ---
    async function fetchCharacters() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/characters/campaign/${campaignId}/${user.id}`);
            const data = await response.json();

            charList.innerHTML = '';
            data.forEach(char => {
                const card = document.createElement('div');
                const isOwner = char.user_id === user.id;
                const canEdit = window.isAdmin || isOwner;

                card.innerHTML = `
                    <h3 style="cursor: pointer;" onclick="openDetailedSheet('${char.id}')">${char.name}</h3>
                    <p style="font-size: 0.9rem; color: #888;">${char.description || 'Sin descripción'}</p>
                    <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                        <button class="btn btn-small" onclick="openDetailedSheet('${char.id}')">Ficha</button>
                        ${canEdit ? `<button class="btn btn-small" style="border-color: #555;" onclick="openEditChar('${char.id}', '${char.name}', '${char.user_id}', '${char.description}')">Ajustes</button>` : ''}
                        ${window.isAdmin ? `<button class="btn btn-small" style="border-color: #444;" onclick="deleteChar('${char.id}')">Hacer NPC</button>` : ''}
                    </div>
                `;
                charList.appendChild(card);
            });
        } catch (e) { console.error(e); }
    }

    document.getElementById('create-char-btn').onclick = () => {
        document.getElementById('char-modal-title').textContent = "NUEVO PERSONAJE";
        document.getElementById('char-id').value = '';
        charForm.reset();
        document.getElementById('char-modal').style.display = 'flex';
    };

    window.closeModal = (id) => document.getElementById(id).style.display = 'none';

    charForm.onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('char-id').value;
        const charData = {
            name: document.getElementById('char-name').value,
            user_id: window.isAdmin ? (charUserSelect.value || null) : user.id,
            description: document.getElementById('char-description').value,
            campaign_id: campaignId
        };

        const url = id ? `http://127.0.0.1:8000/characters/${id}` : `http://127.0.0.1:8000/characters/`;
        const method = id ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(charData)
            });
            if (response.ok) {
                closeModal('char-modal');
                fetchCharacters();
            }
        } catch (e) { console.error(e); }
    };

    window.openEditChar = (id, name, userId, desc) => {
        document.getElementById('char-modal-title').textContent = "EDITAR PERSONAJE";
        document.getElementById('char-id').value = id;
        document.getElementById('char-name').value = name;
        document.getElementById('char-user-select').value = userId || "";
        document.getElementById('char-description').value = desc || "";
        document.getElementById('char-modal').style.display = 'flex';
    };

    window.deleteChar = async (id) => {
        if (!confirm('¿Borrar esta hoja de personaje?')) return;
        await fetch(`http://127.0.0.1:8000/characters/${id}`, { method: 'DELETE' });
        fetchCharacters();
    };

    // INIT
    fetchCampaignInfo();
    fetchParticipants(); // Needed for character select

    // --- DETAILED SHEET LOGIC ---
    let currentChar = null;

    window.openDetailedSheet = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/characters/user/${user.id}`); // This is slow but for now it works to find one. Or better:
            // Let's assume we can fetch by ID. 
            // Wait, I don't have a single char fetch by ID endpoint in characters.py... Let's use the list and find.
            const listResp = await fetch(`http://127.0.0.1:8000/characters/campaign/${campaignId}/${user.id}`);
            const list = await listResp.json();
            currentChar = list.find(c => c.id === id);

            if (!currentChar) return;

            document.getElementById('sheet-char-name').textContent = currentChar.name;
            document.getElementById('sheet-desc').value = currentChar.description || '';
            renderStats();
            renderItems();
            document.getElementById('detailed-sheet').style.display = 'block';
        } catch (e) { console.error(e); }
    };

    window.closeDetailedSheet = () => {
        document.getElementById('detailed-sheet').style.display = 'none';
        fetchCharacters();
    };

    function renderStats() {
        const stats = currentChar.stats || { "Fuerza": 10, "Agilidad": 10, "Mente": 10, "Suerte": 10 };
        const grid = document.getElementById('sheet-stats');
        grid.innerHTML = '';
        for (const [s, v] of Object.entries(stats)) {
            const box = document.createElement('div');
            box.className = 'stat-box';
            box.innerHTML = `<label>${s}</label><div>${v}</div>`;
            grid.appendChild(box);
        }
    }

    function renderItems() {
        const items = currentChar.inventory || [];
        const list = document.getElementById('item-list');
        list.innerHTML = '';
        items.forEach((item, idx) => {
            const row = document.createElement('div');
            row.className = 'item-row';
            row.innerHTML = `
                <span>${item.name}</span>
                <span style="color: #666; font-size: 0.8rem;">${item.desc || ''}</span>
                <button onclick="removeItem(${idx})" class="btn btn-small" style="padding: 0.1rem 0.4rem; border-color: #333;">x</button>
            `;
            list.appendChild(row);
        });
    }

    window.rollRandomStats = () => {
        const stats = {
            "Fuerza": Math.floor(Math.random() * 15) + 5,
            "Agilidad": Math.floor(Math.random() * 15) + 5,
            "Mente": Math.floor(Math.random() * 15) + 5,
            "Suerte": Math.floor(Math.random() * 20) + 1
        };
        currentChar.stats = stats;
        renderStats();
    };

    window.addItem = () => {
        const name = prompt("Nombre del ítem:");
        if (!name) return;
        const desc = prompt("Descripción:");
        if (!currentChar.inventory) currentChar.inventory = [];
        currentChar.inventory.push({ name, desc });
        renderItems();
    };

    window.removeItem = (idx) => {
        currentChar.inventory.splice(idx, 1);
        renderItems();
    };

    window.saveSheetData = async () => {
        currentChar.description = document.getElementById('sheet-desc').value;
        try {
            const response = await fetch(`http://127.0.0.1:8000/characters/${currentChar.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentChar)
            });
            if (response.ok) {
                alert("Hoja guardada en el Haz.");
            }
        } catch (e) { console.error(e); }
    };

    // SHINING MACHINE SIMULATION (simplified from index.js logic)
    window.openShiningMachine = () => {
        const list = document.getElementById('shining-list');
        list.innerHTML = '';

        // Simulating 3 skill rolls
        const skills = [];
        for (let i = 0; i < 3; i++) {
            const rankVal = Math.random() > 0.8 ? 15 : 5;
            const rank = rankVal > 12 ? 'A' : 'C';
            const cat = Math.floor(Math.random() * 10) + 1;
            const idx = Math.floor(Math.random() * 10) + 1;
            skills.push({ rank, tag: `Tag ${cat}-${idx}`, effect: rank === 'A' ? 'Influencia sutil' : 'Intuición residual' });
        }

        skills.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="padding: 0.5rem; color: #9c27b0;">${s.rank}</td>
                <td style="padding: 0.5rem;">${s.tag}</td>
                <td style="padding: 0.5rem; color: #888;">${s.effect}</td>
            `;
            list.appendChild(tr);
        });

        // Add to char skills if needed (for simplicity just display)
        currentChar.skills = skills;
        document.getElementById('shining-machine-modal').style.display = 'flex';
    };

});
