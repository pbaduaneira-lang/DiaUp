const getMessageBtn = document.getElementById("getMessageBtn");
const copyMessageBtn = document.getElementById("copyMessageBtn");
const btnListen = document.getElementById("btn-listen");
const messageContent = document.getElementById("messageContent");
const messageCategory = document.getElementById("messageCategory");
const messageDate = document.getElementById("messageDate");
const categoryFilters = document.getElementById("categoryFilters");
const messageHistory = document.getElementById("messageHistory");

const openProfileBtn = document.getElementById("openProfileBtn");
const closeProfileBtn = document.getElementById("closeProfileBtn");
const profileModal = document.getElementById("profileModal");
const profileForm = document.getElementById("profileForm");
const profileName = document.getElementById("profileName");
const profileBirth = document.getElementById("profileBirth");
const profileCity = document.getElementById("profileCity");
const profileState = document.getElementById("profileState");
const profileStatus = document.getElementById("profileStatus");

const renewCountdown = document.getElementById("renewCountdown");
const autoRenewSelect = document.getElementById("autoRenewSelect");

let selectedCategory = "";
let currentMessage = "";
let history = [];
let renewInterval = 180; // 3 minutos por padrão
let currentCountdown = 180;
let timerId = null;

let userId = localStorage.getItem("diaup_user_id");
if (!userId) {
    userId = "usr_" + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
    localStorage.setItem("diaup_user_id", userId);
    fetch("/api/stats/download", { method: "POST" }).catch(() => {});
}

function startRenewTimer() {
    if (timerId) clearInterval(timerId);
    if (renewInterval <= 0) {
        if (renewCountdown) renewCountdown.textContent = "Pausado";
        return;
    }
    currentCountdown = renewInterval;
    updateCountdownDisplay();

    timerId = setInterval(() => {
        currentCountdown--;
        if (currentCountdown <= 0) {
            getMessage();
            currentCountdown = renewInterval;
        }
        updateCountdownDisplay();
    }, 1000);
}

function updateCountdownDisplay() {
    if (!renewCountdown) return;
    if (renewInterval <= 0) {
        renewCountdown.textContent = "Pausado";
        return;
    }
    const mins = Math.floor(currentCountdown / 60);
    const secs = currentCountdown % 60;
    renewCountdown.textContent = `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

if (autoRenewSelect) {
    autoRenewSelect.addEventListener("change", (e) => {
        renewInterval = Number(e.target.value);
        startRenewTimer();
    });
}

function escapeHTML(value) {
    return String(value || "").replace(/[&<>'"]/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&#39;",
        '"': "&quot;",
    }[char]));
}

function setLoading(isLoading) {
    getMessageBtn.disabled = isLoading;
    getMessageBtn.textContent = isLoading ? "✨ Gerando com IA..." : "Nova mensagem";
}

function renderHistory() {
    if (!history.length) {
        messageHistory.innerHTML = '<p class="empty-history">As mensagens recebidas nesta sessao aparecem aqui.</p>';
        return;
    }

    messageHistory.innerHTML = history.slice(0, 4).map((item) => `
        <article class="history-item">
            <strong>${escapeHTML(item.category)}</strong>
            <span>${escapeHTML(item.content)}</span>
        </article>
    `).join("");
}

function renderCategories(categories) {
    const items = categories.map((item) => ({ ...item, label: item.name }));

    if (!selectedCategory && items.length > 0) {
        selectedCategory = items[0].name;
    }

    categoryFilters.innerHTML = items.map((item) => `
        <button class="filter-button ${item.name === selectedCategory ? "is-active" : ""}" type="button" data-category="${escapeHTML(item.name)}">
            ${escapeHTML(item.label)}
        </button>
    `).join("");
}

async function loadCategories() {
    try {
        const response = await fetch("/user/categories");
        const data = await response.json();
        renderCategories(data.categories || []);
        // Carrega a primeira mensagem automaticamente e inicia a renovação inteligente
        getMessage();
        startRenewTimer();
    } catch (error) {
        categoryFilters.innerHTML = "";
    }
}

async function getMessage() {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        if (btnListen) {
            btnListen.classList.remove("is-speaking");
            btnListen.textContent = "🔊 Ouvir Mensagem";
        }
    }

    setLoading(true);
    messageContent.textContent = "✨ IA conectando-se ao seu momento...";
    messageCategory.textContent = selectedCategory || "Surpresa";
    messageDate.textContent = "Agora";
    
    // Reinicia a contagem regressiva sempre que uma nova mensagem começa a ser buscada
    currentCountdown = renewInterval;
    updateCountdownDisplay();

    const queryParams = new URLSearchParams({
        category: selectedCategory || "",
        user_id: userId,
        name: profileName ? profileName.value : "",
        birth_date: profileBirth ? profileBirth.value : "",
        city: profileCity ? profileCity.value : "",
        state: profileState ? profileState.value : ""
    }).toString();

    try {
        const response = await fetch(`/user/get_message?${queryParams}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Nao foi possivel carregar uma mensagem.");
        }

        currentMessage = data.content;
        messageContent.textContent = data.content;
        messageCategory.textContent = data.category || "Geral";
        messageDate.textContent = "Recebida agora";

        history = [{ content: data.content, category: data.category || "Geral" }, ...history].slice(0, 6);
        renderHistory();
    } catch (error) {
        currentMessage = "";
        messageContent.textContent = error.message;
        messageCategory.textContent = "Sem mensagem";
        messageDate.textContent = "Tente novamente";
    } finally {
        setLoading(false);
    }
}

categoryFilters.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-category]");
    if (!button) return;

    selectedCategory = button.dataset.category;
    categoryFilters.querySelectorAll(".filter-button").forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
    getMessage();
});

getMessageBtn.addEventListener("click", getMessage);

copyMessageBtn.addEventListener("click", async () => {
    if (!currentMessage) return;

    try {
        await navigator.clipboard.writeText(currentMessage);
        copyMessageBtn.textContent = "Copiado";
        setTimeout(() => { copyMessageBtn.textContent = "Copiar"; }, 1400);
    } catch (error) {
        copyMessageBtn.textContent = "Falhou";
        setTimeout(() => { copyMessageBtn.textContent = "Copiar"; }, 1400);
    }
});

function speakCurrentMessage() {
    if (!("speechSynthesis" in window)) {
        alert("Desculpe, o seu navegador não suporta leitura de voz.");
        return;
    }

    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        if (btnListen) {
            btnListen.classList.remove("is-speaking");
            btnListen.textContent = "🔊 Ouvir Mensagem";
        }
        return;
    }

    if (!currentMessage) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(currentMessage);
    utterance.lang = "pt-BR";
    utterance.rate = 0.95;

    utterance.onstart = () => {
        if (btnListen) {
            btnListen.classList.add("is-speaking");
            btnListen.textContent = "⏹️ Parar Leitura";
        }
    };

    const resetBtn = () => {
        if (btnListen) {
            btnListen.classList.remove("is-speaking");
            btnListen.textContent = "🔊 Ouvir Mensagem";
        }
    };

    utterance.onend = resetBtn;
    utterance.onerror = resetBtn;

    window.speechSynthesis.speak(utterance);
}

if (btnListen) {
    btnListen.addEventListener("click", speakCurrentMessage);
}

loadCategories();
renderHistory();
loadProfile();

let profileModalOpenTime = 0;

function openModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    profileModalOpenTime = Date.now();
    profileModal.classList.add("is-open");
    profileModal.setAttribute("aria-hidden", "false");
    profileStatus.textContent = "";
}

function closeModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    if (Date.now() - profileModalOpenTime < 400) return;
    
    profileModal.classList.remove("is-open");
    profileModal.setAttribute("aria-hidden", "true");
}

openProfileBtn.addEventListener("click", openModal);
closeProfileBtn.addEventListener("click", closeModal);
profileModal.addEventListener("click", (e) => {
    if (e.target === profileModal) closeModal(e);
});

async function loadProfile() {
    try {
        const response = await fetch(`/user/profile?user_id=${encodeURIComponent(userId)}`);
        const data = await response.json();
        if (response.ok) {
            profileName.value = data.name || "";
            profileBirth.value = data.birth_date || "";
            profileCity.value = data.city || "";
            profileState.value = data.state || "";
            
            if (data.name === "Viajante" && !localStorage.getItem("diaup_profile_seen")) {
                localStorage.setItem("diaup_profile_seen", "true");
                setTimeout(openModal, 800);
            }
        }
    } catch (error) {
        console.error("Erro ao carregar perfil:", error);
    }
}

profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    profileStatus.textContent = "Salvando perfil e ajustando IA...";
    profileStatus.style.color = "#697586";

    try {
        const response = await fetch("/user/profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                name: profileName.value,
                birth_date: profileBirth.value,
                city: profileCity.value,
                state: profileState.value
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || "Erro ao salvar.");
        
        profileStatus.textContent = "✓ Perfil salvo! Gerando nova mensagem...";
        profileStatus.style.color = "#1b7f63";
        
        setTimeout(() => {
            closeModal();
            getMessage();
        }, 1200);
    } catch (error) {
        profileStatus.textContent = error.message;
        profileStatus.style.color = "#ef6f61";
    }
});
