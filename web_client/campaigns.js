/* campaigns.js */

document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(localStorage.getItem('user'));

    if (!user) {
        window.location.href = 'login.html';
        return;
    }

    const campaignList = document.getElementById('campaign-list');
    const createBtn = document.getElementById('create-campaign-btn');
    const modal = document.getElementById('campaign-modal');
    const closeBtn = document.getElementById('close-modal');
    const campaignForm = document.getElementById('campaign-form');
    const logoutBtn = document.getElementById('logout-btn');
    const modalTitle = document.getElementById('modal-title');
    const editIdInput = document.getElementById('edit-campaign-id');
    const nameInput = document.getElementById('campaign-name');

    // Cargar Campañas
    async function fetchCampaigns() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${user.id}`);
            const data = await response.json();

            campaignList.innerHTML = '';

            if (data.length === 0) {
                campaignList.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #666;">No hay campañas activas en este nivel de la Torre. Crea una para comenzar.</p>';
                return;
            }

            data.forEach(campaign => {
                const isAdmin = campaign.admin_id === user.id;
                const adminName = campaign.admin ? campaign.admin.username : '???';
                const adminShort = adminName.substring(0, 5);

                const card = document.createElement('div');
                card.className = 'campaign-card';
                card.innerHTML = `
                    <h3>${campaign.name}</h3>
                    <div class="campaign-meta">
                        <span>Creada: ${new Date(campaign.created_at).toLocaleDateString()}</span><br>
                        <span>Culpable: ${adminShort}...</span>
                    </div>
                    <div class="card-actions">
                        <button class="btn btn-small" onclick="enterCampaign('${campaign.id}')">Entrar</button>
                        ${isAdmin ? `
                            <button class="btn btn-small btn-delete" onclick="openEditModal('${campaign.id}', '${campaign.name}')">Editar</button>
                            <button class="btn btn-small btn-delete" onclick="deleteCampaign('${campaign.id}')">Eliminar</button>
                        ` : `
                            <button class="btn btn-small btn-delete" style="border-color: #666;" onclick="abandonCampaign('${campaign.id}')">Abandonar</button>
                        `}
                    </div>
                `;
                campaignList.appendChild(card);
            });
        } catch (error) {
            console.error('Error fetching campaigns:', error);
            campaignList.innerHTML = '<p style="color: red;">Error al conectar con el Haz. Revisa el servidor.</p>';
        }
    }

    // Modal logic
    createBtn.onclick = () => {
        modalTitle.textContent = 'NUEVA CAMPAÑA';
        editIdInput.value = '';
        nameInput.value = '';
        modal.style.display = 'flex';
    };

    closeBtn.onclick = () => modal.style.display = 'none';

    window.onclick = (event) => {
        if (event.target == modal) modal.style.display = 'none';
    };

    // Form logic (Create/Update)
    campaignForm.onsubmit = async (e) => {
        e.preventDefault();
        const campaignId = editIdInput.value;
        const name = nameInput.value;

        const url = campaignId
            ? `http://127.0.0.1:8000/campaigns/${campaignId}`
            : 'http://127.0.0.1:8000/campaigns/';

        const method = campaignId ? 'PUT' : 'POST';
        const body = campaignId
            ? JSON.stringify({ name: name })
            : JSON.stringify({ name: name, admin_id: user.id });

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: body
            });

            if (response.ok) {
                modal.style.display = 'none';
                fetchCampaigns();
            } else {
                alert('Error al guardar la campaña');
            }
        } catch (error) {
            console.error('Error saving campaign:', error);
        }
    };

    // Global actions
    window.openEditModal = (id, name) => {
        modalTitle.textContent = 'REFORMULA TU MUNDO';
        editIdInput.value = id;
        nameInput.value = name;
        modal.style.display = 'flex';
    };

    window.deleteCampaign = async (id) => {
        if (!confirm('¿Estás seguro de que quieres borrar este mundo? Todo rastro de él desaparecerá del Haz.')) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                fetchCampaigns();
            }
        } catch (error) {
            console.error('Error deleting campaign:', error);
        }
    };

    window.enterCampaign = (id) => {
        localStorage.setItem('currentCampaign', id);
        window.location.href = 'campaign_dashboard.html'; // Redirige al panel interior de la campaña
    };

    window.abandonCampaign = async (id) => {
        if (!confirm('¿Deseas abandonar este mundo? Perderás el rastro del Haz aquí.')) return;
        try {
            const response = await fetch(`http://127.0.0.1:8000/campaigns/${id}/participants/${user.id}`, {
                method: 'DELETE'
            });
            if (response.ok) fetchCampaigns();
        } catch (e) { console.error(e); }
    };

    logoutBtn.onclick = () => {
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    };

    // Initial load
    fetchCampaigns();
});
