# DiaUp ☀️ — Inteligência Emocional & Motivação Diária

> **O aplicativo humanizado que traz sol, vitalidade e inspiração personalizada para o seu dia a dia.**
> **Status de Deploy:** 🚀 Conectado à nuvem, contínuo no **GitHub** (`pbaduaneira-lang/DiaUp`) e implantado via **Vercel Serverless Functions** + **PostgreSQL Connection Pooler**.

---

## 📖 Sobre o Projeto
O **DiaUp** é um aplicativo web interativo de inteligência emocional e motivação diária. Ele foi projetado para oferecer um acolhimento genuíno e único, combinando **Inteligência Artificial (Google Gemini 2.5 Flash)** com uma **biblioteca de mensagens curadas** pelo painel de administração.

Cada mensagem gerada ou resgatada é adaptada ao perfil do usuário (nome, idade calculada, cidade e estado), garantindo uma experiência profunda, empática e inspiradora.

---

## ✨ Principais Destaques & Funcionalidades

### 1. Identidade Visual Premium & Radiante
* **Sol Brilhando com Efeito Glow:** Ícone SVG animado (`rotateSun` de 35s), transmitindo energia constante e renovação.
* **Marca em Dobro:** O sol possui dimensões imponentes (**120px** no desktop, **92px** no mobile) e o texto **DiaUp** se destaca com tamanho de **4rem** (desktop) e **3.1rem** (mobile), posicionado sobre os raios solares com sombreado de alta proteção e gradiente coral na sílaba "Up".
* **Layout Otimizado (Foco 100% Visível):** A tela inicial foi desenhada para que todo o bloco **"Foco para o seu dia"** apareça imediatamente visível ao abrir o app, sem rolagem (scroll) no topo.

### 2. Sinergia Híbrida: Admin + Inteligência Artificial (50% / 50%)
* **Biblioteca Curada + IA:** Ao solicitar uma reflexão, o sistema alterna harmonicamente (50% de chance) entre exibir uma mensagem gravada na biblioteca do Admin e gerar uma nova mensagem exclusiva via IA.
* **Nome Sempre no Início (Regra do Vocativo):** Todas as reflexões exibidas começam obrigatoriamente com o vocativo do usuário seguido de vírgula (ex: `"Mariana, cuidar de si mesmo em Belo Horizonte..."` ou `"Carlos, acredite nos seus sonhos..."`). Isso garante proximidade imediata e neutralidade de gênero universal.
* **Mensagens Efêmeras vs Curadas:** As mensagens geradas pela IA na hora são **efêmeras** e não lotam o banco de dados. A tabela de mensagens (`messages`) armazena estritamente as reflexões limpas e curadas pelo Administrador no painel `/admin`.

### 3. 7 Categorias Oficiais do Sistema
O aplicativo é estruturado em **7 categorias temáticas principais**, além do filtro surpresa "Geral":
1. 🩺 **Saúde**
2. ❤️ **Relacionamento**
3. 🏡 **Família**
4. 💼 **Trabalho**
5. 🚀 **Projetos**
6. 💖 **Amor**
7. 💰 **Finanças**

### 4. Vida Própria: Carregamento Imediato & Renovação Automática
* **Boas-vindas Instantâneas:** Ao abrir o aplicativo, a primeira reflexão da IA é gerada e exibida automaticamente.
* **Temporizador Regressivo ao Vivo (`#renewCountdown`):** Contagem regressiva contínua (`⏳ 3:00`) que busca automaticamente uma nova reflexão ao zerar.
* **Controle de Tempo:** Intervalos personalizáveis no menu suspenso: **1 min, 3 min, 5 min, 10 min ou Pausar**.

### 5. Sucesso em Celulares: PWA (Progressive Web App) & Blindagem de Cadastro
Para resolver a perda de dados de `localStorage` comum em abas de navegadores móveis (Chrome, Safari, Instagram, WhatsApp), implementamos a arquitetura PWA com **Adicionar à Tela Inicial**:
* **Arquivos do Manifesto (`/static/manifest.json` e `/static/icon.svg`):** Configurados em modo `standalone` e tema `#FF9800`, permitindo que o usuário instale o DiaUp diretamente na tela do celular como um aplicativo nativo em 1 toque, com memória de armazenamento permanente (`localStorage` fixo e dedicado).
* **Blindagem de Cadastro (`loadProfile` em `user.js`):** Se o servidor identificar que o `userId` já possui nome cadastrado (`data.name`), o frontend valida automaticamente o perfil e bloqueia a reabertura desnecessária do modal.
* **Banner de Instalação Superior (`#pwaInstallBanner`):** Aviso flutuante e suave abaixo da barra de navegação com instruções de instalação rápida (`⋮` no Android ou `[↑]` no iPhone).
* **Card de Dica no Fundo da Tela de Cadastro (`#modalPwaCard`):** Exibido no fundo do modal de perfil (`#profileModal`), informando:
  > *"📲 **Instale o app e nunca mais preencha este cadastro!** No navegador do celular, a memória temporária pode apagar seu perfil. Para **salvar em definitivo** e acessar o DiaUp com apenas **1 toque**, clique no menu superior (**⋮** ou **[↑]**) e selecione **'Adicionar à tela inicial'**."*
* **Detecção Inteligente de Standalone:** O sistema reconhece quando o app já está rodando instalado na tela do celular (`matchMedia('(display-mode: standalone)')`) e oculta automaticamente todos os avisos de instalação.

### 6. Painel de Administração & Autenticação Protegida (`/admin`)
* **Acesso Restrito:** Autenticação via cookies com decorador `@admin_required` e tela de login exclusiva (`/admin/login`).
  * **E-mail:** `diaup@gmail.com` | **Senha:** `diaedju1016`
  * Botão **"🚪 Sair"** no topo para encerramento de sessão em tempo real.
* **Gestão e Edição de Biblioteca (`PUT /admin/messages/<id>`):** Adicione, remova e **edite** reflexões em tempo real através do **Modal de Edição Interativo (`#editModal`)**.
* **Relatório de Downloads & Cadastros (`/admin/stats`):** Modal interativo que exibe o contador real de **Downloads** do app, o total de **Usuários Cadastrados** e a tabela com os últimos usuários (Nome, Idade e Localização).

---

## 🛠️ Stack Tecnológica & Arquitetura na Nuvem
* **Backend:** Python 3, Flask (`backend/app/app.py`, `ai_engine.py`, `database.py`)
* **Servidor em Nuvem (Produção):** **Vercel Serverless Functions (`api/index.py`)** integrado via deploy contínuo do **GitHub (`main`)**.
* **Banco de Dados Híbrido:**
  * **Produção (Vercel):** Conectado automaticamente a um **PostgreSQL Connection Pooler (IPv4)** através da variável de ambiente `DATABASE_URL`.
  * **Desenvolvimento Local:** SQLite (`database/app.db`).
* **Frontend:** HTML5, CSS3 Vanilla (com design tokens, glassmorphism, animações solares e regras PWA), JavaScript puro (`user.js`, `admin.js`).
* **Inteligência Artificial:** Google GenAI SDK (`gemini-2.5-flash`) + Mecanismo de Fallback Local.

### Estrutura de Diretórios
```text
DiaUp/
├── api/
│   └── index.py            # Entry point Serverless para Vercel
├── backend/
│   ├── app/
│   │   ├── static/         # Estilos (user.css, admin.css), Scripts (user.js, admin.js) e PWA (manifest.json, icon.svg)
│   │   ├── templates/      # Templates HTML (user.html, admin.html, admin_login.html)
│   │   ├── ai_engine.py    # Motor de IA (Gemini 2.5 Flash) e Fallback Local
│   │   ├── app.py          # Rotas e controladores Flask
│   │   └── database.py     # Gerenciador de conexão SQLite / PostgreSQL (Pooler)
├── database/               # Armazenamento local SQLite (app.db)
├── .agents/                # Diretrizes arquiteturais para agentes de IA (AGENTS.md)
├── requirements.txt        # Dependências Python para Vercel
├── run.py                  # Ponto de entrada para execução local
└── test_endpoints.py       # Suíte automática de testes e validações
```

---

## 🚀 Fluxo de Deploy Contínuo (GitHub & Vercel)
O projeto está 100% automatizado e conectado em nuvem:
1. Qualquer alteração ou nova funcionalidade é versionada localmente pelo Git:
   ```bash
   git add -A
   git commit -m "feat: descricao da nova funcionalidade"
   ```
2. Ao realizar o envio para o GitHub:
   ```bash
   git push origin main
   ```
3. A **Vercel** intercepta automaticamente o *push* na branch `main`, executa a instalação das dependências de `requirements.txt`, compila os arquivos da subpasta `api/index.py` e publica a nova versão em produção em menos de 60 segundos!

---

## 🧪 Como Executar Localmente
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie o servidor de desenvolvimento:
   ```bash
   python run.py
   ```
3. Acesse no navegador:
   * **Usuário:** `http://127.0.0.1:5000/`
   * **Admin:** `http://127.0.0.1:5000/admin`
