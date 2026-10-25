BEGIN;

CREATE TABLE localidade (
    id        INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    sigla_uf  VARCHAR(2),                       -- nulo para biomas
    tipo      VARCHAR(20)  NOT NULL
              CHECK (tipo IN ('ESTADO', 'BIOMA')),
    regiao    VARCHAR(45),
    UNIQUE (nome, tipo)
);

CREATE TABLE desmatamento_anual (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    localidade_id  INT NOT NULL REFERENCES localidade(id),
    ano            INT NOT NULL,
    area_km2       DOUBLE PRECISION NOT NULL CHECK (area_km2 >= 0),
    fonte          VARCHAR(45) NOT NULL
                   CHECK (fonte IN ('PRODES', 'MAPBIOMAS')),
    UNIQUE (localidade_id, ano, fonte)
);

CREATE TABLE dado_climatico (
    id                   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    localidade_id        INT NOT NULL REFERENCES localidade(id),
    ano                  INT NOT NULL,
    temperatura_media_c  DOUBLE PRECISION,
    precipitacao_mm      DOUBLE PRECISION CHECK (precipitacao_mm >= 0),
    fonte                VARCHAR(45) NOT NULL DEFAULT 'INMET'
                         CHECK (fonte IN ('INMET')),
    UNIQUE (localidade_id, ano, fonte)
);

CREATE TABLE projecao (
    id                   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    localidade_id        INT NOT NULL REFERENCES localidade(id),
    ano_base             INT NOT NULL,
    ano_projetado        INT NOT NULL,
    valor_projetado_km2  DOUBLE PRECISION NOT NULL CHECK (valor_projetado_km2 >= 0),
    intervalo_inferior   DOUBLE PRECISION CHECK (intervalo_inferior >= 0),
    intervalo_superior   DOUBLE PRECISION CHECK (intervalo_superior >= 0),
    CHECK (ano_projetado > ano_base),
    UNIQUE (localidade_id, ano_base, ano_projetado)
);

CREATE TABLE insight (
    id               INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    localidade_id    INT NOT NULL REFERENCES localidade(id),
    tela             VARCHAR(20) NOT NULL
                     CHECK (tela IN ('VISAO_GERAL', 'CORRELACAO_CLIMATICA', 'PROJECAO_TENDENCIA')),
    texto_gerado     TEXT NOT NULL,
    metricas_origem  JSON            -- números que originaram o texto
);

-- Linha única (id = 1)
CREATE TABLE status_sistema (
    id                          INT PRIMARY KEY CHECK (id = 1),
    ultima_atualizacao_sucesso  TIMESTAMP,
    status_ultima_execucao      VARCHAR(20)
                                CHECK (status_ultima_execucao IN ('SUCESSO', 'FALHA'))
);

-- Índices nas FKs / filtros principais da API
CREATE INDEX idx_desmatamento_localidade_ano ON desmatamento_anual (localidade_id, ano);
CREATE INDEX idx_clima_localidade_ano        ON dado_climatico (localidade_id, ano);
CREATE INDEX idx_projecao_localidade         ON projecao (localidade_id, ano_base);
CREATE INDEX idx_insight_localidade_tela     ON insight (localidade_id, tela);

COMMIT;