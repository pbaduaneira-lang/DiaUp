import os
import random
from datetime import datetime

def calculate_age(birth_date_str):
    if not birth_date_str:
        return 28
    try:
        # Tenta formato YYYY-MM-DD
        if len(str(birth_date_str)) >= 10:
            birth_date = datetime.strptime(str(birth_date_str)[:10], "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return max(10, min(120, age))
        # Tenta apenas ano YYYY
        elif len(str(birth_date_str)) == 4 and str(birth_date_str).isdigit():
            age = datetime.today().year - int(birth_date_str)
            return max(10, min(120, age))
    except Exception:
        pass
    return 28

def generate_fallback_message(name, age, city, state, category):
    """
    Mecanismo de fallback inteligente caso a chave do Gemini não esteja configurada ou haja sem internet.
    Garante que a mensagem cumpra todas as 5 diretrizes emocionais do DiaUp localmente.
    """
    cidade_clean = city or "sua cidade"
    nome_clean = name or "amigo(a)"
    cat = (category or "Geral").capitalize()

    templates = {
        "Saúde": [
            f"{nome_clean}, cuidar de si mesmo em {cidade_clean} é o primeiro e mais importante passo para qualquer conquista. Aos {age} anos, você entende que sua vitalidade física e mental é o seu maior patrimônio. Ouça o seu corpo hoje, respeite seus limites e celebre cada escolha que nutre o seu bem-estar.",
            f"{nome_clean}, a correria diária em {cidade_clean} não pode nos fazer esquecer de quem nos mantém de pé: nós mesmos. Com a sabedoria dos seus {age} anos, lembre-se de que o descanso e o cuidado com a saúde não são perda de tempo, mas renovação de energia. Respire fundo e dê a si mesmo o amor que você merece."
        ],
        "Projetos": [
            f"{nome_clean}, tirar ideias do papel em {cidade_clean} exige coragem e visão, qualidades que você tem de sobra. Aos {age} anos, cada projeto iniciado é uma manifestação do seu propósito e da sua vontade de crescer. Confie no planejamento que você fez e dê mais um passo prático rumo à sua realização.",
            f"{nome_clean}, o segredo para realizar grandes projetos em {cidade_clean} está em dividir o sonho em pequenas ações diárias. A maturidade dos seus {age} anos te dá a disciplina necessária para persistir mesmo quando os desafios surgem. Mantenha o entusiasmo do primeiro dia e celebre cada etapa concluída."
        ],
        "Trabalho": [
            f"{nome_clean}, o ritmo de {cidade_clean} exige muito, mas sua trajetória profissional está sendo construída com uma solidez admirável. Aos {age} anos, cada desafio superado no trabalho não é um tropeço, e sim um degrau essencial para sua maturidade e autonomia. Confie na sua capacidade de transformar esforço em resultado hoje.",
            f"{nome_clean}, mesmo com a correria típica de {cidade_clean}, é fundamental reconhecer o valor do que você entrega todos os dias. Com a experiência dos seus {age} anos, você já possui o discernimento necessário para focar no que realmente importa em sua carreira. Respire fundo e dê o próximo passo com serenidade."
        ],
        "Foco": [
            f"{nome_clean}, entre tantas distrações que o dia a dia em {cidade_clean} pode trazer, sua clareza de propósito é o seu maior escudo. Aos {age} anos, direcionar sua energia para o que verdadeiramente constrói o seu futuro é um ato de sabedoria e poder pessoal. Mantenha os olhos na sua meta e permita-se avançar um passo de cada vez.",
            f"{nome_clean}, o segredo para avançar em {cidade_clean} não é correr mais rápido, mas caminhar na direção certa com consistência. A bagagem dos seus {age} anos te ensina que o verdadeiro foco nasce da calma e da escolha deliberada. Feche os olhos para o ruído externo e confie no seu ritmo hoje."
        ],
        "Coragem": [
            f"{nome_clean}, é natural sentir frio na barriga diante do novo em {cidade_clean}, mas sua força interna é infinitamente maior que qualquer receio. Aos {age} anos, você já superou tempestades que pareciam intermináveis e saiu mais forte de cada uma delas. Abrace a coragem que habita em você e ouse dar o salto que seu coração pede.",
            f"{nome_clean}, a verdadeira coragem não é a ausência do medo, mas a decisão firme de não deixar que ele paralise seus sonhos em {cidade_clean}. Com a vivência e a maturidade dos seus {age} anos, você tem todos os recursos internos para reescrever qualquer situação. Confie na sua voz interior e siga em frente com firmeza."
        ],
        "Disciplina": [
            f"{nome_clean}, a consistência diária em {cidade_clean} é o que transforma sonhos distantes em conquistas palpáveis na sua vida. Aos {age} anos, você sabe que a motivação inicia o caminho, mas é a disciplina compassiva que sustenta a jornada. Honre seu compromisso consigo mesmo hoje, celebrando cada pequena vitória no trajeto.",
            f"{nome_clean}, construir algo grandioso em {cidade_clean} requer a paciência de plantar um pouco todos os dias. A maturidade dos seus {age} anos te dá a clareza de que os hábitos diários esculpem o futuro que você deseja viver. Mantenha o foco no processo e orgulhe-se da sua dedicação constante."
        ],
        "Relacionamento": [
            f"{nome_clean}, as conexões verdadeiras que cultivamos em {cidade_clean} são flores que regamos com escuta, respeito e presença. Aos {age} anos, você compreende que amar e ser amado exige autenticidade e o acolhimento das imperfeições de cada um. Abra seu coração para a empatia hoje, fortalecendo os laços que trazem paz à sua vida.",
            f"{nome_clean}, construir pontes sólidas com quem amamos em {cidade_clean} é um dos maiores investimentos da nossa jornada. Com a sabedoria dos seus {age} anos, lembre-se de que o diálogo sincero e o carinho diário transformam qualquer obstáculo em união. Valorize quem caminha ao seu lado e espalhe a luz que existe em você."
        ],
        "Família": [
            f"{nome_clean}, o aconchego familiar, não importa onde estejamos em {cidade_clean}, é o porto seguro que renova nossas forças para a vida. Aos {age} anos, você sabe valorizar as raízes que te sustentam e o amor incondicional que moldou quem você é hoje. Dedique um tempo para nutrir esses laços e sentir a paz que vem do lar.",
            f"{nome_clean}, em meio ao ritmo da vida em {cidade_clean}, a família é o nosso lembrete constante de pertencimento e afeto verdadeiro. A maturidade dos seus {age} anos te permite enxergar a beleza nas pequenas tradições e no cuidado mútuo. Agradeça por quem faz parte da sua história e espalhe esse acolhimento."
        ],
        "Amor": [
            f"{nome_clean}, o amor que cultivamos em {cidade_clean} começa pelo carinho e respeito que temos por nós mesmos. Aos {age} anos, você entende que amar é acolher a verdade do outro sem perder a própria essência. Abra seu coração para viver relações leves, francas e repletas de reciprocidade.",
            f"{nome_clean}, nos caminhos de {cidade_clean}, o amor é a luz que suavemente transforma qualquer rotina em significado. Com a sabedoria dos seus {age} anos, você sabe que o afeto verdadeiro floresce na presença e nos pequenos gestos diários. Permita-se amar e ser amado com toda a beleza e intensidade que você merece."
        ],
        "Finanças": [
            f"{nome_clean}, a prosperidade em {cidade_clean} é construída passo a passo com organização, clareza e paciência. Aos {age} anos, cada escolha consciente que você faz com suas finanças é um investimento na sua liberdade e tranquilidade futura. Confie no seu planejamento e celebre cada meta alcançada.",
            f"{nome_clean}, lidar com finanças no ritmo de {cidade_clean} requer equilíbrio entre viver o presente e plantar para o futuro. Com a maturidade dos seus {age} anos, você tem o discernimento necessário para transformar seus recursos em segurança e paz de espírito. Mantenha o foco no seu crescimento e honre o valor do seu esforço."
        ],
        "Sucesso": [
            f"{nome_clean}, o verdadeiro sucesso em {cidade_clean} não é apenas o topo da montanha, mas a pessoa incrível que você se torna na subida. Aos {age} anos, cada aprendizado acumulado é uma medalha silenciosa do seu valor e da sua capacidade de superação. Celebre o quanto você já caminhou e continue construindo seu legado com orgulho.",
            f"{nome_clean}, prosperar em {cidade_clean} é alinhar suas conquistas externas com a sua paz de espírito interior. Com a experiência dos seus {age} anos, você entende que o sucesso autêntico é viver com propósito, integridade e alegria diária. Confie no seu potencial ilimitado para alcançar o extraordinário."
        ],
        "Geral": [
            f"{nome_clean}, o clima e a energia de {cidade_clean} hoje trazem um convite especial para você renovar suas esperanças. Aos {age} anos, sua história já provou inúmeras vezes a sua incrível capacidade de se reinventar e florescer. Respire fundo, acolha o momento presente e saiba que você está exatamente onde precisa estar para evoluir.",
            f"{nome_clean}, cada amanhecer em {cidade_clean} é uma página em branco pronta para receber o melhor da sua energia. Com a vivência dos seus {age} anos, você tem a sabedoria de escolher quais batalhas merecem sua atenção e onde depositar seu coração. Siga com leveza, confiando na beleza do seu caminho único."
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
    city = (profile.get("city") or "Sua Cidade").strip()
    state = (profile.get("state") or "BR").strip()
    cat = (category or "Geral").strip()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return generate_fallback_message(name, age, city, state, cat)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        prompt = f"""Você é o motor de inteligência emocional do aplicativo DiaUp. Sua missão é gerar uma mensagem curta de apoio, reflexão e motivação altamente personalizada, garantindo que o usuário sinta um acolhimento genuíno e único.

DADOS DO USUÁRIO ATUAL:
- Nome: {name}
- Idade: {age} anos
- Localização: {city} - {state}
- Tema solicitado: {cat}

DIRETRIZES DE CONTEÚDO E FORMATO:
1. CURTO E DIRETO: A mensagem deve ter no máximo 3 ou 4 linhas (ideal para leitura rápida em telas de celular).
2. NOME SEMPRE NO INÍCIO: A mensagem DEVE OBRIGATORIAMENTE começar com o nome do usuário seguido de vírgula (exemplo: "{name}, ..."). Use o nome de forma acolhedora logo na primeira palavra do texto.
3. MATURIDADE ADEQUADA: Adapte a abordagem, os conselhos e o vocabulário para a idade de {age} anos. 
4. TOQUE DE EMPATIA LOCAL: Use sutilmente o contexto de estar em {city} (pense no ritmo de vida da região ou na estação/clima atual se fizer sentido para a metáfora) para gerar proximidade geográfica.
5. VARIABILIDADE MÁXIMA: Evite clichês e frases feitas de internet. Reestruture as frases de modo criativo para que, se o mesmo usuário pedir outra mensagem do mesmo tema, ela soe completamente diferente.

RESTRICÇÃO CRÍTICA: Retorne APENAS o texto da mensagem final. Não inclua introduções, explicações, aspas ou títulos. Comece direto no texto de apoio."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        text = response.text.strip()
        # Remove aspas caso o modelo as inclua acidentalmente
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()
        return text
    except Exception as e:
        print(f"[DiaUp AI Engine] Erro ao chamar API Gemini: {e}. Usando fallback local.")
        return generate_fallback_message(name, age, city, state, cat)
