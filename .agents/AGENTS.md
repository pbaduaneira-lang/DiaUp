# Regras e Contexto do Projeto DiaUp (AI Agent Guidelines)

O **DiaUp** é um aplicativo web interativo de inteligência emocional e motivação diária. Este arquivo define as regras arquiteturais, diretrizes visuais e comportamentos obrigatórios que qualquer agente de IA deve seguir ao analisar, dar manutenção ou expandir este projeto.

---

## 1. Identidade & Idioma
* **Nome do Projeto:** **DiaUp** (nunca referenciar como "motivational_app" na UI ou em textos voltados ao usuário).
* **Idioma:** Sempre responder, comentar código e gerar documentação em **Português Brasileiro (PT-BR)**.

---

## 2. Identidade Visual & Branding (Sol Brilhando & DiaUp Gigante)
A identidade visual do DiaUp foi projetada para ser imponente, moderna e radiante:
* **Ícone do Sol Brilhando (`.brand-logo-container` / `.sun-icon`):**
  * SVG exclusivo com gradiente solar quente (`#FFEA68` -> `#FF9800` -> `#FF5E36`), raios e efeito de brilho (`feGaussianBlur`).
  * Animação contínua e suave de rotação (`@keyframes rotateSun`, duração de 35s por volta).
  * **Dimensões:** O tamanho do contêiner deve ser mantido em **120px x 120px** no desktop e **92px x 92px** em telas móveis (`max-width: 520px` / `560px`).
* **Texto "DiaUp" em Dobro (`.brand-text`):**
  * Fonte **Outfit**, peso pesado (`850`), tamanho **4rem** (`64px`) no desktop e **3.1rem** no mobile.
  * O texto sobrepõe estrategicamente os raios do sol (`margin-left: -28px` no desktop e `-20px` no mobile).
  * **A sílaba "Dia" (`.brand-dia`):** Azul Marinho bem escuro e denso (`#031438`) com sombra suave branca (`text-shadow`) para destaque.
  * **A sílaba "Up" (`.brand-highlight`):** Gradiente vibrante em Azul Celeste Neon (`linear-gradient(135deg, #00C6FF, #0072FF)`) com filtro `drop-shadow(0 0 12px rgba(0, 198, 255, 0.5))`, garantindo alto contraste e vivacidade.

---

## 3. Layout & Aproveitamento de Tela (Foco para o seu dia 100% visível)
* **Sem Rolagem Desnecessária no Topo:** A interface foi otimizada para que a seção **"Foco para o seu dia"** (título, quadro de reflexão e botões de categoria) apareça **inteiramente visível na tela sem necessidade de scroll**.
* **Espaçamentos Compactos:** Os paddings verticais de `.app-shell`, `.topbar`, `.hero-copy` e `.message-panel` foram calibrados de forma compacta.
* **Proibido:** NUNCA reintroduzir regras como `min-height: calc(100vh - ...)` ou alinhamentos verticais centralizados que criem vazios excessivos no topo e empurrem o conteúdo principal para baixo.

---

## 4. Tipografia & Estilo
* **UI Geral (Títulos, Botões, Menus e Barras):** Fonte **Outfit**, sans-serif moderna, limpa e geométrica.
* **Mensagens e Reflexões (`blockquote`):** Fonte **Lora**, serifada, humanizada, com estilo itálico, peso médio (`500`) e espaçamento entre linhas confortável (`1.55` a `1.6`), transmitindo serenidade e acolhimento.

---

## 5. Categorias Oficiais do Sistema
O sistema é organizado rigorosamente em **7 categorias temáticas principais**, além da opção geral/surpresa:
1. **Saúde**
2. **Relacionamento**
3. **Família**
4. **Trabalho**
5. **Projetos**
6. **Amor**
7. **Finanças**
*(Qualquer nova mensagem ou filtro deve se enquadrar nessa padronização).*

---

## 6. Motor de IA & Regras de Geração de Mensagens (`ai_engine.py` / `app.py`)
O sistema de mensagens combina Inteligência Artificial (Google Gemini 2.5 Flash / Fallback Local) com a biblioteca curada pelo Admin:

### A. Regras de Busca: Prioridade do Banco de Dados + Sem Repetição Recente
* No endpoint `/user/get_message`, o sistema **busca primeiramente as mensagens salvas no Banco de Dados** (`messages` do Admin) para a categoria solicitada.
* **Filtragem de Vistas:** O sistema verifica se a mensagem do banco já foi incluída em *Mensagens que passaram por aqui* (histórico da sessão).
* **Se houver mensagem do banco ainda não exibida:** Apresenta essa mensagem do banco imediatamente.
* **Se TODAS as mensagens do banco já passaram por ali (ou banco vazio):** A IA Gemini gera uma nova reflexão inédita e altamente personalizada.

### B. Regra de Ouro: Vocativo e Nome Sempre no Início
* **TODA MENSAGEM DEVE OBRIGATORIAMENTE COMEÇAR COM O NOME DO USUÁRIO SEGUIDO DE VÍRGULA** (ex: `"Mariana, cuidar de si mesmo..."` ou `"Carlos, acredite nos seus sonhos..."`).
* O backend garante automaticamente o prefixo `"{nome}, "` caso a mensagem gerada não o possua.

### C. Diretrizes Emocionais de Conteúdo & Sem Menção a Cidade
1. **Curto e Direto:** Máximo de 3 a 4 linhas (leitura rápida em celular).
2. **Maturidade Adequada:** Adaptação de tom e vocabulário à idade do usuário.
3. **Sem Menção a Localização Geográfica:** Proibido citar cidade ou estado nas reflexões. A mensagem deve ser atemporal e universalmente acolhedora.
4. **Variabilidade Máxima:** Evitar clichês e reestruturar frases de forma criativa.

### D. Emissão Exclusiva por Clique (Sem Temporizador por Tempo)
* A renovação de mensagens ocorre **unicamente através do clique do usuário** no botão **"Nova mensagem"** ou no filtro de categorias. Não há temporizador automático regressivo.

---

## 7. Motor de Voz Neural de Estúdio & Avatar SolAura IA
* **Voz de Estúdio (`/user/tts`):** Síntese de áudio MP3 utilizando a voz neural de estúdio Francisca (`pt-BR-FranciscaNeural` via `edge-tts`), com expressividade humana, pausas de respiração naturais e tom caloroso em Português Brasileiro.
* **Avatar SolAura IA (`#avatarSpeakerBtn`):**
  * Posicionado no lado esquerdo da tela em destaque sob a frase introdutória.
  * Conta com **Lip-Sync Visualizer via Web Audio API (`AudioContext` / `AnalyserNode`)**: analisa a frequência do áudio em tempo real e movimenta a boca (`avatarMouth`) e a aura (`avatarAura`) do avatar sincronizadas à voz.

---

## 8. Painel Administrativo, Autenticação, Edição & Estatísticas (`/admin`)
* **Acesso Restrito & Autenticação (Login e Senha):**
  * Credenciais exclusivas: `diaup@gmail.com` / `diaedju1016`.
* **Biblioteca & Estatísticas:**
  * Permite ao administrador adicionar, editar (`PUT /admin/messages/<id>`) e deletar mensagens.
  * Acompanhamento de relatórios de downloads e cadastros (`/admin/stats`).

---

## 9. Arquitetura Técnica & Deploy Contínuo
* **Backend:** Python / Flask (`app.py`, `ai_engine.py`, `database.py`).
* **Suporte a `.env`:** O sistema carrega a chave `GEMINI_API_KEY` do arquivo `.env`.
* **Banco de Dados:** SQLite (`database/app.db`) local e PostgreSQL no deploy na Vercel (`api/index.py`).
* **Deploy Contínuo:** Repositório no GitHub (`pbaduaneira-lang/DiaUp`) conectado com Vercel Serverless Functions.

