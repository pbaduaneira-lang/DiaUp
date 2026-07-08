import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/DiaUp")

_schema_ensured = False

def ensure_schema(force=False):
    global _schema_ensured
    if _schema_ensured and not force:
        return
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id SERIAL PRIMARY KEY,
                user_id TEXT UNIQUE,
                name TEXT NOT NULL,
                birth_date DATE,
                city TEXT,
                state TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT,
                data_nascimento DATE,
                cidade TEXT,
                estado TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS user_id TEXT;")
        cur.execute("ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS name TEXT;")
        cur.execute("ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS birth_date DATE;")
        cur.execute("ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS city TEXT;")
        cur.execute("ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS state TEXT;")
        cur.execute("UPDATE user_profile SET user_id = 'default' WHERE id = 1 AND (user_id IS NULL OR user_id = '')")
        cur.execute("UPDATE user_profile SET name = 'Viajante' WHERE id = 1 AND (name IS NULL OR name = '')")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profile_user_id ON user_profile(user_id)")
        
        cur.execute("SELECT 1 FROM user_profile WHERE user_id = 'default' OR id = 1")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO user_profile (id, user_id, name, birth_date, city, state)
                VALUES (1, 'default', 'Viajante', '1996-01-01', 'São Paulo', 'SP')
            """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_stats (
                metric TEXT PRIMARY KEY,
                value INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            INSERT INTO app_stats (metric, value) VALUES ('downloads', 12)
            ON CONFLICT (metric) DO UPDATE SET value = EXCLUDED.value WHERE app_stats.value < EXCLUDED.value
        """)
        
        # Migração e padronização para as 5 categorias oficiais
        cur.execute("UPDATE messages SET category = 'Saúde' WHERE category IN ('Autoajuda', 'autoajuda', 'Surpresa', 'surpresa')")
        cur.execute("UPDATE messages SET category = 'Projetos' WHERE category IN ('Sucesso', 'sucesso')")
        cur.execute("UPDATE messages SET category = 'Trabalho' WHERE category IN ('Inspiração', 'inspiração')")
        cur.execute("UPDATE messages SET category = 'Relacionamento' WHERE id % 2 = 0 AND (category IS NULL OR category = '' OR category IN ('Geral', 'geral'))")
        cur.execute("UPDATE messages SET category = 'Família' WHERE category IS NULL OR category = '' OR category IN ('Geral', 'geral')")
    conn.close()
    _schema_ensured = True

def get_db():
    ensure_schema()
    try:
        from flask import has_app_context, g
        if has_app_context():
            if 'db' not in g:
                g.db = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
            return g.db
    except ImportError:
        pass
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)

def init_db():
    global _schema_ensured
    conn = get_db()
    try:
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            with conn.cursor() as cur:
                cur.execute(f.read())
        conn.commit()
    finally:
        conn.close()
    _schema_ensured = False
    ensure_schema(force=True)
    print('Database initialized.')

if __name__ == '__main__':
    init_db()

