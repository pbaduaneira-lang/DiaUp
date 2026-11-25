import random
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response

app = Flask(__name__)
app.secret_key = "diaup_secret_key_super_segura_1016"

from .database import get_db, init_db
from . import ai_engine

@app.route("/user/tts", methods=["GET", "POST"])
def user_tts():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        voice = (data.get("voice") or "pt-BR-FranciscaNeural").strip()
    else:
        text = (request.args.get("text") or "").strip()
        voice = (request.args.get("voice") or "pt-BR-FranciscaNeural").strip()

    if not text:
        return jsonify({"error": "O parâmetro 'text' é obrigatório."}), 400

    audio_data = ai_engine.generate_tts_audio(text, voice=voice)
    if not audio_data:
        return jsonify({"error": "Não foi possível gerar a síntese de voz."}), 500

    return Response(audio_data, mimetype="audio/mpeg")



ADMIN_EMAIL = "diaup@gmail.com"
ADMIN_PASSWORD = "diaedju1016"
ADMIN_PASSWORDS = {"diaedju1016", "diaupedju1016"}


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.path.startswith("/admin/") and request.path != "/admin/login":
                return jsonify({"error": "Não autorizado. Faça login no painel administrativo."}), 401
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


def row_to_message(row):
    created_at_val = row["created_at"]
    if hasattr(created_at_val, "isoformat"):
        created_at_str = created_at_val.isoformat()
    else:
        created_at_str = str(created_at_val) if created_at_val is not None else datetime.now().isoformat()
    return {
        "id": row["id"],
        "content": row["content"],
        "category": row["category"] or "Geral",
        "created_at": created_at_str,
    }


@app.route("/")
def user_index():
    return render_template("user.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        email = (data.get("email") or "").strip()
        password = (data.get("password") or "").strip()
        
        if email == ADMIN_EMAIL and (password == ADMIN_PASSWORD or password in ADMIN_PASSWORDS):
            session["admin_logged_in"] = True
            if request.is_json:
                return jsonify({"message": "Login realizado com sucesso!", "redirect": "/admin"}), 200
            return redirect(url_for("admin_index"))
        else:
            if request.is_json:
                return jsonify({"error": "E-mail ou senha incorretos."}), 401
            return render_template("admin_login.html", error="E-mail ou senha incorretos."), 401
            
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_index"))
    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_logged_in", None)
    return jsonify({"message": "Sessão encerrada com sucesso.", "redirect": "/admin/login"}), 200


@app.route("/admin")
@admin_required
def admin_index():
    return render_template("admin.html")


@app.route("/admin/add_message", methods=["POST"])
@admin_required
def add_message():
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    category = (data.get("category") or "Geral").strip() or "Geral"

    if len(content) < 8:
        return jsonify({"error": "Escreva uma mensagem com pelo menos 8 caracteres."}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO messages (content, category) VALUES (%s, %s) RETURNING id",
            (content, category),
        )
        message_id = cursor.fetchone()["id"]
        db.commit()

        cursor.execute("SELECT id, content, category, created_at FROM messages WHERE id = %s", (message_id,))
        return jsonify({"message": "Mensagem adicionada com sucesso.", "item": row_to_message(cursor.fetchone())}), 201
    except Exception as e:
        print(f"[Admin Error] Erro ao salvar mensagem no PostgreSQL: {e}")
        return jsonify({"error": f"Erro do PostgreSQL: {e}. Verifique se a variável DATABASE_URL na Vercel está configurada com a URI do Connection Pooler (IPv4) e a senha codificada."}), 503


@app.route("/admin/messages", methods=["GET"])
@admin_required
def list_messages():
    messages = []
    categories = {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT id, content, category, created_at
            FROM messages
            ORDER BY created_at DESC, id DESC
            """
        )
        messages = [row_to_message(row) for row in cursor.fetchall()]
        for item in messages:
            categories[item["category"]] = categories.get(item["category"], 0) + 1
    except Exception as e:
        print(f"[Admin Error] Erro ao listar mensagens do PostgreSQL: {e}")

    return jsonify({
        "messages": messages,
        "total": len(messages),
        "categories": categories,
    })


@app.route("/admin/messages/<int:message_id>", methods=["DELETE"])
@admin_required
def delete_message(message_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Mensagem nao encontrada."}), 404

        return jsonify({"message": "Mensagem removida."})
    except Exception as e:
        print(f"[Admin Error] Erro ao deletar mensagem: {e}")
        return jsonify({"error": f"Erro PostgreSQL ({e}) ao deletar."}), 503


@app.route("/admin/messages/<int:message_id>", methods=["PUT"])
@admin_required
def update_message(message_id):
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    category = (data.get("category") or "Geral").strip() or "Geral"

    if len(content) < 8:
        return jsonify({"error": "Escreva uma mensagem com pelo menos 8 caracteres."}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE messages SET content = %s, category = %s WHERE id = %s",
            (content, category, message_id),
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Mensagem não encontrada."}), 404

        cursor.execute("SELECT id, content, category, created_at FROM messages WHERE id = %s", (message_id,))
        return jsonify({"message": "Mensagem atualizada com sucesso.", "item": row_to_message(cursor.fetchone())}), 200
    except Exception as e:
        print(f"[Admin Error] Erro ao atualizar mensagem: {e}")
        return jsonify({"error": f"Erro PostgreSQL ({e}) ao atualizar."}), 503


@app.route("/user/profile", methods=["GET"])
def get_user_profile():
    user_id = (request.args.get("user_id") or "default").strip()
    try:
        db = get_db()
        cursor = db.cursor()
        if user_id == "default":
            cursor.execute("SELECT id, user_id, name, birth_date, city, state FROM user_profile WHERE user_id = %s OR id = 1 ORDER BY id ASC LIMIT 1", (user_id,))
        else:
            cursor.execute("SELECT id, user_id, name, birth_date, city, state FROM user_profile WHERE user_id = %s LIMIT 1", (user_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"user_id": user_id, "name": "", "birth_date": "", "city": "", "state": "", "is_new": True}), 200
        birth_date_val = row["birth_date"]
        birth_date_str = birth_date_val.isoformat() if hasattr(birth_date_val, "isoformat") else (str(birth_date_val) if birth_date_val else "")
        return jsonify({
            "user_id": row["user_id"] or "default",
            "name": row["name"] or "",
            "birth_date": birth_date_str,
            "city": row["city"] or "",
            "state": row["state"] or "",
            "is_new": False
        }), 200
    except Exception as e:
        print(f"[DiaUp] Erro ao buscar perfil no PostgreSQL: {e}")
        return jsonify({"user_id": user_id, "name": "", "birth_date": "", "city": "", "state": "", "is_new": True}), 200


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@app.route("/user/profile", methods=["POST"])
def update_user_profile():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    name = (data.get("name") or "Viajante").strip()
    birth_date = ai_engine.normalize_birth_date(data.get("birth_date") or "1996-01-01")
    city = (data.get("city") or "São Paulo").strip()
    state = (data.get("state") or "SP").strip()


    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO user_profile (user_id, name, birth_date, city, state)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT(user_id) DO UPDATE SET
                name = EXCLUDED.name,
                birth_date = EXCLUDED.birth_date,
                city = EXCLUDED.city,
                state = EXCLUDED.state
            """,
            (user_id, name, birth_date, city, state)
        )
        try:
            cursor.execute(
                """
                INSERT INTO usuarios (nome, data_nascimento, cidade, estado)
                VALUES (%s, %s, %s, %s)
                """,
                (name, birth_date if len(str(birth_date)) == 10 else None, city, state)
            )
        except Exception:
            pass
        db.commit()
    except Exception as e:
        print(f"[DiaUp] Aviso: Não foi possível salvar perfil no PostgreSQL ({e}). Operando com resposta ágil com IA.")
    
    return jsonify({"message": "Perfil atualizado com sucesso!", "profile": {"user_id": user_id, "name": name, "birth_date": birth_date, "city": city, "state": state}}), 200


@app.route("/user/get_message", methods=["GET"])
def get_message():
    category = (request.args.get("category") or "").strip()
    user_id = (request.args.get("user_id") or "default").strip()
    name_param = (request.args.get("name") or "").strip()
    city_param = (request.args.get("city") or "").strip()
    state_param = (request.args.get("state") or "").strip()
    birth_param = (request.args.get("birth_date") or "").strip()
    seen_raw = request.args.get("seen") or "[]"
    
    seen_list = []
    try:
        import json
        seen_list = json.loads(seen_raw)
        if not isinstance(seen_list, list):
            seen_list = []
    except Exception:
        seen_list = []

    # Normaliza mensagens já vistas para verificação case-insensitive
    seen_normalized = {str(s).strip().lower() for s in seen_list if s}
    
    profile = {
        "name": name_param or "Amigo(a)",
        "birth_date": birth_param or "1996-01-01",
        "city": city_param or "Sua Cidade",
        "state": state_param or "BR",
    }
    saved_messages = []
    
    try:
        db = get_db()
        cursor = db.cursor()
        if user_id == "default":
            cursor.execute("SELECT id, user_id, name, birth_date, city, state FROM user_profile WHERE user_id = %s OR id = 1 ORDER BY id ASC LIMIT 1", (user_id,))
        else:
            cursor.execute("SELECT id, user_id, name, birth_date, city, state FROM user_profile WHERE user_id = %s LIMIT 1", (user_id,))
        profile_row = cursor.fetchone()
        if profile_row and profile_row["name"]:
            birth_date_val = profile_row["birth_date"]
            birth_date_str = birth_date_val.isoformat() if hasattr(birth_date_val, "isoformat") else (str(birth_date_val) if birth_date_val else "1996-01-01")
            profile = {
                "name": profile_row["name"] or profile["name"],
                "birth_date": birth_date_str or profile["birth_date"],
                "city": profile_row["city"] or profile["city"],
                "state": profile_row["state"] or profile["state"],
            }
        
        cursor.execute(
            "SELECT content FROM messages WHERE LOWER(category) = LOWER(%s) OR LOWER(category) = 'geral'",
            (category or "Geral",)
        )
        saved_rows = cursor.fetchall()
        saved_messages = [row["content"] for row in saved_rows]
    except Exception as e:
        print(f"[DiaUp] Erro de conexão ao PostgreSQL durante get_message: {e}. Usando fallback/IA com parâmetros do usuário.")

    # 1. Filtra as mensagens salvas no Banco de Dados do Admin que AINDA NÃO foram vistas pelo usuário
    unseen_db_messages = []
    name_clean = profile["name"].strip().lower()
    for msg in saved_messages:
        msg_clean = msg.strip().lower()
        # Verifica se o texto puro ou o texto prefixado com nome já foi visto
        if msg_clean not in seen_normalized and f"{name_clean}, {msg_clean}" not in seen_normalized:
            unseen_db_messages.append(msg)

    # 2. Se existirem mensagens no banco ainda não vistas, apresenta uma mensagem do banco!
    if unseen_db_messages:
        ai_content = random.choice(unseen_db_messages)
    else:
        # 3. Se TODAS as mensagens do banco já passaram por ali (ou banco vazio), gera nova reflexão via IA Gemini!
        ai_content = ai_engine.generate_motivational_message(profile, category)

    # Garante que a mensagem sempre comece com o nome do usuário seguido de vírgula
    name = profile["name"].strip()
    if name and not ai_content.lower().startswith(f"{name.lower()},"):
        for prefix in ["olá,", "olá ", "querido,", "querido ", "querida,", "querida "]:
            if ai_content.lower().startswith(prefix):
                ai_content = ai_content[len(prefix):].strip()
                break
        
        if not ai_content.lower().startswith(f"{name.lower()},"):
            first_word = ai_content.split()[0] if ai_content.split() else ""
            proper_nouns = {"Deus", "Jesus", "Senhor", "Brasil", "São", "Rio", "Belo", "Porto", "Curitiba", "Salvador", "Fortaleza", "Brasília", "DiaUp"}
            if first_word not in proper_nouns and len(ai_content) > 0:
                ai_content = ai_content[0].lower() + ai_content[1:]
            ai_content = f"{name}, {ai_content}"

    return jsonify({
        "id": "ai",
        "content": ai_content,
        "category": category or "Geral",
        "created_at": datetime.now().isoformat()
    }), 200



def _resolve_user_profile():
    """Obtém o perfil do usuário combinando parâmetros da query e o banco de dados."""
    user_id = (request.args.get("user_id") or "default").strip()
    name_param = (request.args.get("name") or "").strip()
    city_param = (request.args.get("city") or "").strip()
    state_param = (request.args.get("state") or "").strip()
    birth_param = (request.args.get("birth_date") or "").strip()

    profile = {
        "name": name_param or "Amigo(a)",
        "birth_date": birth_param or "1996-01-01",
        "city": city_param or "Sua Cidade",
        "state": state_param or "BR",
    }

    try:
        db = get_db()
        cursor = db.cursor()
        if user_id == "default":
            cursor.execute("SELECT id, user_id, name, birth_date, city, state FROM user_profile WHERE user_id = %s OR id = 1 ORDER BY id ASC LIMIT 1", (user_id,))
        else:
            cursor.execute("SELECT id, user_id, name, birth_date, city, state FROM user_profile WHERE user_id = %s LIMIT 1", (user_id,))
        profile_row = cursor.fetchone()
        if profile_row and profile_row["name"]:
            birth_date_val = profile_row["birth_date"]
            birth_date_str = birth_date_val.isoformat() if hasattr(birth_date_val, "isoformat") else (str(birth_date_val) if birth_date_val else "1996-01-01")
            profile = {
                "name": name_param or profile_row["name"] or profile["name"],
                "birth_date": birth_param or birth_date_str or profile["birth_date"],
                "city": city_param or profile_row["city"] or profile["city"],
                "state": state_param or profile_row["state"] or profile["state"],
            }
    except Exception as e:
        print(f"[DiaUp] Aviso ao resolver perfil do usuário: {e}")

    return profile


def _ensure_name_prefix(text, name):
    """Garante a regra de ouro: toda mensagem começa com '{nome}, '."""
    name = (name or "").strip()
    if not name or not text:
        return text
    if not text.lower().startswith(f"{name.lower()},"):
        for prefix in ["olá,", "olá ", "querido,", "querido ", "querida,", "querida "]:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()
                break
        if not text.lower().startswith(f"{name.lower()},"):
            first_word = text.split()[0] if text.split() else ""
            proper_nouns = {"Deus", "Jesus", "Senhor", "Brasil", "São", "Rio", "Belo", "Porto", "Curitiba", "Salvador", "Fortaleza", "Brasília", "DiaUp"}
            if first_word not in proper_nouns and len(text) > 0:
                text = text[0].lower() + text[1:]
            text = f"{name}, {text}"
    return text


@app.route("/user/horoscope", methods=["GET"])
def get_horoscope():
    profile = _resolve_user_profile()
    sign_id = (request.args.get("sign") or "").strip() or None
    result = ai_engine.generate_horoscope(profile, sign_id=sign_id)
    result["content"] = _ensure_name_prefix(result["content"], profile["name"])
    result["signs"] = [
        {"id": s["id"], "name": s["name"], "symbol": s["symbol"]}
        for s in ai_engine.ZODIAC_SIGNS
    ]
    return jsonify(result), 200


@app.route("/user/tarot", methods=["GET"])
def get_tarot():
    profile = _resolve_user_profile()
    card_id = request.args.get("card_id")
    result = ai_engine.generate_tarot_reading(profile, card_id=card_id)
    result["content"] = _ensure_name_prefix(result["content"], profile["name"])
    return jsonify(result), 200


@app.route("/user/categories", methods=["GET"])
def get_categories():
    official_cats = ["Saúde", "Relacionamento", "Família", "Trabalho", "Projetos", "Amor", "Finanças"]
    db_cats = {}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT COALESCE(NULLIF(TRIM(category), ''), 'Geral') AS category, COUNT(*) AS total
            FROM messages
            GROUP BY COALESCE(NULLIF(TRIM(category), ''), 'Geral')
            """
        )
        db_cats = {row["category"].lower(): row["total"] for row in cursor.fetchall()}
    except Exception as e:
        print(f"[DiaUp] Aviso em get_categories: não foi possível consultar PostgreSQL ({e}). Usando categorias oficiais.")
    
    categories = []
    for cat in official_cats:
        total = db_cats.get(cat.lower(), 1)
        categories.append({"name": cat, "total": total})

    return jsonify({"categories": categories})


@app.route("/api/stats/download", methods=["POST"])
def track_download():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO app_stats (metric, value) VALUES ('downloads', 1)
            ON CONFLICT(metric) DO UPDATE SET value = app_stats.value + 1
            """
        )
        db.commit()
    except Exception as e:
        print(f"[Stats Warning] track_download: {e}")
    return jsonify({"status": "success"}), 200


@app.route("/admin/stats", methods=["GET"])
@admin_required
def get_admin_stats():
    downloads = 0
    registered = 0
    recent_users = []
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT value FROM app_stats WHERE metric = 'downloads'")
        row_dl = cursor.fetchone()
        downloads = row_dl["value"] if row_dl else 0
        
        cursor.execute("SELECT name, birth_date, city, state FROM user_profile WHERE name != 'Viajante' AND name != ''")
        users_up = [dict(r) for r in cursor.fetchall()]
        
        users_us = []
        try:
            cursor.execute("SELECT nome AS name, data_nascimento AS birth_date, cidade AS city, estado AS state FROM usuarios WHERE nome != 'Viajante' AND nome != '' AND nome IS NOT NULL")
            users_us = [dict(r) for r in cursor.fetchall()]
        except Exception as ex:
            print(f"[Admin Stats Warning] Erro ao buscar da tabela usuarios: {ex}")
            
        all_users = []
        seen = set()
        for u in users_up + users_us:
            name_clean = (u.get("name") or "").strip()
            if not name_clean or name_clean.lower() == "viajante":
                continue
            key = (name_clean.lower(), str(u.get("birth_date") or "").strip())
            if key not in seen:
                seen.add(key)
                if hasattr(u.get("birth_date"), "isoformat"):
                    u["birth_date"] = u["birth_date"].isoformat()
                else:
                    u["birth_date"] = str(u.get("birth_date") or "")
                all_users.append(u)
                
        registered = len(all_users)
        recent_users = all_users[:20]
    except Exception as e:
        print(f"[Admin Error] get_admin_stats falhou: {e}")
        
    return jsonify({
        "downloads": downloads,
        "registered": registered,
        "recent_users": recent_users
    }), 200


@app.route("/init_db")
def initialize_database():
    init_db()
    return "Database initialized."


@app.teardown_appcontext
def close_db(error=None):
    try:
        from flask import g
        db = g.pop('db', None)
        if db is not None:
            db.close()
    except Exception:
        pass


if __name__ == "__main__":
    app.run(debug=True)
