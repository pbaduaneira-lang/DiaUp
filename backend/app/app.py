import random
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from .database import get_db, init_db
from . import ai_engine

app = Flask(__name__)
app.secret_key = "diaup_secret_key_super_segura_1016"

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
        return jsonify({"error": "Falha de conexão com o banco na nuvem. Verifique se a variável DATABASE_URL na Vercel está com a URL do Connection Pooler (IPv4) do Supabase."}), 503


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
        return jsonify({"error": "Erro ao conectar com o banco na nuvem."}), 503


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
        return jsonify({"error": "Erro de conexão com o banco na nuvem."}), 503


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


@app.route("/user/profile", methods=["POST"])
def update_user_profile():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    name = (data.get("name") or "Viajante").strip()
    birth_date = (data.get("birth_date") or "1996-01-01").strip()
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

    if saved_messages and random.random() < 0.5:
        ai_content = random.choice(saved_messages)
    else:
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
        
        cursor.execute("SELECT COUNT(*) AS total FROM user_profile WHERE name != 'Viajante' AND name != ''")
        row_reg = cursor.fetchone()
        registered = row_reg["total"] if row_reg else 0
        
        cursor.execute("SELECT name, birth_date, city, state FROM user_profile WHERE name != 'Viajante' AND name != '' ORDER BY id DESC LIMIT 10")
        for row in cursor.fetchall():
            item = dict(row)
            if hasattr(item.get("birth_date"), "isoformat"):
                item["birth_date"] = item["birth_date"].isoformat()
            else:
                item["birth_date"] = str(item.get("birth_date") or "")
            recent_users.append(item)
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
