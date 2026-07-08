# DiaUp ☀️ — Inteligência Emocional & Motivação Diária

> **O aplicativo humanizado que traz sol, vitalidade e inspiração personalizada para o seu dia a dia.**

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

### 2. Sinergia Híbrida: Admin + Inteligência Artificial
* **Biblioteca Curada + IA:** Ao solicitar uma reflexão, o sistema alterna harmonicamente (50% de chance) entre exibir uma mensagem gravada por você na biblioteca do Admin e gerar uma nova mensagem exclusiva via IA.
* **Nome Sempre no Início:** Todas as reflexões exibidas começam obrigatoriamente com o vocativo do usuário seguido de vírgula (ex: `"Mariana, cuidar de si mesmo em Belo Horizonte..."` ou `"Carlos, acredite nos seus sonhos..."`). Isso garante proximidade imediata sem riscos de erro de gênero gramatical.
* **Empatia Geográfica & Maturidade:** As reflexões levam em conta o ritmo da cidade do usuário e sua faixa etária.

### 3. 7 Categorias Oficiais
O aplicativo é estruturado nas seguintes áreas essenciais da vida:
* 🩺 **Saúde**
* ❤️ **Relacionamento**
* 🏡 **Família**
* 💼 **Trabalho**
* 🚀 **Projetos**
* 💖 **Amor**
* 💰 **Finanças**
*(Além de um botão "Geral/Surpreenda-me").*

### 4. Vida Própria: Carregamento Imediato & Renovação Automática
* **Boas-vindas Instantâneas:** Ao abrir o aplicativo, a primeira reflexão da IA é gerada e exibida automaticamente, saudando o usuário de imediato.
* **Temporizador Regressivo ao Vivo (`#renewCountdown`):** Um relógio no painel conta o tempo para a próxima renovação automática (ex: `⏳ 3:00`). Ao zerar, uma nova reflexão inspiradora é trazida na hora!
* **Controle de Tempo:** O usuário pode escolher intervalos de **1 min, 3 min, 5 min, 10 min ou Pausar**.

### 5. Painel de Administração & Autenticação Protegida (`/admin`)
* **Acesso Restrito:** Autenticação via cookies com decorador `@admin_required` e tela de login exclusiva com o Sol Brilhando e botão **"🚪 Sair"**.
  * **Login:** `diaup@gmail.com` | **Senha:** `diaedju1016`
* **Gestão e Edição de Biblioteca (`PUT /admin/messages/<id>`):** Adicione, remova e **edite** mensagens em tempo real através do novo **Modal de Edição Interativo (`#editModal`)**.
* **Relatório de Downloads & Cadastros:** Acompanhe em tempo real o contador oficial de downloads do app, o total de usuários cadastrados e visualize a lista dos últimos cadastros com detalhes de idade e localização.

---

## 🛠️ Stack Tecnológica & Estrutura
* **Backend:** Python 3, Flask
* **Banco de Dados:** SQLite (`database/app.db`)
* **Frontend:** HTML5, CSS3 Vanilla (com variáveis modernas, glassmorphism e animações CSS), JavaScript puro
* **Inteligência Artificial:** Google GenAI SDK (`gemini-2.5-flash`) com Fallback Local inteligente

### Estrutura de Diretórios
```text
motivational_app/
├── backend/
│   ├── app/
│   │   ├── static/         # Estilos (user.css, admin.css) e Scripts (user.js, admin.js)
│   │   ├── templates/      # Templates HTML (user.html, admin.html)
│   │   ├── ai_engine.py    # Motor de IA e geração de fallback
│   │   ├── app.py          # Rotas e controladores Flask
│   │   └── database.py     # Gestão e inicialização do SQLite
├── database/               # Armazenamento do banco SQLite (app.db)
├── .agents/                # Regras e contexto do projeto para agentes de IA (AGENTS.md)
├── requirements.txt        # Dependências Python
├── run.py                  # Ponto de entrada do servidor
├── test_ai_engine.py       # Testes unitários do motor de IA
└── test_endpoints.py       # Testes de integração das rotas da API
```

---

## 🚀 Como Executar o Projeto Localmente

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicie o servidor de desenvolvimento:**
   ```bash
   python run.py
   ```

3. **Acesse no navegador:**
   * **Aplicativo do Usuário:** `http://127.0.0.1:5000/`
   * **Painel Administrativo:** `http://127.0.0.1:5000/admin`

---

## 🧪 Testes e Validação
Para garantir o funcionamento correto das rotas, integração do painel admin e validação de prefixo de nome nas mensagens, execute a suíte automática de testes:
```bash
python test_endpoints.py
python test_ai_engine.py
```
