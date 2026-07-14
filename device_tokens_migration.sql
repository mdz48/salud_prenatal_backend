-- El proyecto no usa Alembic (Base.metadata.create_all no altera columnas
-- existentes), así que este script se corre a mano una sola vez contra la
-- base ya desplegada para reflejar el cambio de device_token_model.py:
-- user_id pasa a ser nullable (token de dispositivo, no de sesión) y su FK
-- pasa de ON DELETE CASCADE a ON DELETE SET NULL.
--
-- Busca la(s) FK real(es) de device_tokens.user_id -> users.user_id por
-- catálogo (pg_constraint), en vez de asumir el nombre por convención
-- (device_tokens_user_id_fkey): si el nombre real fuera otro, un DROP
-- CONSTRAINT IF EXISTS con el nombre adivinado sería un no-op silencioso y
-- quedarían DOS foreign keys activas (la vieja CASCADE + la nueva SET
-- NULL), anulando el cambio.

DO $$
DECLARE
    fk_name text;
BEGIN
    FOR fk_name IN
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = ANY(con.conkey)
        WHERE con.contype = 'f'
          AND rel.relname = 'device_tokens'
          AND att.attname = 'user_id'
    LOOP
        EXECUTE format('ALTER TABLE device_tokens DROP CONSTRAINT %I', fk_name);
    END LOOP;
END $$;

ALTER TABLE device_tokens ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE device_tokens
    ADD CONSTRAINT device_tokens_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL;
