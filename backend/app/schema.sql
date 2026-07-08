DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS user_profile;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS app_stats;

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_profile (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE,
    name TEXT NOT NULL,
    birth_date DATE,
    city TEXT,
    state TEXT
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT,
    data_nascimento DATE,
    cidade TEXT,
    estado TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_stats (
    metric TEXT PRIMARY KEY,
    value INTEGER DEFAULT 0
);

INSERT INTO user_profile (id, user_id, name, birth_date, city, state)
VALUES (1, 'default', 'Viajante', '1996-01-01', 'São Paulo', 'SP');

INSERT INTO app_stats (metric, value) VALUES ('downloads', 12);
