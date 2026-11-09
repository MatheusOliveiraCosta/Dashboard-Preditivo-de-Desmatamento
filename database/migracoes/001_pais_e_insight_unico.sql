-- Migração 001 — para bancos criados com a versão anterior do schema.sql.
-- Bancos novos já nascem com isto; não é preciso rodar.
--
-- 1) localidade.tipo passa a aceitar 'PAIS' (registro "Brasil": série, projeção e insight próprios).
-- 2) insight passa a ter um único texto por (localidade, tela).
--
-- Como rodar (com os containers no ar):
--   docker compose exec -T db psql -U postgres -d ecomonitor < database/migracoes/001_pais_e_insight_unico.sql

BEGIN;

ALTER TABLE localidade DROP CONSTRAINT IF EXISTS localidade_tipo_check;
ALTER TABLE localidade
    ADD CONSTRAINT localidade_tipo_check CHECK (tipo IN ('PAIS', 'ESTADO', 'BIOMA'));

-- mantém só o texto mais recente de cada (localidade, tela) antes de criar a restrição
DELETE FROM insight a
USING insight b
WHERE a.localidade_id = b.localidade_id AND a.tela = b.tela AND a.id < b.id;

ALTER TABLE insight DROP CONSTRAINT IF EXISTS insight_localidade_tela_key;
ALTER TABLE insight
    ADD CONSTRAINT insight_localidade_tela_key UNIQUE (localidade_id, tela);

COMMIT;
