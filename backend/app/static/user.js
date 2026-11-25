const getMessageBtn = document.getElementById("getMessageBtn");
const copyMessageBtn = document.getElementById("copyMessageBtn");
const btnListen = document.getElementById("btn-listen");
const shareCardBtn = document.getElementById("shareCardBtn");
const favoriteBtn = document.getElementById("favoriteBtn");
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
const pwaInstallBanner = document.getElementById("pwaInstallBanner");
const closePwaBannerBtn = document.getElementById("closePwaBannerBtn");

const streakBadge = document.getElementById("streakBadge");
const themeToggleBtn = document.getElementById("themeToggleBtn");
const diaupToast = document.getElementById("diaupToast");

// Abas de modo
const modeTabs = document.querySelectorAll(".mode-tab");
const viewMessage = document.getElementById("viewMessage");
const viewHoroscope = document.getElementById("viewHoroscope");
const viewTarot = document.getElementById("viewTarot");

// Horóscopo
const horoscopeSignBadge = document.getElementById("horoscopeSignBadge");
const horoscopeSignSelect = document.getElementById("horoscopeSignSelect");
const horoscopeElement = document.getElementById("horoscopeElement");
const horoscopeEnergy = document.getElementById("horoscopeEnergy");
const horoscopeColor = document.getElementById("horoscopeColor");
const horoscopeNumber = document.getElementById("horoscopeNumber");
const horoscopeContent = document.getElementById("horoscopeContent");
const refreshHoroscopeBtn = document.getElementById("refreshHoroscopeBtn");
const listenHoroscopeBtn = document.getElementById("listenHoroscopeBtn");
const shareHoroscopeBtn = document.getElementById("shareHoroscopeBtn");
const copyHoroscopeBtn = document.getElementById("copyHoroscopeBtn");

// Tarô 3D
const tarotBadge = document.getElementById("tarotBadge");
const tarotKeyword = document.getElementById("tarotKeyword");
const tarotDeck = document.getElementById("tarotDeck");
const tarotContent = document.getElementById("tarotContent");
const resetTarotBtn = document.getElementById("resetTarotBtn");
const listenTarotBtn = document.getElementById("listenTarotBtn");
const shareTarotBtn = document.getElementById("shareTarotBtn");
const copyTarotBtn = document.getElementById("copyTarotBtn");

// Histórico & Favoritos
const historyTabBtn = document.getElementById("historyTabBtn");
const favoritesTabBtn = document.getElementById("favoritesTabBtn");
const favoritesCountEl = document.getElementById("favoritesCount");
const historySectionTitle = document.getElementById("historySectionTitle");

// SolAura & Voz
const avatarSpeaker = document.getElementById("avatarSpeaker");
const avatarSpeakerBtn = document.getElementById("avatarSpeakerBtn");
const avatarMouth = document.getElementById("avatarMouth");
const avatarAura = document.getElementById("avatarAura");
const avatarStatusBadge = document.getElementById("avatarStatusBadge");
const voiceChips = document.querySelectorAll(".voice-chip");

// Estado da aplicação
let activeMode = "message"; // "message" | "horoscope" | "tarot"
let activeHistoryTab = "recent"; // "recent" | "favorites"
let selectedCategory = "";
let currentMessage = "";
let currentHoroscope = "";
let currentHoroscopeMeta = null;
let currentTarot = "";
let currentTarotMeta = null;
let tarotDrawn = false;
let horoscopeLoaded = false;
let history = [];
let favorites = [];
let selectedVoice = localStorage.getItem("diaup_voice") || "pt-BR-FranciscaNeural";

const CATEGORY_ICONS = {
    "Saúde": "🌿",
    "Relacionamento": "🤝",
    "Família": "🏡",
    "Trabalho": "💼",
    "Projetos": "🚀",
    "Amor": "💛",
    "Finanças": "💎",
};

let userId = localStorage.getItem("diaup_user_id");
if (!userId) {
    userId = "usr_" + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);
    localStorage.setItem("diaup_user_id", userId);
    fetch("/api/stats/download", { method: "POST" }).catch(() => {});
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

let toastTimer = null;
function showToast(msg) {
    if (!diaupToast) return;
    diaupToast.textContent = msg;
    diaupToast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        diaupToast.classList.remove("is-visible");
    }, 2400);
}

// ==========================================
// TEMA DINÂMICO (DIA / NOITE) & STREAK
// ==========================================
function applyTheme(mode) {
    const isNight = mode === "night";
    document.body.classList.toggle("theme-night", isNight);
    if (themeToggleBtn) {
        themeToggleBtn.textContent = isNight ? "☀️" : "🌙";
        themeToggleBtn.title = isNight ? "Mudar para modo Solar (Dia)" : "Mudar para modo Estrelado (Noite)";
    }
}

function initTheme() {
    const saved = localStorage.getItem("diaup_theme");
    if (saved === "day" || saved === "night") {
        applyTheme(saved);
    } else {
        const hour = new Date().getHours();
        applyTheme(hour >= 19 || hour < 6 ? "night" : "day");
    }
}

if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
        const next = document.body.classList.contains("theme-night") ? "day" : "night";
        localStorage.setItem("diaup_theme", next);
        applyTheme(next);
    });
}

function initStreak() {
    try {
        const today = new Date().toISOString().slice(0, 10);
        const lastVisit = localStorage.getItem("diaup_last_visit");
        let count = parseInt(localStorage.getItem("diaup_streak") || "0", 10) || 0;

        if (lastVisit !== today) {
            if (lastVisit) {
                const diffDays = Math.round((new Date(today) - new Date(lastVisit)) / 86400000);
                count = diffDays === 1 ? count + 1 : 1;
            } else {
                count = 1;
            }
            localStorage.setItem("diaup_last_visit", today);
            localStorage.setItem("diaup_streak", String(count));
        }

        if (streakBadge) {
            streakBadge.textContent = `🔥 ${count} ${count === 1 ? "dia" : "dias"}`;
        }
    } catch (e) {}
}

// ==========================================
// SELETOR DE VOZ NEURAL
// ==========================================
function syncVoiceUI() {
    voiceChips.forEach((chip) => {
        chip.classList.toggle("is-active", chip.dataset.voice === selectedVoice);
    });
}

voiceChips.forEach((chip) => {
    chip.addEventListener("click", () => {
        selectedVoice = chip.dataset.voice || "pt-BR-FranciscaNeural";
        localStorage.setItem("diaup_voice", selectedVoice);
        syncVoiceUI();
        stopAudioPlayback();
        showToast(`Voz selecionada: ${chip.textContent}`);
    });
});

// ==========================================
// FAVORITOS & HISTÓRICO
// ==========================================
function loadFavorites() {
    try {
        const raw = localStorage.getItem("diaup_favorites");
        favorites = raw ? JSON.parse(raw) : [];
        if (!Array.isArray(favorites)) favorites = [];
    } catch (e) {
        favorites = [];
    }
    updateFavoritesBadge();
}

function saveFavorites() {
    try {
        localStorage.setItem("diaup_favorites", JSON.stringify(favorites));
    } catch (e) {}
    updateFavoritesBadge();
}

function updateFavoritesBadge() {
    if (favoritesCountEl) favoritesCountEl.textContent = String(favorites.length);
    if (favoriteBtn) {
        const isFav = Boolean(currentMessage && favorites.some((f) => f.content === currentMessage));
        favoriteBtn.textContent = isFav ? "❤️" : "🤍";
        favoriteBtn.classList.toggle("is-favorited", isFav);
    }
}

function toggleFavoriteCurrentMessage() {
    if (!currentMessage) return;
    const idx = favorites.findIndex((f) => f.content === currentMessage);
    if (idx >= 0) {
        favorites.splice(idx, 1);
        showToast("Removida dos favoritos");
    } else {
        favorites.unshift({
            content: currentMessage,
            category: messageCategory ? messageCategory.textContent : (selectedCategory || "Geral"),
        });
        favorites = favorites.slice(0, 30);
        showToast("Salva nos favoritos ❤️");
    }
    saveFavorites();
    if (activeHistoryTab === "favorites") renderHistory();
}

if (favoriteBtn) {
    favoriteBtn.addEventListener("click", toggleFavoriteCurrentMessage);
}

function renderHistory() {
    const list = activeHistoryTab === "favorites" ? favorites : history;

    if (!list.length) {
        messageHistory.innerHTML = activeHistoryTab === "favorites"
            ? '<p class="empty-history">Toque no coração 🤍 em qualquer mensagem para guardá-la aqui.</p>'
            : '<p class="empty-history">As mensagens recebidas nesta sessao aparecem aqui.</p>';
        return;
    }

    messageHistory.innerHTML = list.slice(0, 6).map((item, idx) => `
        <article class="history-item">
            <div class="history-item-head">
                <strong>${escapeHTML(item.category)}</strong>
                ${activeHistoryTab === "favorites" ? `<button type="button" class="history-remove-btn" data-remove-fav="${idx}" title="Remover dos favoritos">✕</button>` : ""}
            </div>
            <span>${escapeHTML(item.content)}</span>
        </article>
    `).join("");
}

if (messageHistory) {
    messageHistory.addEventListener("click", (event) => {
        const btn = event.target.closest("button[data-remove-fav]");
        if (!btn) return;
        const idx = parseInt(btn.dataset.removeFav, 10);
        if (!Number.isNaN(idx)) {
            favorites.splice(idx, 1);
            saveFavorites();
            renderHistory();
        }
    });
}

if (historyTabBtn && favoritesTabBtn) {
    historyTabBtn.addEventListener("click", () => {
        activeHistoryTab = "recent";
        historyTabBtn.classList.add("is-active");
        favoritesTabBtn.classList.remove("is-active");
        if (historySectionTitle) historySectionTitle.textContent = "Mensagens que passaram por aqui";
        renderHistory();
    });

    favoritesTabBtn.addEventListener("click", () => {
        activeHistoryTab = "favorites";
        favoritesTabBtn.classList.add("is-active");
        historyTabBtn.classList.remove("is-active");
        if (historySectionTitle) historySectionTitle.textContent = "Suas mensagens favoritas";
        renderHistory();
    });
}

// ==========================================
// ABAS DE MODO (MENSAGEM | HORÓSCOPO | TARÔ)
// ==========================================
function switchMode(mode) {
    activeMode = mode;
    stopAudioPlayback();

    modeTabs.forEach((tab) => {
        const isActive = tab.dataset.mode === mode;
        tab.classList.toggle("is-active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    if (viewMessage) viewMessage.hidden = mode !== "message";
    if (viewHoroscope) viewHoroscope.hidden = mode !== "horoscope";
    if (viewTarot) viewTarot.hidden = mode !== "tarot";

    if (avatarStatusBadge) {
        if (mode === "horoscope") avatarStatusBadge.textContent = "Toque para ouvir o horóscopo";
        else if (mode === "tarot") avatarStatusBadge.textContent = "Toque para ouvir seu Tarô";
        else avatarStatusBadge.textContent = "Toque para ouvir a mensagem";
    }

    if (mode === "horoscope" && !horoscopeLoaded) {
        loadHoroscope();
    }
}

modeTabs.forEach((tab) => {
    tab.addEventListener("click", () => switchMode(tab.dataset.mode));
});

// ==========================================
// MOTOR DE VOZ NEURAL & LIP-SYNC (SOLAURA)
// ==========================================
let currentAudio = null;
let audioCtx = null;
let audioAnalyser = null;
let animFrameId = null;

function getActiveTextForSpeech() {
    if (activeMode === "horoscope") return currentHoroscope;
    if (activeMode === "tarot") return currentTarot;
    return currentMessage;
}

function getActiveListenButton() {
    if (activeMode === "horoscope") return listenHoroscopeBtn;
    if (activeMode === "tarot") return listenTarotBtn;
    return btnListen;
}

function stopAudioPlayback() {
    if (currentAudio) {
        try {
            currentAudio.pause();
            currentAudio.currentTime = 0;
        } catch (e) {}
        currentAudio = null;
    }
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
    if (animFrameId) {
        cancelAnimationFrame(animFrameId);
        animFrameId = null;
    }

    [btnListen, listenHoroscopeBtn, listenTarotBtn].forEach((btn) => {
        if (btn) {
            btn.classList.remove("is-speaking");
            btn.textContent = "🔊 Ouvir";
        }
    });

    if (avatarSpeaker) avatarSpeaker.classList.remove("is-speaking");
    if (avatarSpeakerBtn) avatarSpeakerBtn.classList.remove("is-speaking");
    if (avatarMouth) avatarMouth.setAttribute("d", "M 40 57 Q 50 63 60 57");
    if (avatarAura) avatarAura.style.transform = "scale(1)";
    if (avatarStatusBadge) {
        if (activeMode === "horoscope") avatarStatusBadge.textContent = "Toque para ouvir o horóscopo";
        else if (activeMode === "tarot") avatarStatusBadge.textContent = "Toque para ouvir seu Tarô";
        else avatarStatusBadge.textContent = "Toque para ouvir a mensagem";
    }
}

function startLipSyncAnimation(audioElement) {
    try {
        if (!audioCtx) {
            const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
            if (AudioCtxClass) audioCtx = new AudioCtxClass();
        }
        if (audioCtx && audioCtx.state === "suspended") {
            audioCtx.resume();
        }

        if (audioCtx) {
            const source = audioCtx.createMediaElementSource(audioElement);
            audioAnalyser = audioCtx.createAnalyser();
            audioAnalyser.fftSize = 64;
            source.connect(audioAnalyser);
            audioAnalyser.connect(audioCtx.destination);

            const dataArray = new Uint8Array(audioAnalyser.frequencyBinCount);

            function animateFrame() {
                if (!currentAudio || currentAudio.paused) return;

                audioAnalyser.getByteFrequencyData(dataArray);
                let sum = 0;
                for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
                const average = sum / dataArray.length;
                const vol = Math.min(1, average / 110);

                const mouthOpening = 61 + vol * 18;
                const mouthWidth = 40 - vol * 2;
                const mouthEnd = 60 + vol * 2;
                if (avatarMouth) {
                    avatarMouth.setAttribute("d", `M ${mouthWidth} 57 Q 50 ${mouthOpening} ${mouthEnd} 57`);
                }
                if (avatarAura) {
                    avatarAura.style.transform = `scale(${1 + vol * 0.22})`;
                }

                animFrameId = requestAnimationFrame(animateFrame);
            }

            animateFrame();
        }
    } catch (e) {
        console.log("[DiaUp LipSync]", e);
    }
}

async function speakActiveContent() {
    const textToSpeak = getActiveTextForSpeech();
    if (!textToSpeak) {
        if (activeMode === "tarot") showToast("Escolha uma carta de Tarô primeiro 🔮");
        return;
    }

    if ((currentAudio && !currentAudio.paused) || (window.speechSynthesis && window.speechSynthesis.speaking)) {
        stopAudioPlayback();
        return;
    }

    stopAudioPlayback();

    const activeBtn = getActiveListenButton();
    if (activeBtn) activeBtn.textContent = "⏳ Voz...";
    if (avatarStatusBadge) avatarStatusBadge.textContent = "Preparando voz...";

    try {
        const res = await fetch(`/user/tts?text=${encodeURIComponent(textToSpeak)}&voice=${encodeURIComponent(selectedVoice)}`);
        if (!res.ok) throw new Error("Erro no TTS backend");

        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);

        const audio = new Audio(audioUrl);
        currentAudio = audio;

        audio.onplay = () => {
            if (activeBtn) {
                activeBtn.classList.add("is-speaking");
                activeBtn.textContent = "⏹️ Parar";
            }
            if (avatarSpeaker) avatarSpeaker.classList.add("is-speaking");
            if (avatarSpeakerBtn) avatarSpeakerBtn.classList.add("is-speaking");
            if (avatarStatusBadge) avatarStatusBadge.textContent = "Recitando agora 🔊";
            startLipSyncAnimation(audio);
        };

        audio.onended = () => {
            stopAudioPlayback();
            URL.revokeObjectURL(audioUrl);
        };

        audio.onerror = () => {
            stopAudioPlayback();
            fallbackWebSpeech(textToSpeak);
        };

        await audio.play();
    } catch (err) {
        console.warn("[DiaUp TTS] Usando fallback local Web Speech:", err);
        fallbackWebSpeech(textToSpeak);
    }
}

function fallbackWebSpeech(textToSpeak) {
    if (!("speechSynthesis" in window) || !textToSpeak) {
        stopAudioPlayback();
        return;
    }

    const activeBtn = getActiveListenButton();
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = "pt-BR";
    utterance.rate = 0.95;

    utterance.onstart = () => {
        if (activeBtn) {
            activeBtn.classList.add("is-speaking");
            activeBtn.textContent = "⏹️ Parar";
        }
        if (avatarSpeaker) avatarSpeaker.classList.add("is-speaking");
        if (avatarSpeakerBtn) avatarSpeakerBtn.classList.add("is-speaking");
        if (avatarStatusBadge) avatarStatusBadge.textContent = "Recitando agora 🔊";
    };

    utterance.onend = stopAudioPlayback;
    utterance.onerror = stopAudioPlayback;

    window.speechSynthesis.speak(utterance);
}

// ==========================================
// CATEGORIAS & MENSAGENS MOTIVACIONAIS
// ==========================================
function setLoading(isLoading) {
    getMessageBtn.disabled = isLoading;
    getMessageBtn.textContent = isLoading ? "✨ Gerando com IA..." : "Nova mensagem";
}

function renderCategories(categories) {
    const items = categories.map((item) => ({ ...item, label: item.name }));

    if (!selectedCategory && items.length > 0) {
        selectedCategory = items[0].name;
    }

    categoryFilters.innerHTML = items.map((item) => {
        const icon = CATEGORY_ICONS[item.name] || "✨";
        return `
            <button class="filter-button ${item.name === selectedCategory ? "is-active" : ""}" type="button" data-category="${escapeHTML(item.name)}">
                ${icon} ${escapeHTML(item.label)}
            </button>
        `;
    }).join("");
}

async function loadCategories() {
    const fallbackCats = [
        { name: "Saúde" },
        { name: "Relacionamento" },
        { name: "Família" },
        { name: "Trabalho" },
        { name: "Projetos" },
        { name: "Amor" },
        { name: "Finanças" }
    ];
    try {
        const response = await fetch("/user/categories");
        const data = await response.json();
        renderCategories(data.categories || fallbackCats);
        getMessage();
    } catch (error) {
        renderCategories(fallbackCats);
        getMessage();
    }
}

async function getMessage() {
    stopAudioPlayback();

    setLoading(true);
    messageContent.classList.add("is-updating");
    messageContent.textContent = "✨ IA conectando-se ao seu momento...";
    messageCategory.textContent = selectedCategory || "Surpresa";
    messageDate.textContent = "Agora";

    const seenList = history.map((item) => item.content);

    const queryParams = new URLSearchParams({
        category: selectedCategory || "",
        user_id: userId,
        name: profileName ? profileName.value : "",
        birth_date: profileBirth ? profileBirth.value : "",
        city: profileCity ? profileCity.value : "",
        state: profileState ? profileState.value : "",
        seen: JSON.stringify(seenList)
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

        history = [{ content: data.content, category: data.category || "Geral" }, ...history].slice(0, 12);
        updateFavoritesBadge();
        if (activeHistoryTab === "recent") renderHistory();
    } catch (error) {
        currentMessage = "";
        messageContent.textContent = error.message;
        messageCategory.textContent = "Sem mensagem";
        messageDate.textContent = "Tente novamente";
    } finally {
        messageContent.classList.remove("is-updating");
        setLoading(false);
    }
}

// ==========================================
// HORÓSCOPO DIÁRIO
// ==========================================
async function loadHoroscope() {
    stopAudioPlayback();
    if (refreshHoroscopeBtn) {
        refreshHoroscopeBtn.disabled = true;
        refreshHoroscopeBtn.textContent = "✨ Consultando astros...";
    }
    if (horoscopeContent) {
        horoscopeContent.classList.add("is-updating");
        horoscopeContent.textContent = "✨ Alinhando os astros para o seu dia...";
    }

    const queryParams = new URLSearchParams({
        user_id: userId,
        name: profileName ? profileName.value : "",
        birth_date: profileBirth ? profileBirth.value : "",
        sign: horoscopeSignSelect ? horoscopeSignSelect.value : ""
    }).toString();

    try {
        const response = await fetch(`/user/horoscope?${queryParams}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Não foi possível consultar o horóscopo.");

        horoscopeLoaded = true;
        currentHoroscope = data.content;
        currentHoroscopeMeta = data;

        if (horoscopeSignBadge) horoscopeSignBadge.textContent = `${data.symbol} ${data.sign}`;
        if (horoscopeElement) horoscopeElement.textContent = `Elemento ${data.element}`;
        if (horoscopeEnergy) horoscopeEnergy.textContent = `Energia: ${data.energy}`;
        if (horoscopeColor) horoscopeColor.textContent = `🎨 ${data.lucky_color}`;
        if (horoscopeNumber) horoscopeNumber.textContent = `🍀 Nº ${data.lucky_number}`;
        if (horoscopeContent) horoscopeContent.textContent = data.content;
    } catch (err) {
        if (horoscopeContent) horoscopeContent.textContent = err.message;
    } finally {
        if (horoscopeContent) horoscopeContent.classList.remove("is-updating");
        if (refreshHoroscopeBtn) {
            refreshHoroscopeBtn.disabled = false;
            refreshHoroscopeBtn.textContent = "✨ Atualizar Horóscopo";
        }
    }
}

if (refreshHoroscopeBtn) refreshHoroscopeBtn.addEventListener("click", loadHoroscope);
if (horoscopeSignSelect) horoscopeSignSelect.addEventListener("change", loadHoroscope);

// ==========================================
// TARÔ DO DIA (ANIMAÇÃO 3D)
// ==========================================
function resetTarotDeck() {
    stopAudioPlayback();
    tarotDrawn = false;
    currentTarot = "";
    currentTarotMeta = null;

    if (tarotBadge) tarotBadge.textContent = "🔮 Escolha 1 carta";
    if (tarotKeyword) tarotKeyword.textContent = "Arcanos Maiores";
    if (tarotContent) {
        tarotContent.textContent = "Respire fundo, pense no seu dia e toque em uma das 3 cartas acima para revelar seu Arcano.";
    }

    if (tarotDeck) {
        tarotDeck.querySelectorAll(".tarot-card-slot").forEach((slot) => {
            slot.classList.remove("is-flipped", "is-dimmed");
        });
    }
}

async function drawTarotCard(clickedSlot) {
    if (tarotDrawn) return;
    tarotDrawn = true;
    stopAudioPlayback();

    const slots = tarotDeck ? Array.from(tarotDeck.querySelectorAll(".tarot-card-slot")) : [];
    slots.forEach((s) => {
        if (s !== clickedSlot) s.classList.add("is-dimmed");
    });

    if (tarotContent) {
        tarotContent.classList.add("is-updating");
        tarotContent.textContent = "🔮 Revelando seu Arcano e interpretando com IA...";
    }

    const queryParams = new URLSearchParams({
        user_id: userId,
        name: profileName ? profileName.value : "",
        birth_date: profileBirth ? profileBirth.value : "",
    }).toString();

    try {
        const response = await fetch(`/user/tarot?${queryParams}`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Não foi possível revelar a carta.");

        currentTarot = data.content;
        currentTarotMeta = data;

        const romanEl = clickedSlot.querySelector(".tarot-roman");
        const symbolEl = clickedSlot.querySelector(".tarot-symbol");
        const nameEl = clickedSlot.querySelector(".tarot-name");
        if (romanEl) romanEl.textContent = data.roman;
        if (symbolEl) symbolEl.textContent = data.symbol;
        if (nameEl) nameEl.textContent = data.card_name;

        clickedSlot.classList.add("is-flipped");

        if (tarotBadge) tarotBadge.textContent = `${data.symbol} ${data.card_name}`;
        if (tarotKeyword) tarotKeyword.textContent = data.keyword;
        if (tarotContent) tarotContent.textContent = data.content;
    } catch (err) {
        tarotDrawn = false;
        if (tarotContent) tarotContent.textContent = err.message;
        slots.forEach((s) => s.classList.remove("is-dimmed"));
    } finally {
        if (tarotContent) tarotContent.classList.remove("is-updating");
    }
}

if (tarotDeck) {
    tarotDeck.addEventListener("click", (event) => {
        const slot = event.target.closest(".tarot-card-slot");
        if (!slot) return;
        drawTarotCard(slot);
    });
}
if (resetTarotBtn) resetTarotBtn.addEventListener("click", resetTarotDeck);

// ==========================================
// GERADOR DE CARD COMPARTILHÁVEL (CANVAS PNG)
// ==========================================
function wrapCanvasText(ctx, text, maxWidth) {
    const words = String(text || "").split(/\s+/);
    const lines = [];
    let currentLine = "";

    for (const word of words) {
        const testLine = currentLine ? `${currentLine} ${word}` : word;
        if (ctx.measureText(testLine).width > maxWidth && currentLine) {
            lines.push(currentLine);
            currentLine = word;
        } else {
            currentLine = testLine;
        }
    }
    if (currentLine) lines.push(currentLine);
    return lines;
}

async function generateAndShareCard(tagLabel, textContent) {
    if (!textContent) {
        showToast("Gere uma mensagem primeiro ✨");
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = 1080;
    canvas.height = 1350;
    const ctx = canvas.getContext("2d");
    const isNight = document.body.classList.contains("theme-night");

    // Fundo gradiente solar ou noturno
    const grad = ctx.createLinearGradient(0, 0, 1080, 1350);
    if (isNight) {
        grad.addColorStop(0, "#040d21");
        grad.addColorStop(0.55, "#0d224d");
        grad.addColorStop(1, "#162d5e");
    } else {
        grad.addColorStop(0, "#fff8e7");
        grad.addColorStop(0.5, "#f5f0e8");
        grad.addColorStop(1, "#ffe4cf");
    }
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 1080, 1350);

    // Aura solar decorativa no topo
    const sunGrad = ctx.createRadialGradient(540, 210, 20, 540, 210, 240);
    sunGrad.addColorStop(0, "rgba(255, 234, 104, 0.92)");
    sunGrad.addColorStop(0.45, "rgba(255, 152, 0, 0.45)");
    sunGrad.addColorStop(1, "rgba(255, 94, 54, 0)");
    ctx.fillStyle = sunGrad;
    ctx.beginPath();
    ctx.arc(540, 210, 240, 0, Math.PI * 2);
    ctx.fill();

    // Sol central
    ctx.fillStyle = "#FF9800";
    ctx.beginPath();
    ctx.arc(540, 210, 62, 0, Math.PI * 2);
    ctx.fill();

    // Marca DiaUp
    ctx.textAlign = "center";
    ctx.font = "800 84px Outfit, sans-serif";
    ctx.fillStyle = isNight ? "#ffffff" : "#031438";
    ctx.fillText("Dia", 478, 355);
    ctx.fillStyle = "#00A8FF";
    ctx.fillText("Up", 602, 355);

    // Pílula de categoria / signo / tarô
    ctx.font = "700 32px Outfit, sans-serif";
    const pillText = (tagLabel || "Foco para o seu dia").toUpperCase();
    const pillWidth = Math.min(760, ctx.measureText(pillText).width + 72);
    ctx.fillStyle = isNight ? "rgba(0, 198, 255, 0.18)" : "rgba(27, 127, 99, 0.14)";
    ctx.beginPath();
    ctx.roundRect(540 - pillWidth / 2, 415, pillWidth, 64, 32);
    ctx.fill();
    ctx.fillStyle = isNight ? "#7dd3fc" : "#11523f";
    ctx.fillText(pillText, 540, 458);

    // Cartão central do texto
    ctx.fillStyle = isNight ? "rgba(15, 27, 51, 0.85)" : "rgba(255, 255, 255, 0.9)";
    ctx.beginPath();
    ctx.roundRect(90, 525, 900, 610, 36);
    ctx.fill();

    // Texto principal em Lora itálica
    ctx.fillStyle = isNight ? "#f8fafc" : "#1a2636";
    ctx.font = "italic 500 44px Lora, Georgia, serif";
    const lines = wrapCanvasText(ctx, `“${textContent}”`, 780);
    const lineHeight = 68;
    const totalHeight = lines.length * lineHeight;
    let startY = 830 - totalHeight / 2 + 24;
    lines.slice(0, 8).forEach((line) => {
        ctx.fillText(line, 540, startY);
        startY += lineHeight;
    });

    // Rodapé
    ctx.font = "600 28px Outfit, sans-serif";
    ctx.fillStyle = isNight ? "rgba(226, 232, 240, 0.72)" : "rgba(24, 33, 47, 0.58)";
    ctx.fillText("Inteligência Emocional & Motivação Diária • DiaUp", 540, 1245);

    canvas.toBlob(async (blob) => {
        if (!blob) return;
        const file = new File([blob], "diaup-card.png", { type: "image/png" });

        if (navigator.canShare && navigator.canShare({ files: [file] })) {
            try {
                await navigator.share({
                    title: "DiaUp",
                    text: textContent,
                    files: [file],
                });
                showToast("Card compartilhado ✨");
                return;
            } catch (e) {}
        }

        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "diaup-card.png";
        link.click();
        URL.revokeObjectURL(url);
        showToast("Card salvo! Pronto para postar 🖼️");
    }, "image/png");
}

// ==========================================
// EVENTOS DE AÇÃO (COPIAR, OUVIR, CARD)
// ==========================================
async function copyText(text, btn) {
    if (!text) return;
    try {
        await navigator.clipboard.writeText(text);
        const prev = btn.textContent;
        btn.textContent = "Copiado ✓";
        showToast("Texto copiado!");
        setTimeout(() => { btn.textContent = prev; }, 1400);
    } catch (error) {
        showToast("Não foi possível copiar");
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
copyMessageBtn.addEventListener("click", () => copyText(currentMessage, copyMessageBtn));
if (shareCardBtn) {
    shareCardBtn.addEventListener("click", () => generateAndShareCard(messageCategory ? messageCategory.textContent : "DiaUp", currentMessage));
}

if (copyHoroscopeBtn) copyHoroscopeBtn.addEventListener("click", () => copyText(currentHoroscope, copyHoroscopeBtn));
if (shareHoroscopeBtn) {
    shareHoroscopeBtn.addEventListener("click", () => {
        const label = currentHoroscopeMeta ? `Horóscopo • ${currentHoroscopeMeta.sign}` : "Horóscopo DiaUp";
        generateAndShareCard(label, currentHoroscope);
    });
}

if (copyTarotBtn) copyTarotBtn.addEventListener("click", () => copyText(currentTarot, copyTarotBtn));
if (shareTarotBtn) {
    shareTarotBtn.addEventListener("click", () => {
        const label = currentTarotMeta ? `Tarô • ${currentTarotMeta.card_name}` : "Tarô DiaUp";
        generateAndShareCard(label, currentTarot);
    });
}

if (btnListen) btnListen.addEventListener("click", speakActiveContent);
if (listenHoroscopeBtn) listenHoroscopeBtn.addEventListener("click", speakActiveContent);
if (listenTarotBtn) listenTarotBtn.addEventListener("click", speakActiveContent);
if (avatarSpeakerBtn) avatarSpeakerBtn.addEventListener("click", speakActiveContent);

// ==========================================
// MODAL DE PERFIL & PWA
// ==========================================
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

    const modalPwaCard = document.getElementById("modalPwaCard");
    if (modalPwaCard) {
        const isStandalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
        modalPwaCard.style.display = isStandalone ? "none" : "block";
    }
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
            const hasValidName = data.name && data.name !== "Viajante" && data.name.trim() !== "";
            if (!data.is_new && hasValidName) {
                profileName.value = data.name || "";
                profileBirth.value = data.birth_date || "";
                profileCity.value = data.city || "";
                profileState.value = data.state || "";
                localStorage.setItem("diaup_profile_saved", "true");
                checkAndShowPwaBanner();
            } else if (!localStorage.getItem("diaup_profile_saved")) {
                profileName.value = "";
                profileBirth.value = "";
                profileCity.value = "";
                profileState.value = "";
                setTimeout(openModal, 400);
            } else {
                profileName.value = data.name || "";
                profileBirth.value = data.birth_date || "";
                profileCity.value = data.city || "";
                profileState.value = data.state || "";
                checkAndShowPwaBanner();
            }
        }
    } catch (error) {
        console.error("Erro ao carregar perfil:", error);
        if (!localStorage.getItem("diaup_profile_saved")) {
            profileName.value = "";
            profileBirth.value = "";
            profileCity.value = "";
            profileState.value = "";
            setTimeout(openModal, 400);
        } else {
            checkAndShowPwaBanner();
        }
    }
}

function checkAndShowPwaBanner() {
    if (!pwaInstallBanner) return;
    const isStandalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
    if (isStandalone || localStorage.getItem("diaup_pwa_banner_dismissed")) {
        pwaInstallBanner.style.display = "none";
        return;
    }
    pwaInstallBanner.style.display = "flex";
}

if (closePwaBannerBtn) {
    closePwaBannerBtn.addEventListener("click", () => {
        if (pwaInstallBanner) pwaInstallBanner.style.display = "none";
        localStorage.setItem("diaup_pwa_banner_dismissed", "true");
    });
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
        localStorage.setItem("diaup_profile_saved", "true");
        horoscopeLoaded = false;

        setTimeout(() => {
            closeModal();
            if (activeMode === "horoscope") loadHoroscope();
            else getMessage();
            checkAndShowPwaBanner();
        }, 1200);
    } catch (error) {
        profileStatus.textContent = error.message;
        profileStatus.style.color = "#ef6f61";
    }
});

// Inicialização
initTheme();
initStreak();
syncVoiceUI();
loadFavorites();
loadCategories();
renderHistory();
loadProfile();
