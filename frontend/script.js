const API_BASE = "http://localhost:8000";

const SCREENS = {
    auth: document.getElementById("auth-section"),
    onboarding: document.getElementById("onboarding-section"),
    upload: document.getElementById("upload-section"),
    result: document.getElementById("result-section"),
};

const loadingOverlay = document.getElementById("loading-overlay");
const stepNav = document.getElementById("step-nav");
const btnLogout = document.getElementById("btn-logout");

let arquivoSelecionado = null;
let estadoUsuario = null;
let sessaoInicializada = false;

const STORAGE_TOKEN = "medsync_token";
const STORAGE_RESULTADO = "medsync_ultimo_resultado";

// ─── API helpers ───
function getToken() {
    return localStorage.getItem(STORAGE_TOKEN) || sessionStorage.getItem(STORAGE_TOKEN);
}

function setToken(token) {
    if (token) {
        localStorage.setItem(STORAGE_TOKEN, token);
        sessionStorage.setItem(STORAGE_TOKEN, token);
    } else {
        localStorage.removeItem(STORAGE_TOKEN);
        sessionStorage.removeItem(STORAGE_TOKEN);
        sessionStorage.removeItem(STORAGE_RESULTADO);
    }
}

function salvarResultadoLocal(data) {
    try {
        sessionStorage.setItem(STORAGE_RESULTADO, JSON.stringify(data));
    } catch {
        /* quota excedida — ignora */
    }
}

function lerResultadoLocal() {
    try {
        const raw = sessionStorage.getItem(STORAGE_RESULTADO);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function escapeHtml(texto) {
    const div = document.createElement("div");
    div.textContent = texto ?? "";
    return div.innerHTML;
}

// Renderização segura de um subset de Markdown:
// - negrito: **texto**
// - itálico: *texto*
// - listas numeradas: "1. item"
// - quebras de linha / parágrafos
// Importante: sempre escapa HTML antes de inserir tags.
function renderMarkdownSafe(md) {
    const raw = (md ?? "").toString();
    const escaped = escapeHtml(raw).replace(/\r\n/g, "\n");

    const lines = escaped.split("\n");
    let html = "";
    let inOl = false;

    const closeOl = () => {
        if (inOl) {
            html += "</ol>";
            inOl = false;
        }
    };

    const formatInline = (s) => {
        // Negrito: **texto**
        let out = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
        // Itálico: *texto* (simples, evita conflito com negrito já processado)
        out = out.replace(/(^|[^*])\*(?!\s)(.+?)(?!\s)\*(?!\*)/g, "$1<em>$2</em>");
        return out;
    };

    let paragraphBuffer = [];
    const flushParagraph = () => {
        if (!paragraphBuffer.length) return;
        const content = formatInline(paragraphBuffer.join("<br>"));
        html += `<p>${content}</p>`;
        paragraphBuffer = [];
    };

    for (const line of lines) {
        const trimmed = line.trim();

        const olMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (olMatch) {
            flushParagraph();
            if (!inOl) {
                html += "<ol>";
                inOl = true;
            }
            html += `<li>${formatInline(olMatch[2])}</li>`;
            continue;
        }

        // Linha em branco fecha bloco atual
        if (!trimmed) {
            closeOl();
            flushParagraph();
            continue;
        }

        // Linha normal -> parte do parágrafo
        closeOl();
        paragraphBuffer.push(formatInline(line));
    }

    closeOl();
    flushParagraph();

    return html || "<p></p>";
}

async function apiRequest(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    let data = {};
    try {
        data = await response.json();
    } catch {
        /* resposta não-JSON */
    }

    if (!response.ok) {
        if (response.status === 401) {
            setToken(null);
        }
        const msg = data.detail || data.mensagem || "Erro na requisição.";
        const erro = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
        erro.status = response.status;
        throw erro;
    }
    return data;
}

// ─── Navegação ───
function atualizarStepNav(passoAtivo) {
    document.querySelectorAll(".step-item").forEach((el, i) => {
        const n = i + 1;
        el.classList.remove("active", "done");
        if (n < passoAtivo) el.classList.add("done");
        if (n === passoAtivo) el.classList.add("active");
    });
}

function mostrarTela(nome, passo = 1) {
    Object.values(SCREENS).forEach((sec) => {
        if (sec) sec.classList.remove("active");
    });
    const alvo = SCREENS[nome] || SCREENS.upload || SCREENS.auth;
    if (alvo) alvo.classList.add("active");
    atualizarStepNav(passo);
    btnLogout.classList.toggle("hidden", nome === "auth");
}

function trocarTabAuth(tab) {
    document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === tab));
    document.getElementById("form-login").classList.toggle("hidden", tab !== "login");
    document.getElementById("form-register").classList.toggle("hidden", tab !== "register");
    document.getElementById("login-error").textContent = "";
    document.getElementById("register-error").textContent = "";
}

// ─── Loading ───
const LOADING_STEPS = [
    { key: "extract", title: "Processando seu laudo", subtitle: "Extraindo marcadores do PDF..." },
    { key: "rag", title: "Cruzando referências", subtitle: "Consultando base médica vetorial..." },
    { key: "ai", title: "Gerando tradução", subtitle: "IA personalizando para o seu perfil..." },
];

function mostrarLoading(ativo, stepIndex = 0) {
    loadingOverlay.classList.toggle("visible", ativo);
    loadingOverlay.setAttribute("aria-hidden", !ativo);

    if (ativo && LOADING_STEPS[stepIndex]) {
        const s = LOADING_STEPS[stepIndex];
        document.getElementById("loading-title").textContent = s.title;
        document.getElementById("loading-subtitle").textContent = s.subtitle;
        document.querySelectorAll(".load-step").forEach((el, i) => {
            el.classList.remove("active", "done");
            if (i < stepIndex) el.classList.add("done");
            if (i === stepIndex) el.classList.add("active");
        });
    }
}

function animarLoadingDuranteUpload() {
    let i = 0;
    mostrarLoading(true, 0);
    const interval = setInterval(() => {
        i = Math.min(i + 1, LOADING_STEPS.length - 1);
        mostrarLoading(true, i);
    }, 2800);
    return () => {
        clearInterval(interval);
        mostrarLoading(false);
    };
}

// ─── Auth ───
async function processarSessao(data) {
    sessionStorage.removeItem(STORAGE_RESULTADO);
    setToken(data.token);
    estadoUsuario = data.usuario;
    if (data.tem_perfil) {
        await carregarPerfilUI();
        mostrarTela("upload", 3);
    } else {
        mostrarTela("onboarding", 2);
    }
}

async function fazerLogin(e) {
    e.preventDefault();
    const errEl = document.getElementById("login-error");
    errEl.textContent = "";
    try {
        const data = await apiRequest("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({
                email: document.getElementById("login-email").value.trim(),
                senha: document.getElementById("login-senha").value,
            }),
        });
        await processarSessao(data);
    } catch (err) {
        errEl.textContent = err.message;
    }
}

async function fazerRegistro(e) {
    e.preventDefault();
    const errEl = document.getElementById("register-error");
    errEl.textContent = "";
    try {
        const data = await apiRequest("/api/auth/registro", {
            method: "POST",
            body: JSON.stringify({
                nome: document.getElementById("reg-nome").value.trim(),
                email: document.getElementById("reg-email").value.trim(),
                senha: document.getElementById("reg-senha").value,
            }),
        });
        await processarSessao(data);
    } catch (err) {
        errEl.textContent = err.message;
    }
}

function logout() {
    setToken(null);
    estadoUsuario = null;
    arquivoSelecionado = null;
    mostrarTela("auth", 1);
    document.getElementById("form-login").reset();
    document.getElementById("form-register").reset();
}

// ─── Perfil ───
async function salvarPerfil(e) {
    e.preventDefault();
    const errEl = document.getElementById("perfil-error");
    errEl.textContent = "";
    try {
        await apiRequest("/api/perfil", {
            method: "POST",
            body: JSON.stringify({
                idade: parseInt(document.getElementById("perfil-idade").value, 10),
                genero_biologico: document.getElementById("perfil-genero").value,
                peso_kg: parseFloat(document.getElementById("perfil-peso").value),
                altura_cm: parseFloat(document.getElementById("perfil-altura").value),
                condicoes_previas: document.getElementById("perfil-condicoes").value.trim() || null,
                historico_familiar: document.getElementById("perfil-historico").value.trim() || null,
            }),
        });
        await carregarPerfilUI();
        mostrarTela("upload", 3);
    } catch (err) {
        errEl.textContent = err.message;
    }
}

async function carregarPerfilUI() {
    try {
        const data = await apiRequest("/api/auth/me");
        estadoUsuario = data.usuario;
        const nome = data.usuario?.nome?.split(" ")[0] || "usuário";
        document.getElementById("user-greeting").textContent = nome;

        const p = data.perfil;
        const badge = document.getElementById("imc-badge");
        if (p?.peso_kg && p?.altura_cm) {
            const altM = p.altura_cm / 100;
            const imc = (p.peso_kg / (altM * altM)).toFixed(1);
            badge.textContent = `IMC ${imc}`;
            badge.classList.remove("hidden");
        } else {
            badge.classList.add("hidden");
        }
    } catch {
        /* silencioso */
    }
}

// ─── Dropzone ───
function initDropzone() {
    const dropzone = document.getElementById("dropzone");
    const input = document.getElementById("pdf-file");
    const inner = document.getElementById("dropzone-inner");
    const fileLabel = document.getElementById("file-selected");
    const btnAnalisar = document.getElementById("btn-analisar");

    const setFile = (file) => {
        if (!file || file.type !== "application/pdf") {
            document.getElementById("upload-error").textContent = "Selecione um arquivo PDF válido.";
            return;
        }
        arquivoSelecionado = file;
        dropzone.classList.add("has-file");
        fileLabel.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
        fileLabel.classList.remove("hidden");
        btnAnalisar.disabled = false;
        document.getElementById("upload-error").textContent = "";
    };

    dropzone.addEventListener("click", () => input.click());
    input.addEventListener("change", () => setFile(input.files[0]));

    ["dragenter", "dragover"].forEach((ev) => {
        dropzone.addEventListener(ev, (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });
    });
    ["dragleave", "drop"].forEach((ev) => {
        dropzone.addEventListener(ev, (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (ev === "drop" && e.dataTransfer.files.length) {
                setFile(e.dataTransfer.files[0]);
            }
        });
    });
}

// ─── Upload & resultados ───
async function enviarExame() {
    if (!arquivoSelecionado) return;

    const errEl = document.getElementById("upload-error");
    errEl.textContent = "";
    const pararLoading = animarLoadingDuranteUpload();

    const formData = new FormData();
    formData.append("arquivo", arquivoSelecionado);

    try {
        const data = await apiRequest("/api/upload", { method: "POST", body: formData });
        pararLoading();
        salvarResultadoLocal(data);
        preencherResultados(data);
        mostrarTela("result", 4);
    } catch (err) {
        pararLoading();
        if (err.status === 401) {
            mostrarTela("auth", 1);
            document.getElementById("login-error").textContent =
                "Sessão expirada. Faça login novamente.";
            return;
        }
        mostrarTela("upload", 3);
        errEl.textContent = err.message;
    }
}

function preencherResultados(data) {
    const nome = data.dados_extraidos?.nome_paciente;
    document.getElementById("paciente-nome").textContent = nome || estadoUsuario?.nome || "Paciente";
    // A IA pode retornar Markdown (ex: **negrito**). Renderizamos de forma segura.
    document.getElementById("traducao-texto").innerHTML = renderMarkdownSafe(data.traducao_leiga || "");

    const grid = document.getElementById("metrics-grid");
    grid.innerHTML = "";

    const lista = data.metricas_classificadas?.length
        ? data.metricas_classificadas
        : (data.dados_extraidos?.metricas || []).map((m) => ({
              marcador: m.marcador,
              valor: m.valor,
              status: "indefinido",
          }));

    const statusLabels = {
        normal: "Dentro do esperado",
        atencao: "Requer atenção",
        indefinido: "Referência indisponível",
    };

    lista.forEach((metrica, i) => {
        const status = metrica.status || "indefinido";
        const div = document.createElement("div");
        div.className = `metric-card status-${status}`;
        div.style.animationDelay = `${i * 0.05}s`;
        div.innerHTML = `
            <div class="metric-status">${escapeHtml(statusLabels[status] || statusLabels.indefinido)}</div>
            <div class="metric-name">${escapeHtml(metrica.marcador)}</div>
            <div class="metric-value">${escapeHtml(String(metrica.valor ?? "—"))}</div>
        `;
        grid.appendChild(div);
    });
}

function novaAnalise() {
    sessionStorage.removeItem(STORAGE_RESULTADO);
    arquivoSelecionado = null;
    document.getElementById("pdf-file").value = "";
    document.getElementById("file-selected").classList.add("hidden");
    document.getElementById("dropzone").classList.remove("has-file");
    document.getElementById("btn-analisar").disabled = true;
    document.getElementById("upload-error").textContent = "";
    mostrarTela("upload", 3);
}

// ─── Boot ───
function tentarRestaurarResultadoSalvo() {
    const salvo = lerResultadoLocal();
    if (!salvo || !getToken()) return false;
    preencherResultados(salvo);
    mostrarTela("result", 4);
    return true;
}

async function restaurarSessao() {
    if (sessaoInicializada) return;
    sessaoInicializada = true;

    if (!getToken()) {
        mostrarTela("auth", 1);
        return;
    }

    if (tentarRestaurarResultadoSalvo()) {
        carregarPerfilUI();
        return;
    }

    try {
        const data = await apiRequest("/api/auth/me");
        estadoUsuario = data.usuario;
        if (data.tem_perfil) {
            await carregarPerfilUI();
            mostrarTela("upload", 3);
        } else {
            mostrarTela("onboarding", 2);
        }
    } catch {
        const salvo = lerResultadoLocal();
        if (salvo && getToken()) {
            preencherResultados(salvo);
            mostrarTela("result", 4);
            return;
        }
        setToken(null);
        mostrarTela("auth", 1);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initDropzone();
    restaurarSessao();
});

window.addEventListener("pageshow", (event) => {
    if (event.persisted && getToken() && lerResultadoLocal()) {
        tentarRestaurarResultadoSalvo();
    }
});
