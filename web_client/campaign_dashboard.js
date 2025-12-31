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
        // If event is not present (called from code), we find the button
        const btn = window.event ? window.event.currentTarget : document.querySelector(`.tab-btn[onclick*="${tabId}"]`);
        if (btn) btn.classList.add('active');

        // Reload data depending on tab
        if (tabId === 'participantes') fetchParticipants();
        if (tabId === 'personajes') fetchCharacters();
        if (tabId === 'gestion') {
            fetchParticipantsLimits();
            fetchCampaignSettings();
        }
    };

    async function fetchCampaignSettings() {
        if (!window.isAdmin) return;
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/settings`);
            const settings = await response.json();

            document.getElementById('campaign-rules-input').value = settings.rules || "";
            document.getElementById('shining-prob-input').value = settings.shining_prob || 1.0;
            document.getElementById('max-power-input').value = settings.max_power || 50;
            document.getElementById('global-char-limit-input').value = settings.default_char_limit || 3;
        } catch (e) { console.error(e); }
    }

    window.saveCampaignGeneralSettings = async () => {
        const settings = {
            rules: document.getElementById('campaign-rules-input').value,
            shining_prob: parseFloat(document.getElementById('shining-prob-input').value),
            max_power: parseInt(document.getElementById('max-power-input').value),
            default_char_limit: parseInt(document.getElementById('global-char-limit-input').value),
        };

        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/settings?requester_id=${user.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            if (response.ok) {
                alert("Configuración del Mundo salvaguardada.");
            } else {
                const err = await response.json();
                alert("Error: " + err.detail);
            }
        } catch (e) { console.error(e); }
    };

    async function fetchParticipantsLimits() {
        if (!window.isAdmin) return;
        const list = document.getElementById('limit-management-list');
        list.innerHTML = 'Cargando pistoleros...';
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/participants/limits`);
            if (!response.ok) {
                const errData = await response.json();
                list.innerHTML = `<p style="color: #f44;">Error del Haz: ${errData.detail || response.statusText}</p>`;
                return;
            }
            const data = await response.json();
            list.innerHTML = '';
            if (data.length === 0) {
                list.innerHTML = '<p style="color: #666; font-style: italic;">No hay otros pistoleros en este Círculo.</p>';
            }
            data.forEach(p => {
                const item = document.createElement('div');
                item.className = 'participant-item';
                item.innerHTML = `
                    <div>
                        <strong>${p.users ? p.users.username : 'NPC'}</strong>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span style="font-size: 0.8rem; color: #888;">Límite de vivos:</span>
                        <input type="number" class="limit-input" value="${p.char_limit || 3}" 
                            onchange="updateLimit('${p.user_id}', this.value)">
                    </div>
                `;
                list.appendChild(item);
            });
        } catch (e) {
            console.error(e);
            list.innerHTML = '<p style="color: #f44;">El Haz ha bloqueado la conexión.</p>';
        }
    }

    window.updateLimit = async (targetUserId, newLimit) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/participants/${targetUserId}/limit`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limit: parseInt(newLimit) })
            });
            if (response.ok) {
                console.log(`Límite actualizado para ${targetUserId}: ${newLimit}`);
            } else {
                const err = await response.json();
                alert("Error al actualizar límite: " + (err.detail || "Desconocido"));
            }
        } catch (e) {
            console.error(e);
            alert("Fallo en la conexión al actualizar el límite.");
        }
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
                } else {
                    // Show admin only elements
                    document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
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

                const stats = char.stats || {};
                const estado = stats.Estado || char.condition?.status || 'vivo';
                const isDead = estado === 'muerte';
                const isTranscended = estado === 'trascendido';
                const isPendingDeath = char.condition && char.condition.request_death === true;

                // Players can only open sheet if not dead and not transcended
                const canOpenSheet = window.isAdmin || (isOwner && !isDead && !isTranscended);
                const canAdjust = window.isAdmin || (isOwner && !isDead && !isTranscended);

                card.className = `char-card ${isDead ? 'dead' : ''} ${isTranscended ? 'transcended' : ''} ${isPendingDeath ? 'pending-death' : ''}`;
                card.innerHTML = `
                    <h3 style="${canOpenSheet ? 'cursor: pointer;' : 'cursor: default;'}" onclick="${canOpenSheet ? `openDetailedSheet('${char.id}')` : ''}">${char.name} ${isDead ? '(CAÍDO)' : isTranscended ? '(TRASCENDIDO)' : ''}</h3>
                    <div style="font-size: 0.8rem; color: #666; margin-bottom: 0.5rem;">Controlado por: ${char.users ? char.users.username : 'NPC'}</div>
                    <p style="font-size: 0.9rem; color: #888;">${char.description ? char.description.substring(0, 100) + '...' : 'Sin descripción'}</p>
                    ${isPendingDeath ? '<p style="color: #ff9800; font-size: 0.8rem; font-weight: bold; animation: death-aura 2s infinite;">[EL FINAL SE ACERCA]</p>' : ''}
                    <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                        ${canOpenSheet ? `<button class="btn btn-small" onclick="openDetailedSheet('${char.id}')">Ficha</button>` : ''}
                        ${canAdjust ? `<button class="btn btn-small" style="border-color: #555;" onclick="openEditChar('${char.id}', '${char.name}', '${char.user_id}', '${char.description}')">Ajustes</button>` : ''}
                        ${(isDead || isTranscended) && !window.isAdmin ? `<span style="color: #444; font-size: 0.7rem; align-self: center;">El Haz te impide interactuar con este ${isTranscended ? 'Ser' : 'Caído'}.</span>` : ''}
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
        document.getElementById('admin-controls').style.display = 'none';
        document.getElementById('char-modal').style.display = 'flex';
    };

    window.closeModal = (id) => document.getElementById(id).style.display = 'none';

    charForm.onsubmit = async (e) => {
        e.preventDefault();

        // LIMIT CHECK
        if (!window.isAdmin) {
            try {
                // Get all characters and count live ones
                const charResp = await fetch(`http://127.0.0.1:8000/characters/campaign/${campaignId}/${user.id}`);
                const allChars = await charResp.json();
                const liveChars = allChars.filter(c => c.user_id === user.id && (!c.condition || c.condition.status !== 'muerte'));

                // Get user limit overrides and campaign default
                const limitsResp = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/participants/limits`);
                const limitsData = await limitsResp.json();
                const userOverride = limitsData.find(l => l.user_id === user.id)?.char_limit;

                // Priority: User Override > Global Campaign Limit > Default 3
                let finalLimit = 3;
                if (userOverride !== undefined && userOverride !== null) {
                    finalLimit = userOverride;
                } else {
                    const settingsResp = await fetch(`http://127.0.0.1:8000/campaigns/${campaignId}/settings`);
                    const settings = await settingsResp.json();
                    finalLimit = settings.default_char_limit || 3;
                }

                if (liveChars.length >= finalLimit) {
                    alert(`Has alcanzado tu límite de pistoleros activos (${finalLimit}).`);
                    return;
                }
            } catch (e) { console.error("Error checking limits", e); }
        }

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
            const response = await fetch(`${url}?requester_id=${user.id}`, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(charData)
            });
            if (response.ok) {
                closeModal('char-modal');
                fetchCharacters();
            } else {
                const err = await response.json();
                alert("Error: " + err.detail);
            }
        } catch (e) { console.error(e); }
    };

    window.openEditChar = (id, name, userId, desc) => {
        document.getElementById('char-modal-title').textContent = "AJUSTES DE PERSONAJE";
        document.getElementById('char-id').value = id;
        document.getElementById('char-name').value = name;
        document.getElementById('char-user-select').value = userId || "";
        document.getElementById('char-description').value = desc || "";

        if (window.isAdmin) {
            document.getElementById('admin-controls').style.display = 'block';
        }

        document.getElementById('char-modal').style.display = 'flex';
    };

    window.adminUpdateCondition = async (status) => {
        const id = document.getElementById('char-id').value;
        try {
            // Update both for compatibility
            const response = await fetch(`http://127.0.0.1:8000/characters/${id}/condition?requester_id=${user.id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: status })
            });

            // Update stats.estado refactor
            const charResp = await fetch(`http://127.0.0.1:8000/characters/campaign/${campaignId}/${user.id}`);
            const list = await charResp.json();
            const char = list.find(c => c.id === id);
            if (char) {
                if (!char.stats) char.stats = {};
                char.stats.Estado = status;

                // Also clear death request if confirm death, revive or transcend
                if (status === 'muerte' || status === 'vivo' || status === 'trascendido') {
                    if (char.condition) char.condition.request_death = false;
                }

                await fetch(`http://127.0.0.1:8000/characters/${id}?requester_id=${user.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(char)
                });
            }

            if (response.ok) {
                closeModal('char-modal');
                fetchCharacters();
            }
        } catch (e) { console.error(e); }
    };

    window.deletePermanent = async () => {
        const id = document.getElementById('char-id').value;
        if (!confirm('¿ESTÁS SEGURO? Esto eliminará al personaje TOTALMENTE del Haz. Esta acción es irreversible.')) return;

        const verification = prompt('Por favor, escribe "BORRAR" para confirmar:');
        if (verification !== 'BORRAR') return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/characters/${id}/permanent`, { method: 'DELETE' });
            if (response.ok) {
                closeModal('char-modal');
                fetchCharacters();
            }
        } catch (e) { console.error(e); }
    };


    // INIT
    fetchCampaignInfo();
    fetchParticipants(); // Needed for character select

    // --- DETAILED SHEET LOGIC ---
    let currentChar = null;

    window.openDetailedSheet = async (id) => {
        try {
            const listResp = await fetch(`http://127.0.0.1:8000/characters/campaign/${campaignId}/${user.id}`);
            const list = await listResp.json();
            currentChar = list.find(c => c.id === id);

            if (!currentChar) return;

            document.getElementById('sheet-char-name').textContent = currentChar.name;
            const descArea = document.getElementById('sheet-desc');
            descArea.value = currentChar.description || '';
            descArea.style.height = 'auto';
            descArea.style.height = descArea.scrollHeight + 'px';
            descArea.readOnly = true;
            document.getElementById('edit-desc-btn').textContent = "🔨 Editar";

            document.querySelector('#sheet-owner span').textContent = currentChar.users ? currentChar.users.username : 'NPC';

            renderStats();
            renderItems();
            renderQuickConditions();
            renderSkills();

            // LOCK GENERATORS: Disable buttons instead of hiding
            const stats = currentChar.stats || {};
            const estado = stats.Estado || currentChar.condition?.status || 'vivo';
            const isDead = estado === 'muerte';
            const isTranscended = estado === 'trascendido';

            const isStatsGenerated = stats['Vida Máxima'] > 0;
            const isShiningGenerated = currentChar.skills && currentChar.skills.length > 0;

            const rollBtn = document.getElementById('roll-stats-btn');
            const shiningBtn = document.getElementById('roll-shining-btn');

            // Admin can always click these, players are locked if already generated OR if character is special state
            if (rollBtn) rollBtn.disabled = (isStatsGenerated || isDead || isTranscended) && !window.isAdmin;
            if (shiningBtn) shiningBtn.disabled = (isShiningGenerated || isDead || isTranscended) && !window.isAdmin;

            document.getElementById('detailed-sheet').style.display = 'block';
        } catch (e) { console.error(e); }
    };

    window.closeDetailedSheet = () => {
        document.getElementById('detailed-sheet').style.display = 'none';
        fetchCharacters();
    };

    window.toggleEditDesc = () => {
        const area = document.getElementById('sheet-desc');
        const btn = document.getElementById('edit-desc-btn');
        if (area.readOnly) {
            area.readOnly = false;
            area.focus();
            btn.textContent = "💾 Bloquear";
        } else {
            area.readOnly = true;
            btn.textContent = "🔨 Editar";
            saveSheetData();
        }
    };

    window.requestDeath = async () => {
        const message = window.isAdmin
            ? 'Nota: Has marcado a este personaje para el final. El Haz aguarda tu confirmación final en los Ajustes.'
            : '¿Deseas solicitar el fin de este personaje ante el Maestro?';

        if (!confirm(message)) return;

        if (!currentChar.condition) currentChar.condition = {};
        currentChar.condition.request_death = true;

        // Also add to a general status list if not there
        if (!currentChar.condition.status_list) currentChar.condition.status_list = [];
        if (!currentChar.condition.status_list.includes('Petición de Muerte')) {
            currentChar.condition.status_list.push('Petición de Muerte');
        }

        await saveSheetData();

        if (!window.isAdmin) alert("Petición de muerte enviada al Maestro.");
        renderQuickConditions();
        closeDetailedSheet();
    };

    function renderStats() {
        const stats = currentChar.stats || {};
        const grid = document.getElementById('sheet-stats');
        grid.innerHTML = '';

        const statKeys = [
            'Vida Máxima', 'Vida', 'Fuerza', 'Resistencia',
            'Fuerza Resplandor', 'Resistencia Resplandor', 'Destreza', 'Inteligencia', 'Estado'
        ];

        statKeys.forEach(s => {
            const val = stats[s] || (s === 'Estado' ? 'vivo' : 0);
            const box = document.createElement('div');
            box.className = 'stat-box';
            box.innerHTML = `<label>${s}</label><div>${val}</div>`;
            grid.appendChild(box);
        });
    }

    function renderQuickConditions() {
        const cond = currentChar.condition || {};
        const stats = currentChar.stats || {};
        const estado = stats.Estado || cond.status || 'vivo';

        const list = document.getElementById('quick-conditions');
        list.innerHTML = '';

        const badge = document.createElement('span');
        badge.className = 'btn btn-small';

        let color = '#0f0';
        if (estado === 'muerte') color = '#f44';
        if (estado === 'trascendido') color = '#9c27b0';

        badge.style = `border-color: ${color}; color: ${color}; pointer-events: none; ${estado === 'trascendido' ? 'animation: transcendental-glow 4s infinite alternate;' : ''}`;
        badge.textContent = estado.toUpperCase();
        if (estado === 'trascendido') {
            badge.innerHTML = '✨ TRASCENDIDO ✨';
        }
        list.appendChild(badge);

        if (cond.request_death) {
            const b = document.createElement('span');
            b.className = 'btn btn-small';
            b.style = 'border-color: #ff9800; color: #ff9800; pointer-events: none;';
            b.textContent = 'AGONIZANTE';
            list.appendChild(b);
        }
    }

    window.openConditionsModal = () => {
        const cond = currentChar.condition || {};
        const list = document.getElementById('conditions-list');
        list.innerHTML = '';

        const statuses = cond.status_list || [];
        // Add basic status
        statuses.unshift(cond.status === 'muerte' ? "Fallecido (En el Haz)" : "En plenitud (Consciente)");

        if (cond.request_death) statuses.push("Petición de finalización pendiente");

        statuses.forEach(s => {
            const item = document.createElement('div');
            item.style = "padding: 0.5rem; background: rgba(255,152,0,0.1); border-left: 3px solid #ff9800; color: #eee;";
            item.textContent = s;
            list.appendChild(item);
        });

        document.getElementById('conditions-modal').style.display = 'flex';
    };

    function renderSkills() {
        const skills = currentChar.skills || [];
        const container = document.getElementById('sheet-skills');
        if (!container) return;

        container.innerHTML = '';
        if (skills.length === 0) {
            container.innerHTML = '<div style="color: #666; font-style: italic; font-size: 0.9rem;">Sin habilidades detectadas...</div>';
            return;
        }

        skills.forEach(s => {
            const row = document.createElement('div');
            const rankClass = `rank-${s.rank.toLowerCase()}`;
            row.style = "padding: 0.5rem; background: rgba(20, 20, 20, 0.6); border-left: 3px solid currentColor; display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;";
            row.className = rankClass;
            row.innerHTML = `
                <div>
                    <span style="font-weight: bold; margin-right: 0.5rem;">[${s.rank}]</span>
                    <span style="color: #eee;">${s.tag}</span>
                </div>
                <span style="color: #888; font-size: 0.8rem;">${s.effect}</span>
            `;
            container.appendChild(row);
        });
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
        const stats = currentChar.stats || {};
        const isStatsGenerated = stats['Vida Máxima'] > 0;

        let message = '¿Generar estadísticas? Esto bloqueará las tiradas para este pistolero.';
        if (isStatsGenerated && window.isAdmin) {
            message = 'Este pistolero ya tiene estadísticas. ¿Deseas RE-GENERARLAS aleatoriamente? Esta acción sobreescribirá los valores actuales.';
        } else if (isStatsGenerated && !window.isAdmin) {
            return; // Safety
        }

        if (!confirm(message)) return;

        const newStats = {
            "Vida Máxima": Math.floor(Math.random() * 20) + 20,
            "Fuerza": Math.floor(Math.random() * 10) + 5,
            "Resistencia": Math.floor(Math.random() * 10) + 5,
            "Fuerza Resplandor": Math.floor(Math.random() * 10) + 1,
            "Resistencia Resplandor": Math.floor(Math.random() * 10) + 1,
            "Destreza": Math.floor(Math.random() * 10) + 5,
            "Inteligencia": Math.floor(Math.random() * 10) + 5,
            "Estado": "vivo"
        };
        newStats["Vida"] = newStats["Vida Máxima"];

        currentChar.stats = newStats;
        saveSheetData();
        renderStats();

        // Disable button only if not admin
        const btn = document.getElementById('roll-stats-btn');
        if (btn && !window.isAdmin) btn.disabled = true;
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
        if (!currentChar) return;

        // CLEAN DATA: Remove 'users' join object before sending to backend
        // to avoid database errors with unexpected payload fields
        const payload = { ...currentChar };
        delete payload.users;

        payload.description = document.getElementById('sheet-desc').value;

        try {
            const response = await fetch(`http://127.0.0.1:8000/characters/${currentChar.id}?requester_id=${user.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                alert("Hoja guardada en el Haz.");
                // Update local currentChar to reflect saved description
                currentChar.description = payload.description;
            } else {
                const err = await response.json();
                alert("Error al guardar: " + (err.detail || "Error desconocido"));
            }
        } catch (e) {
            console.error(e);
            alert("No se pudo conectar con el servidor.");
        }
    };

    // REAL SHINING MACHINE CALL
    window.openShiningMachine = async () => {
        const isShiningGenerated = currentChar.skills && currentChar.skills.length > 0;

        let message = '¿Deseas conectar a este pistolero con el Haz?';
        if (isShiningGenerated && window.isAdmin) {
            message = 'Este pistolero ya posee el Resplandor. ¿Deseas RE-GENERAR sus habilidades? Las actuales se perderán en el vacío.';
        } else if (isShiningGenerated && !window.isAdmin) {
            return; // Safety
        }

        if (!confirm(message)) return;

        const list = document.getElementById('shining-list');
        list.innerHTML = 'Conectando con el Haz...';

        try {
            const response = await fetch(`http://127.0.0.1:8000/characters/${currentChar.id}/shining?requester_id=${user.id}`, {
                method: 'POST'
            });
            const data = await response.json();

            list.innerHTML = '';

            if (!response.ok) {
                const errorMsg = data.detail || data.message || "Error desconocido en el Haz.";
                list.innerHTML = `<tr><td colspan="3" style="text-align: center; color: #f44; padding: 1rem;">ERRATAS DEL HAZ: ${errorMsg}</td></tr>`;
                document.getElementById('shining-machine-modal').style.display = 'flex';
                return;
            }

            if (data.skills && data.skills.length > 0) {
                data.skills.forEach(s => {
                    const tr = document.createElement('tr');
                    const rankClass = `rank-${s.rank.toLowerCase()}`;
                    tr.className = rankClass;
                    tr.innerHTML = `
                        <td style="padding: 0.5rem; font-weight: bold;">${s.rank}</td>
                        <td style="padding: 0.5rem;">${s.tag}</td>
                        <td style="padding: 0.5rem; color: #888;">${s.effect}</td>
                    `;
                    list.appendChild(tr);
                });

                currentChar.skills = data.skills;
                renderSkills();

                // Disable button for player, keep enabled for admin
                const btn = document.getElementById('roll-shining-btn');
                if (btn && !window.isAdmin) btn.disabled = true;
            } else {
                const finalMsg = data.message || "No se detectó el Resplandor en esta ocasión.";
                list.innerHTML = `<tr><td colspan="3" style="text-align: center; padding: 1rem;">${finalMsg}</td></tr>`;
            }

            document.getElementById('shining-machine-modal').style.display = 'flex';
        } catch (e) {
            console.error(e);
            alert("El Haz está turbulento. Intenta más tarde.");
        }
    };

});
