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
  * Protegido por um intenso sombreado luminoso branco (`text-shadow`) para garantir leitura perfeita sobre o SVG do sol.
  * A sílaba **"Up"** (`.brand-highlight`) possui gradiente coral/laranja em sincronia com o sol.

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

### A. Sinergia Admin + IA
* No endpoint `/user/get_message`, o sistema busca mensagens salvas pelo Admin na tabela SQLite `messages` para a categoria solicitada (ou 'Geral').
* Se existirem mensagens gravadas no Admin, há **50% de chance** de exibir uma mensagem curada do Admin e **50% de chance** de gerar uma nova reflexão via IA.

### B. Regra de Ouro: Vocativo e Nome Sempre no Início
* **TODA MENSAGEM (IA, Fallback ou Admin) DEVE OBRIGATORIAMENTE COMEÇAR COM O NOME DO USUÁRIO SEGUIDO DE VÍRGULA** (ex: `"Mariana, cuidar de si mesmo em Belo Horizonte..."` ou `"Carlos, acredite nos seus sonhos..."`).
* **Motivo:** O banco de dados (`user_profile`) não armazena gênero. Iniciar diretamente com o nome e vírgula é universal, elegante, neutro e evita erros gramaticais ou de adivinhação de gênero (nunca usar "Querido/Querida").
* **Garantia no Código (`app.py`):** Se a mensagem gerada ou resgatada não iniciar com o nome do usuário, o backend aplica automaticamente o prefixo `"{nome}, "` e ajusta a capitalização da primeira palavra (respeitando nomes próprios, siglas e palavras como "Deus", "Jesus", "Brasil", "DiaUp").

### C. Diretrizes Emocionais de Conteúdo
1. **Curto e Direto:** Máximo de 3 a 4 linhas, ideal para leitura rápida no celular.
2. **Maturidade Adequada:** Adaptação de tom e vocabulário à idade calculada do usuário.
3. **Toque de Empatia Local:** Citar de forma sutil e natural a cidade/estado do usuário.
4. **Variabilidade Máxima:** Evitar clichês e reestruturar frases de forma criativa.

### D. Carregamento Imediato & Renovação Automática por Temporizador
* **Sem Tela Parada ao Abrir:** O aplicativo carrega e exibe automaticamente a primeira mensagem da IA ao ser aberto, saudando o usuário instantaneamente sem exigir cliques iniciais.
* **Temporizador de Inspiração Contínua (`#renewCountdown` / `#autoRenewSelect`):**
  * O painel de reflexão conta com um temporizador regressivo ao vivo (ex: `⏳ 3:00`, `2:59`...) que busca uma nova mensagem automaticamente ao zerar o ciclo.
  * O usuário tem controle total do intervalo no menu suspenso: **1 min, 3 min, 5 min, 10 min ou Pausar**.

---

## 7. Painel Administrativo, Autenticação, Edição & Estatísticas (`/admin`)
* **Acesso Restrito & Autenticação (Login e Senha):**
  * O acesso ao painel de administração (`/admin`) e a todos os seus endpoints de API (`/admin/add_message`, `/admin/messages`, `/admin/messages/<id>`, `/admin/stats`) é **rigorosamente protegido** por sessão via cookies e exige login prévio.
  * **Credenciais Exclusivas Oficiais (Fixas):**
    * **E-mail (Login):** `diaup@gmail.com`
    * **Senha:** `diaedju1016`
  * O controle é feito através do decorador `@admin_required` no backend (`app.py`). Requisições não autenticadas em rotas de páginas são redirecionadas para `/admin/login`, e em rotas de API recebem status `401 Unauthorized`.
  * O painel conta com o botão **"🚪 Sair"** no topo para encerrar a sessão imediatamente e retornar à tela de login.
* **Biblioteca de Mensagens & Edição Interativa:**
  * Permite ao administrador logado adicionar novas reflexões personalizadas e remover mensagens existentes.
  * **Edição de Mensagens (`PUT /admin/messages/<id>`):** Ao clicar no botão **"Editar"** ao lado de qualquer mensagem na biblioteca, um modal interativo (`#editModal`) se abre, permitindo alterar o texto e reclassificar a categoria em tempo real sem perder o foco ou precisar recriar o item.
* **Acompanhamento de Métricas (`/admin/stats`):**
  * O botão **"Relatório de Downloads & Cadastros"** abre um modal interativo no próprio painel.
  * Apresenta o contador real de **Downloads** (registrados via `/api/stats/download`), total de **Usuários Cadastrados** na tabela `user_profile` e a lista dos últimos usuários cadastrados (com nome, idade e localização).

---

## 8. Arquitetura Técnica & Banco de Dados
* **Backend:** Python / Flask (`backend/app/app.py`, `ai_engine.py`, `database.py`).
* **Banco de Dados:** SQLite (`database/app.db`).
* **Tabelas Principais:**
  * `messages`: Armazena mensagens curadas da biblioteca do Admin (`id`, `content`, `category`, `created_at`).
  * `user_profile`: Armazena perfil do usuário (`id`, `user_id`, `name`, `birth_date`, `city`, `state`).
  * `app_stats`: Registra contagens gerais como downloads (`stat_key`, `stat_value`).
* **Testes:** Sempre validar alterações executando a suíte de testes com `python test_endpoints.py` no terminal.
