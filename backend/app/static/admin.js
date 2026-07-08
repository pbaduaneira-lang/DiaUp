const form = document.getElementById("messageForm");
const contentInput = document.getElementById("content");
const categoryInput = document.getElementById("category");
const statusMessage = document.getElementById("statusMessage");
const messagesList = document.getElementById("messagesList");
const categorySummary = document.getElementById("categorySummary");
const totalMessages = document.getElementById("totalMessages");
const totalCategories = document.getElementById("totalCategories");
const refreshMessages = document.getElementById("refreshMessages");

const totalDownloads = document.getElementById("totalDownloads");
const totalRegistered = document.getElementById("totalRegistered");
const openStatsBtn = document.getElementById("openStatsBtn");
const closeStatsBtn = document.getElementById("closeStatsBtn");
const statsModal = document.getElementById("statsModal");
const modalDownloads = document.getElementById("modalDownloads");
const modalRegistered = document.getElementById("modalRegistered");
const recentUsersList = document.getElementById("recentUsersList");
const logoutBtn = document.getElementById("logoutBtn");

const editModal = document.getElementById("editModal");
const closeEditBtn = document.getElementById("closeEditBtn");
const cancelEditBtn = document.getElementById("cancelEditBtn");
const editForm = document.getElementById("editForm");
const editMessageId = document.getElementById("editMessageId");
const editContent = document.getElementById("editContent");
const editCategory = document.getElementById("editCategory");
const editStatusMessage = document.getElementById("editStatusMessage");

function escapeHTML(value) {
    return String(value || "").replace(/[&<>'"]/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;",
    }[char]));
}

function setStatus(text, type = "neutral") {
    statusMessage.textContent = text;
    statusMessage.style.color = type === "error" ? "#b9382b" : type === "success" ? "#1b7f63" : "#667085";
}

const OFFICIAL_CATEGORIES = ["Saúde", "Relacionamento", "Família", "Trabalho", "Projetos", "Amor", "Finanças"];
let currentLibraryFilter = "Todas";
let allLibraryMessages = [];

function renderMessages(data) {
    allLibraryMessages = data.messages || [];
    const categories = data.categories || {};

    totalMessages.textContent = data.total || 0;
    totalCategories.textContent = OFFICIAL_CATEGORIES.length;

    const allButtons = ["Todas", ...OFFICIAL_CATEGORIES];
    categorySummary.innerHTML = allButtons.map((cat) => {
        const count = cat === "Todas" ? allLibraryMessages.length : (categories[cat] || 0);
        const activeClass = cat === currentLibraryFilter ? "active" : "";
        return `<button type="button" class="category-chip filter-btn ${activeClass}" data-filter="${escapeHTML(cat)}">${escapeHTML(cat)}: ${count}</button>`;
    }).join("");

    filterAndDisplayMessages();
}

function filterAndDisplayMessages() {
    const filtered = currentLibraryFilter === "Todas"
        ? allLibraryMessages
        : allLibraryMessages.filter(m => (m.category || "") === currentLibraryFilter);

    if (!filtered.length) {
        messagesList.innerHTML = `<p class="empty-state">Nenhuma mensagem em "${escapeHTML(currentLibraryFilter)}".</p>`;
        return;
    }

    messagesList.innerHTML = filtered.map((item) => `
        <article class="message-row" data-id="${item.id}">
            <div>
                <div class="message-meta">
                    <span>${escapeHTML(item.category || "Saúde")}</span>
                    <span>#${item.id}</span>
                </div>
                <p>${escapeHTML(item.content)}</p>
            </div>
            <div class="row-actions">
                <button class="edit-button" type="button" data-edit="${item.id}">Editar</button>
                <button class="delete-button" type="button" data-delete="${item.id}">Remover</button>
            </div>
        </article>
    `).join("");
}

async function loadMessages() {
    messagesList.innerHTML = '<p class="empty-state">Carregando mensagens...</p>';

    try {
        const response = await fetch("/admin/messages");
        if (response.status === 401) {
            window.location.href = "/admin/login";
            return;
        }
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Nao foi possivel carregar as mensagens.");
        }

        renderMessages(data);
    } catch (error) {
        messagesList.innerHTML = `<p class="empty-state">${escapeHTML(error.message)}</p>`;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setStatus("Salvando...");

    try {
        const response = await fetch("/admin/add_message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                content: contentInput.value,
                category: categoryInput.value,
            }),
        });
        if (response.status === 401) {
            window.location.href = "/admin/login";
            return;
        }
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Erro ao adicionar mensagem.");
        }

        form.reset();
        setStatus(data.message, "success");
        await loadMessages();
    } catch (error) {
        setStatus(error.message, "error");
    }
});

messagesList.addEventListener("click", async (event) => {
    const editBtn = event.target.closest("button[data-edit]");
    if (editBtn) {
        const id = Number(editBtn.dataset.edit);
        const msg = allLibraryMessages.find(m => m.id === id);
        if (msg) {
            editMessageId.value = msg.id;
            editContent.value = msg.content;
            editCategory.value = msg.category || "Saúde";
            if (editStatusMessage) editStatusMessage.textContent = "";
            openEditModal();
        }
        return;
    }

    const button = event.target.closest("button[data-delete]");
    if (!button) return;

    const id = button.dataset.delete;
    button.disabled = true;
    button.textContent = "Removendo...";

    try {
        const response = await fetch(`/admin/messages/${id}`, { method: "DELETE" });
        if (response.status === 401) {
            window.location.href = "/admin/login";
            return;
        }
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Nao foi possivel remover.");
        }

        setStatus(data.message, "success");
        await loadMessages();
    } catch (error) {
        setStatus(error.message, "error");
        button.disabled = false;
        button.textContent = "Remover";
    }
});

if (categorySummary) {
    categorySummary.addEventListener("click", (e) => {
        const btn = e.target.closest("button[data-filter]");
        if (!btn) return;
        currentLibraryFilter = btn.dataset.filter;
        const categoriesMap = {};
        for (const m of allLibraryMessages) {
            const c = m.category || "Saúde";
            categoriesMap[c] = (categoriesMap[c] || 0) + 1;
        }
        renderMessages({ messages: allLibraryMessages, total: allLibraryMessages.length, categories: categoriesMap });
    });
}

refreshMessages.addEventListener("click", () => {
    loadMessages();
    loadStats();
});

async function loadStats() {
    try {
        const response = await fetch("/admin/stats");
        if (response.status === 401) {
            window.location.href = "/admin/login";
            return;
        }
        const data = await response.json();
        if (response.ok) {
            if (totalDownloads) totalDownloads.textContent = data.downloads || 0;
            if (totalRegistered) totalRegistered.textContent = data.registered || 0;
            if (modalDownloads) modalDownloads.textContent = data.downloads || 0;
            if (modalRegistered) modalRegistered.textContent = data.registered || 0;
            
            const users = data.recent_users || [];
            if (recentUsersList) {
                if (!users.length) {
                    recentUsersList.innerHTML = '<p class="empty-msg">Nenhum usuário cadastrado ainda.</p>';
                } else {
                    recentUsersList.innerHTML = users.map(u => `
                        <div class="user-card">
                            <strong>${escapeHTML(u.name)}</strong>
                            <span>${escapeHTML(u.city || "")} - ${escapeHTML(u.state || "")} (${escapeHTML(u.birth_date || "")})</span>
                        </div>
                    `).join("");
                }
            }
        }
    } catch (err) {
        console.error("Erro ao buscar estatísticas:", err);
    }
}

let statsModalOpenTime = 0;

function openStatsModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    statsModalOpenTime = Date.now();
    loadStats();
    if (statsModal) {
        statsModal.classList.add("is-open");
        statsModal.setAttribute("aria-hidden", "false");
    }
}

function closeStatsModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    // Proteção contra eventos de clique fantasma ou propagação rápida (típico de touch/mobile)
    if (Date.now() - statsModalOpenTime < 400) return;
    
    if (statsModal) {
        statsModal.classList.remove("is-open");
        statsModal.setAttribute("aria-hidden", "true");
    }
}

if (openStatsBtn) openStatsBtn.addEventListener("click", openStatsModal);
if (closeStatsBtn) closeStatsBtn.addEventListener("click", closeStatsModal);
if (statsModal) statsModal.addEventListener("click", (e) => {
    if (e.target === statsModal) closeStatsModal(e);
});

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/admin/logout", { method: "POST" });
            const data = await response.json();
            window.location.href = data.redirect || "/admin/login";
        } catch (e) {
            console.error("Erro ao sair:", e);
            window.location.href = "/admin/login";
        }
    });
}

loadMessages();
loadStats();

let editModalOpenTime = 0;

function openEditModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    editModalOpenTime = Date.now();
    if (editModal) {
        editModal.classList.add("is-open");
        editModal.setAttribute("aria-hidden", "false");
    }
}

function closeEditModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    if (Date.now() - editModalOpenTime < 400) return;
    
    if (editModal) {
        editModal.classList.remove("is-open");
        editModal.setAttribute("aria-hidden", "true");
    }
}

if (closeEditBtn) closeEditBtn.addEventListener("click", closeEditModal);
if (cancelEditBtn) cancelEditBtn.addEventListener("click", closeEditModal);
if (editModal) editModal.addEventListener("click", (e) => {
    if (e.target === editModal) closeEditModal(e);
});

if (editForm) {
    editForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = editMessageId.value;
        if (editStatusMessage) {
            editStatusMessage.textContent = "Salvando alterações...";
            editStatusMessage.style.color = "#667085";
        }
        
        try {
            const response = await fetch(`/admin/messages/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    content: editContent.value,
                    category: editCategory.value,
                })
            });
            if (response.status === 401) {
                window.location.href = "/admin/login";
                return;
            }
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Erro ao atualizar mensagem.");
            
            if (editStatusMessage) {
                editStatusMessage.textContent = data.message;
                editStatusMessage.style.color = "#1b7f63";
            }
            setTimeout(async () => {
                closeEditModal();
                await loadMessages();
            }, 800);
        } catch (err) {
            if (editStatusMessage) {
                editStatusMessage.textContent = err.message;
                editStatusMessage.style.color = "#b9382b";
            }
        }
    });
}
