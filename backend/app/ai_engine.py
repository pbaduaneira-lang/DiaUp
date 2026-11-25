import os
import random
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def parse_birth_date(birth_date_str):
    """Faz o parse flexível de data de nascimento em formato brasileiro (DD/MM/AAAA), ISO (AAAA-MM-DD) ou apenas ano (AAAA)."""
    if not birth_date_str:
        return None
    raw = str(birth_date_str).strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw[:10], fmt)
        except Exception:
            continue
    if len(raw) == 4 and raw.isdigit():
        try:
            return datetime(int(raw), 1, 1)
        except Exception:
            return None
    return None


def normalize_birth_date(birth_date_str):
    """Normaliza qualquer formato aceito de data para YYYY-MM-DD (compatível com PostgreSQL e SQLite)."""
    dt = parse_birth_date(birth_date_str)
    if dt:
        return dt.strftime("%Y-%m-%d")
    return str(birth_date_str or "").strip()


def calculate_age(birth_date_str):
    if not birth_date_str:
        return 28
    try:
        raw = str(birth_date_str).strip()
        if len(raw) == 4 and raw.isdigit():
            age = datetime.today().year - int(raw)
            return max(10, min(120, age))
        birth_date = parse_birth_date(raw)
        if birth_date:
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return max(10, min(120, age))
    except Exception:
        pass
    return 28

def generate_fallback_message(name, age, category):
    """
    Mecanismo de fallback inteligente caso a chave do Gemini não esteja configurada ou haja sem internet.
    Garante que a mensagem cumpra todas as diretrizes emocionais do DiaUp localmente sem citar cidade.
    """
    nome_clean = name or "amigo(a)"
    cat = (category or "Geral").capitalize()

    templates = {
        "Saúde": [
            f"{nome_clean}, cuidar de si mesmo é o primeiro e mais importante passo para qualquer conquista. Aos {age} anos, você entende que sua vitalidade física e mental é o seu maior patrimônio. Ouça o seu corpo hoje, respeite seus limites e celebre cada escolha que nutre o seu bem-estar.",
            f"{nome_clean}, a correria diária não pode nos fazer esquecer de quem nos mantém de pé: nós mesmos. Com a sabedoria dos seus {age} anos, lembre-se de que o descanso e o cuidado com a saúde não são perda de tempo, mas renovação de energia. Respire fundo e dê a si mesmo o amor que você merece."
        ],
        "Projetos": [
            f"{nome_clean}, tirar ideias do papel exige coragem e visão, qualidades que você tem de sobra. Aos {age} anos, cada projeto iniciado é uma manifestação do seu propósito e da sua vontade de crescer. Confie no planejamento que você fez e dê mais um passo prático rumo à sua realização.",
            f"{nome_clean}, o segredo para realizar grandes projetos está em dividir o sonho em pequenas ações diárias. A maturidade dos seus {age} anos te dá a disciplina necessária para persistir mesmo quando os desafios surgem. Mantenha o entusiasmo do primeiro dia e celebre cada etapa concluída."
        ],
        "Trabalho": [
            f"{nome_clean}, o ritmo do dia a dia exige muito, mas sua trajetória profissional está sendo construída com uma solidez admirável. Aos {age} anos, cada desafio superado no trabalho não é um tropeço, e sim um degrau essencial para sua maturidade e autonomia. Confie na sua capacidade de transformar esforço em resultado hoje.",
            f"{nome_clean}, mesmo com a correria dos compromissos, é fundamental reconhecer o valor do que você entrega todos os dias. Com a experiência dos seus {age} anos, você já possui o discernimento necessário para focar no que realmente importa em sua carreira. Respire fundo e dê o próximo passo com serenidade."
        ],
        "Foco": [
            f"{nome_clean}, entre tantas distrações do mundo, sua clareza de propósito é o seu maior escudo. Aos {age} anos, direcionar sua energia para o que verdadeiramente constrói o seu futuro é um ato de sabedoria e poder pessoal. Mantenha os olhos na sua meta e permita-se avançar um passo de cada vez.",
            f"{nome_clean}, o segredo para avançar não é correr mais rápido, mas caminhar na direção certa com consistência. A bagagem dos seus {age} anos te ensina que o verdadeiro foco nasce da calma e da escolha deliberada. Feche os olhos para o ruído externo e confie no seu ritmo hoje."
        ],
        "Coragem": [
            f"{nome_clean}, é natural sentir frio na barriga diante do novo, mas sua força interna é infinitamente maior que qualquer receio. Aos {age} anos, você já superou tempestades que pareciam intermináveis e saiu mais forte de cada uma delas. Abrace a coragem que habita em você e ouse dar o salto que seu coração pede.",
            f"{nome_clean}, a verdadeira coragem não é a ausência do medo, mas a decisão firme de não deixar que ele paralise seus sonhos. Com a vivência e a maturidade dos seus {age} anos, você tem todos os recursos internos para reescrever qualquer situação. Confie na sua voz interior e siga em frente com firmeza."
        ],
        "Disciplina": [
            f"{nome_clean}, a consistência diária é o que transforma sonhos distantes em conquistas palpáveis na sua vida. Aos {age} anos, você sabe que a motivação inicia o caminho, mas é a disciplina compassiva que sustenta a jornada. Honre seu compromisso consigo mesmo hoje, celebrando cada pequena vitória no trajeto.",
            f"{nome_clean}, construir algo grandioso requer a paciência de plantar um pouco todos os dias. A maturidade dos seus {age} anos te dá a clareza de que os hábitos diários esculpem o futuro que você deseja viver. Mantenha o foco no processo e orgulhe-se da sua dedicação constante."
        ],
        "Relacionamento": [
            f"{nome_clean}, as conexões verdadeiras que cultivamos são flores que regamos com escuta, respeito e presença. Aos {age} anos, você compreende que amar e ser amado exige autenticidade e o acolhimento das imperfeições de cada um. Abra seu coração para a empatia hoje, fortalecendo os laços que trazem paz à sua vida.",
            f"{nome_clean}, construir pontes sólidas com quem amamos é um dos maiores investimentos da nossa jornada. Com a sabedoria dos seus {age} anos, lembre-se de que o diálogo sincero e o carinho diário transformam qualquer obstáculo em união. Valorize quem caminha ao seu lado e espalhe a luz que existe em você."
        ],
        "Família": [
            f"{nome_clean}, o aconchego familiar é o porto seguro que renova nossas forças para a vida. Aos {age} anos, você sabe valorizar as raízes que te sustentam e o amor incondicional que moldou quem você é hoje. Dedique um tempo para nutrir esses laços e sentir a paz que vem do lar.",
            f"{nome_clean}, em meio ao ritmo da vida, a família é o nosso lembrete constante de pertencimento e afeto verdadeiro. A maturidade dos seus {age} anos te permite enxergar a beleza nas pequenas tradições e no cuidado mútuo. Agradeça por quem faz parte da sua história e espalhe esse acolhimento."
        ],
        "Amor": [
            f"{nome_clean}, o amor que cultivamos começa pelo carinho e respeito que temos por nós mesmos. Aos {age} anos, você entende que amar é acolher a verdade do outro sem perder a própria essência. Abra seu coração para viver relações leves, francas e repletas de reciprocidade.",
            f"{nome_clean}, nos caminhos da vida, o amor é a luz que suavemente transforma qualquer rotina em significado. Com a sabedoria dos seus {age} anos, você sabe que o afeto verdadeiro floresce na presença e nos pequenos gestos diários. Permita-se amar e ser amado com toda a beleza e intensidade que você merece."
        ],
        "Finanças": [
            f"{nome_clean}, a prosperidade é construída passo a passo com organização, clareza e paciência. Aos {age} anos, cada escolha consciente que você faz com suas finanças é um investimento na sua liberdade e tranquilidade futura. Confie no seu planejamento e celebre cada meta alcançada.",
            f"{nome_clean}, lidar com finanças requer equilíbrio entre viver o presente e plantar para o futuro. Com a maturidade dos seus {age} anos, você tem o discernimento necessário para transformar seus recursos em segurança e paz de espírito. Mantenha o foco no seu crescimento e honre o valor do seu esforço."
        ],
        "Sucesso": [
            f"{nome_clean}, o verdadeiro sucesso não é apenas o topo da montanha, mas a pessoa incrível que você se torna na subida. Aos {age} anos, cada aprendizado acumulado é uma medalha silenciosa do seu valor e da sua capacidade de superação. Celebre o quanto você já caminhou e continue construindo seu legado com orgulho.",
            f"{nome_clean}, prosperar é alinhar suas conquistas externas com a sua paz de espírito interior. Com a experiência dos seus {age} anos, você entende que o sucesso autêntico é viver com propósito, integridade e alegria diária. Confie no seu potencial ilimitado para alcançar o extraordinário."
        ],
        "Geral": [
            f"{nome_clean}, a energia de hoje traz um convite especial para você renovar suas esperanças. Aos {age} anos, sua história já provou inúmeras vezes a sua incrível capacidade de se reinventar e florescer. Respire fundo, acolha o momento presente e saiba que você está exatamente onde precisa estar para evoluir.",
            f"{nome_clean}, cada amanhecer é uma página em branco pronta para receber o melhor da sua energia. Com a vivência dos seus {age} anos, você tem a sabedoria de escolher quais batalhas merecem sua atenção e onde depositar seu coração. Siga com leveza, confiando na beleza do seu caminho único."
        ]
    }

    options = templates.get(cat, templates["Geral"])
    return random.choice(options)

def generate_motivational_message(profile, category):
    """
    Gera uma mensagem de apoio usando o Google Gemini (se a API Key estiver configurada),
    ou utiliza o fallback inteligente local.
    """
    name = (profile.get("name") or "Amigo(a)").strip()
    birth_date = profile.get("birth_date")
    age = calculate_age(birth_date)
    cat = (category or "Geral").strip()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return generate_fallback_message(name, age, cat)

    prompt = f"""Você é o motor de inteligência emocional do aplicativo DiaUp. Sua missão é gerar uma mensagem curta de apoio, reflexão e motivação altamente personalizada, garantindo que o usuário sinta um acolhimento genuíno e único.


DADOS DO USUÁRIO ATUAL:
- Nome: {name}
- Idade: {age} anos
- Tema solicitado: {cat}

DIRETRIZES DE CONTEÚDO E FORMATO:
1. CURTO E DIRETO: A mensagem deve ter no máximo 3 ou 4 linhas (ideal para leitura rápida em telas de celular).
2. NOME SEMPRE NO INÍCIO: A mensagem DEVE OBRIGATORIAMENTE começar com o nome do usuário seguido de vírgula (exemplo: "{name}, ..."). Use o nome de forma acolhedora logo na primeira palavra do texto.
3. MATURIDADE ADEQUADA: Adapte a abordagem, os conselhos e o vocabulário para a idade de {age} anos. 
4. VARIABILIDADE MÁXIMA: Evite clichês e frases feitas de internet. Reestruture as frases de modo criativo para que, se o mesmo usuário pedir outra mensagem do mesmo tema, ela soe completamente diferente.

RESTRICÇÃO CRÍTICA: Retorne APENAS o texto da mensagem final. Não inclua introduções, explicações, aspas, títulos ou menções a cidade, estado ou localização geográfica. Comece direto no texto de apoio."""

    try:
        text = None

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            text = response.text.strip()
        except Exception as primary_err:
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=api_key)
                try:
                    model = genai_legacy.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(prompt)
                except Exception:
                    model = genai_legacy.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                text = response.text.strip()
            except Exception as secondary_err:
                raise Exception(f"Primary SDK: {primary_err} | Secondary SDK: {secondary_err}")

        if text:
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1].strip()
            return text
        return generate_fallback_message(name, age, cat)
    except Exception as e:
        print(f"[DiaUp AI Engine] Erro ao chamar API Gemini: {e}. Usando fallback local.")
        return generate_fallback_message(name, age, cat)


def generate_tts_audio(text, voice="pt-BR-FranciscaNeural"):
    """
    Gera o arquivo de áudio MP3 com síntese neural de alta fidelidade em Português Brasileiro (PT-BR)
    utilizando a voz de estúdio Francisca/Antonio (expressividade humana) com fallback gracioso.
    """
    if not text or not text.strip():
        return None

    clean_text = text.strip()

    # 1. Tenta síntese de voz neural estúdio com edge-tts (Francisca / Antonio)
    try:
        import asyncio
        import edge_tts
        import concurrent.futures

        target_voice = voice if voice in ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", "pt-BR-ThalitaNeural"] else "pt-BR-FranciscaNeural"

        async def _synth():
            communicate = edge_tts.Communicate(clean_text, target_voice, rate="+0%", pitch="+0Hz")
            audio_bytes = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
            return bytes(audio_bytes)

        try:
            audio_data = asyncio.run(_synth())
        except Exception:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                audio_data = pool.submit(lambda: asyncio.run(_synth())).result()

        if audio_data and len(audio_data) > 500:
            return audio_data
    except Exception as e:
        print(f"[DiaUp Neural TTS] Aviso ao gerar voz neural estúdio: {e}. Usando fallback gTTS.")

    # 2. Fallback para gTTS
    try:
        import io
        from gtts import gTTS
        fp = io.BytesIO()
        tts = gTTS(text=clean_text, lang='pt', tld='com.br')
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        print(f"[DiaUp TTS Engine] Erro ao gerar áudio: {e}")
        return None


# ==========================================
# HORÓSCOPO DIÁRIO PERSONALIZADO
# ==========================================

ZODIAC_SIGNS = [
    {"id": "aries", "name": "Áries", "symbol": "♈", "element": "Fogo", "date_range": "21/03 a 19/04", "colors": ["Vermelho Solar", "Âmbar", "Coral"]},
    {"id": "touro", "name": "Touro", "symbol": "♉", "element": "Terra", "date_range": "20/04 a 20/05", "colors": ["Verde Esmeralda", "Dourado", "Terracota"]},
    {"id": "gemeos", "name": "Gêmeos", "symbol": "♊", "element": "Ar", "date_range": "21/05 a 20/06", "colors": ["Amarelo Ouro", "Azul Celeste", "Prata"]},
    {"id": "cancer", "name": "Câncer", "symbol": "♋", "element": "Água", "date_range": "21/06 a 22/07", "colors": ["Pérola", "Azul Sereno", "Prata"]},
    {"id": "leao", "name": "Leão", "symbol": "♌", "element": "Fogo", "date_range": "23/07 a 22/08", "colors": ["Dourado Solar", "Laranja Vibrante", "Âmbar"]},
    {"id": "virgem", "name": "Virgem", "symbol": "♍", "element": "Terra", "date_range": "23/08 a 22/09", "colors": ["Verde Sálvia", "Areia", "Azul Marinho"]},
    {"id": "libra", "name": "Libra", "symbol": "♎", "element": "Ar", "date_range": "23/09 a 22/10", "colors": ["Rosa Quartzo", "Azul Céu", "Lavanda"]},
    {"id": "escorpiao", "name": "Escorpião", "symbol": "♏", "element": "Água", "date_range": "23/10 a 21/11", "colors": ["Vinho", "Índigo", "Dourado"]},
    {"id": "sagitario", "name": "Sagitário", "symbol": "♐", "element": "Fogo", "date_range": "22/11 a 21/12", "colors": ["Violeta", "Turquesa", "Laranja"]},
    {"id": "capricornio", "name": "Capricórnio", "symbol": "♑", "element": "Terra", "date_range": "22/12 a 19/01", "colors": ["Azul Profundo", "Grafite", "Verde Musgo"]},
    {"id": "aquario", "name": "Aquário", "symbol": "♒", "element": "Ar", "date_range": "20/01 a 18/02", "colors": ["Azul Elétrico", "Ciano", "Prata"]},
    {"id": "peixes", "name": "Peixes", "symbol": "♓", "element": "Água", "date_range": "19/02 a 20/03", "colors": ["Água-Marinha", "Lilás", "Branco Pérola"]},
]

ZODIAC_BY_ID = {s["id"]: s for s in ZODIAC_SIGNS}


def get_zodiac_from_birth_date(birth_date_str):
    """Calcula o signo solar a partir da data de nascimento (DD/MM/AAAA ou AAAA-MM-DD)."""
    raw = str(birth_date_str or "").strip()
    if not raw or (len(raw) == 4 and raw.isdigit()):
        return None
    dt = parse_birth_date(raw)
    if not dt:
        return None
    try:
        m, d = dt.month, dt.day
        if (m == 3 and d >= 21) or (m == 4 and d <= 19):
            return ZODIAC_BY_ID["aries"]
        if (m == 4 and d >= 20) or (m == 5 and d <= 20):
            return ZODIAC_BY_ID["touro"]
        if (m == 5 and d >= 21) or (m == 6 and d <= 20):
            return ZODIAC_BY_ID["gemeos"]
        if (m == 6 and d >= 21) or (m == 7 and d <= 22):
            return ZODIAC_BY_ID["cancer"]
        if (m == 7 and d >= 23) or (m == 8 and d <= 22):
            return ZODIAC_BY_ID["leao"]
        if (m == 8 and d >= 23) or (m == 9 and d <= 22):
            return ZODIAC_BY_ID["virgem"]
        if (m == 9 and d >= 23) or (m == 10 and d <= 22):
            return ZODIAC_BY_ID["libra"]
        if (m == 10 and d >= 23) or (m == 11 and d <= 21):
            return ZODIAC_BY_ID["escorpiao"]
        if (m == 11 and d >= 22) or (m == 12 and d <= 21):
            return ZODIAC_BY_ID["sagitario"]
        if (m == 12 and d >= 22) or (m == 1 and d <= 19):
            return ZODIAC_BY_ID["capricornio"]
        if (m == 1 and d >= 20) or (m == 2 and d <= 18):
            return ZODIAC_BY_ID["aquario"]
        return ZODIAC_BY_ID["peixes"]
    except Exception:
        return None


def _call_gemini_text(prompt):
    """Helper centralizado para chamar a API do Gemini com fallback entre SDKs."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        text = None
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            text = response.text.strip()
        except Exception:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            try:
                model = genai_legacy.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
            except Exception:
                model = genai_legacy.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
            text = response.text.strip()

        if text:
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1].strip()
            return text
    except Exception as e:
        print(f"[DiaUp AI Engine] Aviso ao chamar Gemini: {e}")
    return None


def generate_horoscope(profile, sign_id=None):
    """Gera o horóscopo diário personalizado para o signo do usuário."""
    name = (profile.get("name") or "Amigo(a)").strip()
    age = calculate_age(profile.get("birth_date"))

    sign_info = None
    if sign_id and sign_id.lower() in ZODIAC_BY_ID:
        sign_info = ZODIAC_BY_ID[sign_id.lower()]
    if not sign_info:
        sign_info = get_zodiac_from_birth_date(profile.get("birth_date"))
    if not sign_info:
        sign_info = ZODIAC_BY_ID["leao"]

    today_seed = int(datetime.now().strftime("%Y%m%d")) + sum(ord(c) for c in sign_info["id"])
    rng = random.Random(today_seed)
    lucky_number = rng.randint(1, 99)
    lucky_color = rng.choice(sign_info["colors"])
    energy = rng.choice(["Radiante ☀️", "Criativa ✨", "Serena 🌿", "Magnética 💫", "Focada 🎯"])

    fallback_by_element = {
        "Fogo": [
            f"{name}, a energia de {sign_info['name']} acende hoje sua coragem para iniciar o que estava guardado. Confie no seu impulso criativo, mas lembre-se de respirar antes de agir para transformar entusiasmo em conquistas reais.",
            f"{name}, os astros iluminam seu brilho natural de {sign_info['name']} neste dia. É um excelente momento para liderar conversas importantes, celebrar suas vitórias e espalhar otimismo por onde passar."
        ],
        "Terra": [
            f"{name}, a força serena de {sign_info['name']} favorece escolhas práticas e resultados duradouros hoje. Organize suas prioridades com calma e confie que cada passo firme constrói a segurança que você deseja.",
            f"{name}, o céu convida sua essência de {sign_info['name']} a valorizar os pequenos prazeres e a constância. Uma decisão bem pensada hoje pode abrir portas valiosas para sua tranquilidade."
        ],
        "Ar": [
            f"{name}, sua mente brilhante de {sign_info['name']} está especialmente receptiva a boas ideias e conexões sinceras hoje. Permita-se ouvir novas perspectivas e transformar diálogos leves em grandes oportunidades.",
            f"{name}, a leveza de {sign_info['name']} traz clareza para resolver pendências com criatividade. Confie na sua intuição comunicativa e dê espaço para o novo surpreender sua rotina."
        ],
        "Água": [
            f"{name}, a sensibilidade de {sign_info['name']} é sua maior bússola neste dia. Acolha seus sentimentos com carinho, fortaleça os laços que nutrem sua alma e confie no tempo certo das coisas.",
            f"{name}, as energias de hoje abraçam sua intuição profunda de {sign_info['name']}. Reserve um instante de silêncio para ouvir seu coração: a resposta que você procura já está dentro de você."
        ],
    }

    prompt = f"""Você é o astrólogo emocional e acolhedor do aplicativo DiaUp.
Crie um horóscopo diário curto, inspirador e positivo para o usuário.

DADOS:
- Nome: {name}
- Idade: {age} anos
- Signo: {sign_info['name']} (Elemento {sign_info['element']})
- Data de hoje: {datetime.now().strftime('%d/%m/%Y')}

REGRAS OBRIGATÓRIAS:
1. Comece OBRIGATORIAMENTE com "{name}, " na primeira palavra.
2. Máximo de 3 a 4 linhas (leitura rápida e agradável no celular).
3. Tom acolhedor, maduro e luminoso, adaptado para {age} anos.
4. Proibido citar cidade, estado ou localização geográfica.
5. Retorne APENAS o texto final do horóscopo, sem títulos, aspas ou marcadores."""

    ai_text = _call_gemini_text(prompt)
    if not ai_text:
        ai_text = random.choice(fallback_by_element.get(sign_info["element"], fallback_by_element["Fogo"]))

    return {
        "sign_id": sign_info["id"],
        "sign": sign_info["name"],
        "symbol": sign_info["symbol"],
        "element": sign_info["element"],
        "date_range": sign_info["date_range"],
        "lucky_number": lucky_number,
        "lucky_color": lucky_color,
        "energy": energy,
        "content": ai_text,
        "created_at": datetime.now().isoformat(),
    }


# ==========================================
# TARÔ DO DIA (ARCANOS MAIORES)
# ==========================================

TAROT_DECK = [
    {"id": 0, "roman": "XIX", "name": "O Sol", "symbol": "☀️", "keyword": "Vitalidade & Clareza", "accent": "#FF9800",
     "fallback": "a carta O Sol ilumina o seu caminho hoje com alegria, verdade e energia renovada. Permita-se brilhar sem medo e celebrar as boas notícias que se aproximam."},
    {"id": 1, "roman": "XVII", "name": "A Estrela", "symbol": "🌟", "keyword": "Esperança & Inspiração", "accent": "#00B4D8",
     "fallback": "a carta A Estrela traz serenidade e fé renovada para o seu coração. Mesmo após dias desafiadores, o universo sussurra que você está guiado rumo à cura e à realização."},
    {"id": 2, "roman": "VIII", "name": "A Força", "symbol": "🦁", "keyword": "Coragem Gentil", "accent": "#EF6F61",
     "fallback": "a carta A Força lembra que seu maior poder não está na pressa, mas na calma firme e no domínio emocional. Você tem tudo o que precisa para vencer qualquer obstáculo com elegância."},
    {"id": 3, "roman": "I", "name": "O Mago", "symbol": "✨", "keyword": "Criação & Iniciativa", "accent": "#7C3AED",
     "fallback": "a carta O Mago revela que todas as ferramentas para transformar suas ideias em realidade já estão em suas mãos. Confie no seu talento e dê o primeiro passo hoje."},
    {"id": 4, "roman": "III", "name": "A Imperatriz", "symbol": "🌿", "keyword": "Abundância & Cuidado", "accent": "#1B7F63",
     "fallback": "a carta A Imperatriz anuncia um ciclo fértil de criatividade, afeto e prosperidade. Cuide de si com carinho e veja seus projetos florescerem naturalmente."},
    {"id": 5, "roman": "X", "name": "A Roda da Fortuna", "symbol": "🎡", "keyword": "Virada Positiva", "accent": "#D97706",
     "fallback": "a carta A Roda da Fortuna sinaliza uma mudança bem-vinda em movimento. Abra-se para o inesperado com confiança, pois o fluxo da vida está girando a seu favor."},
    {"id": 6, "roman": "XIV", "name": "A Temperança", "symbol": "🕊️", "keyword": "Equilíbrio & Paz", "accent": "#0EA5E9",
     "fallback": "a carta A Temperança convida você a dosar razão e emoção com suavidade. Hoje, a harmonia nasce quando você respeita o seu ritmo e escolhe a paz acima da urgência."},
    {"id": 7, "roman": "XXI", "name": "O Mundo", "symbol": "🌍", "keyword": "Plenitude & Conquista", "accent": "#2563EB",
     "fallback": "a carta O Mundo celebra ciclos completos e horizontes abertos. Reconheça o quanto você evoluiu até aqui e prepare-se para abraçar uma nova fase de realização."},
    {"id": 8, "roman": "VI", "name": "Os Enamorados", "symbol": "💛", "keyword": "Escolhas do Coração", "accent": "#E11D48",
     "fallback": "a carta Os Enamorados ilumina o valor das conexões verdadeiras e das decisões alinhadas aos seus valores. Escolher com autenticidade hoje trará leveza e sintonia."},
    {"id": 9, "roman": "VII", "name": "O Carro", "symbol": "⚡", "keyword": "Direção & Vitória", "accent": "#EA580C",
     "fallback": "a carta O Carro traz impulso, foco e determinação para avançar. Segure as rédeas dos seus objetivos com confiança, pois o movimento de hoje leva você mais perto da vitória."},
    {"id": 10, "roman": "IX", "name": "O Eremita", "symbol": "🕯️", "keyword": "Sabedoria Interior", "accent": "#4F46E5",
     "fallback": "a carta O Eremita convida a uma pausa consciente para ouvir sua própria sabedoria. No silêncio de hoje, você encontra clareza para enxergar o próximo passo com segurança."},
    {"id": 11, "roman": "XI", "name": "A Justiça", "symbol": "⚖️", "keyword": "Verdade & Clareza", "accent": "#0F766E",
     "fallback": "a carta A Justiça traz equilíbrio, honestidade e colheita justa para os seus esforços. Confie na transparência das suas ações, pois tudo tende a se alinhar com retidão."},
]


def generate_tarot_reading(profile, card_id=None):
    """Sorteia ou interpreta uma carta de Tarô personalizada para o usuário."""
    name = (profile.get("name") or "Amigo(a)").strip()
    age = calculate_age(profile.get("birth_date"))

    card = None
    if card_id is not None:
        try:
            idx = int(card_id) % len(TAROT_DECK)
            card = TAROT_DECK[idx]
        except Exception:
            card = None
    if not card:
        card = random.choice(TAROT_DECK)

    prompt = f"""Você é o guia simbólico e acolhedor de Tarô do aplicativo DiaUp.
Interprete a carta sorteada de forma poética, prática, positiva e motivadora.

DADOS:
- Nome: {name}
- Idade: {age} anos
- Carta sorteada: {card['name']} (Arcano {card['roman']} — {card['keyword']})

REGRAS OBRIGATÓRIAS:
1. Comece OBRIGATORIAMENTE com "{name}, " na primeira palavra.
2. Máximo de 3 a 4 linhas (leitura rápida e inspiradora no celular).
3. Relacione o simbolismo da carta {card['name']} com um conselho prático e acolhedor para o dia de alguém de {age} anos.
4. Proibido citar cidade, estado ou localização geográfica.
5. Retorne APENAS o texto final da leitura, sem títulos ou aspas."""

    ai_text = _call_gemini_text(prompt)
    if not ai_text:
        ai_text = f"{name}, {card['fallback']}"

    return {
        "card_id": card["id"],
        "roman": card["roman"],
        "card_name": card["name"],
        "symbol": card["symbol"],
        "keyword": card["keyword"],
        "accent": card["accent"],
        "content": ai_text,
        "created_at": datetime.now().isoformat(),
    }



