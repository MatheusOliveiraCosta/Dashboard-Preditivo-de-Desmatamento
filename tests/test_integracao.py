"""Pipeline completo (arquivos -> ETL -> PostgreSQL) e depois a API lendo o banco."""
import json
import os
import sys

import pytest
from fastapi.testclient import TestClient

from pipeline import config, insights, run_etl, textos
from tests.dados_teste import ANOS, BIOMAS, ESTADOS, criar_dados


@pytest.fixture
def esperado(conn, tmp_path, monkeypatch):
    """Carrega arquivos de teste, roda o ETL de verdade e devolve os valores esperados."""
    dados = criar_dados(tmp_path)
    raw = tmp_path / "raw"
    monkeypatch.setattr(config, "DATABASE_URL", os.environ["DATABASE_URL"])
    monkeypatch.setattr(config, "PRODES_ESTADOS", raw / "prodes" / "prodes_estados.csv")
    monkeypatch.setattr(config, "PRODES_BIOMAS", raw / "prodes" / "prodes_biomas.csv")
    monkeypatch.setattr(config, "MAPBIOMAS_ESTADOS", raw / "mapbiomas" / "mapbiomas_estados.csv")
    monkeypatch.setattr(config, "MAPBIOMAS_BIOMAS", raw / "mapbiomas" / "mapbiomas_biomas.csv")
    monkeypatch.setattr(config, "INMET_DIR", raw / "inmet")
    monkeypatch.setattr(config, "INMET_ESTACOES_BIOMA", raw / "inmet" / "estacoes_bioma.csv")
    monkeypatch.setattr(config, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(config, "CLIMA_COBERTURA_MIN", 0.01)  # os arquivos de teste são diários
    monkeypatch.setattr(config, "MIN_ESTADOS_BRASIL", 5)
    monkeypatch.setattr(config, "GEMINI_API_KEY", None)

    monkeypatch.setattr(sys, "argv", ["run_etl", "--sem-llm"])
    with pytest.raises(SystemExit) as saida:
        run_etl.main()
    assert saida.value.code in (0, None)
    return dados


@pytest.fixture
def cliente(esperado):
    from app.main import app
    return TestClient(app)


def id_de(cliente, **filtro):
    return next(l["id"] for l in cliente.get("/api/v1/localidades").json()
                if all(l[k] == v for k, v in filtro.items()))


def soma_biomas(esperado, i):
    return round(sum(v[i] for v in esperado["biomas"].values()), 4)


# ---------------------------------------------------------------- dados no banco
def test_brasil_e_a_soma_dos_biomas_e_nao_dos_estados(conn, esperado):
    with conn.cursor() as cur:
        cur.execute("SELECT d.ano, d.area_km2 FROM desmatamento_anual d JOIN localidade l ON l.id=d.localidade_id "
                    "WHERE l.tipo='PAIS' AND d.fonte='PRODES' ORDER BY d.ano")
        brasil = cur.fetchall()
    assert [a for a, _ in brasil] == list(ANOS)
    for i, (_, area) in enumerate(brasil):
        assert area == pytest.approx(soma_biomas(esperado, i), rel=1e-6)


def test_clima_do_brasil_so_existe_com_estados_suficientes(conn, esperado):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM dado_climatico c JOIN localidade l ON l.id=c.localidade_id WHERE l.tipo='PAIS'")
        assert cur.fetchone()[0] == len(ANOS)  # 6 estados >= MIN_ESTADOS_BRASIL (5)
        cur.execute("SELECT count(DISTINCT l.nome) FROM dado_climatico c JOIN localidade l ON l.id=c.localidade_id WHERE l.tipo='BIOMA'")
        assert cur.fetchone()[0] == 4  # biomas com estação: Amazônia, Cerrado, Mata Atlântica, Caatinga


def test_projecao_e_insights_gerados_para_todas_as_localidades_com_dado(conn, esperado):
    with conn.cursor() as cur:
        cur.execute("SELECT count(DISTINCT localidade_id), count(*) FROM projecao")
        n_loc, n_linhas = cur.fetchone()
        cur.execute("SELECT count(DISTINCT localidade_id) FROM desmatamento_anual")
        assert n_loc == cur.fetchone()[0]
        assert n_linhas == n_loc * config.ANOS_PROJECAO
        cur.execute("SELECT tela, count(*) FROM insight GROUP BY tela")
        telas = dict(cur.fetchall())
    assert set(telas) == {"VISAO_GERAL", "CORRELACAO_CLIMATICA", "PROJECAO_TENDENCIA"}
    assert telas["VISAO_GERAL"] == telas["PROJECAO_TENDENCIA"] == n_loc
    assert telas["CORRELACAO_CLIMATICA"] < n_loc  # sem clima em alguns estados/biomas


def test_metricas_de_validacao_do_modelo_foram_salvas(esperado):
    caminho = config.PROCESSED_DIR / "metricas_modelo.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert "Brasil" in dados["localidades"] and dados["localidades"]["Brasil"]["n_teste"] == 3
    assert dados["localidades"]["Brasil"]["mae"] is not None


def test_etl_pode_rodar_de_novo_sem_duplicar(conn, esperado, monkeypatch):
    def contagens():
        with conn.cursor() as cur:
            cur.execute("SELECT (SELECT count(*) FROM desmatamento_anual), (SELECT count(*) FROM dado_climatico),"
                        "(SELECT count(*) FROM projecao), (SELECT count(*) FROM insight), (SELECT count(*) FROM localidade)")
            return cur.fetchone()
    conn.commit()
    antes = contagens()
    monkeypatch.setattr(sys, "argv", ["run_etl", "--sem-llm"])
    with pytest.raises(SystemExit):
        run_etl.main()
    conn.commit()
    assert contagens() == antes


def test_status_do_sistema_registra_sucesso(conn, esperado):
    with conn.cursor() as cur:
        cur.execute("SELECT status_ultima_execucao, ultima_atualizacao_sucesso FROM status_sistema WHERE id = 1")
        status, momento = cur.fetchone()
    assert status == "SUCESSO" and momento is not None


# ---------------------------------------------------------------- API
def test_localidades(cliente):
    r = cliente.get("/api/v1/localidades")
    assert r.status_code == 200
    lista = r.json()
    assert len(lista) == 27 + 6 + 1
    assert lista[0] == {"id": lista[0]["id"], "nome": "Brasil", "sigla_uf": None, "tipo": "PAIS", "regiao": None}
    assert {l["tipo"] for l in lista} == {"PAIS", "ESTADO", "BIOMA"}
    assert [l["tipo"] for l in lista] == sorted((l["tipo"] for l in lista), key=["PAIS", "ESTADO", "BIOMA"].index)


def test_overview_do_brasil(cliente, esperado):
    r = cliente.get("/api/v1/overview")
    assert r.status_code == 200
    d = r.json()
    ultimo = len(ANOS) - 1
    kpi = d["kpis"][0]
    assert kpi["region"] == "BR" and kpi["ano_referencia"] == 2023
    assert kpi["area_desmatada_km2"] == pytest.approx(soma_biomas(esperado, ultimo), rel=1e-6)
    anterior = soma_biomas(esperado, ultimo - 1)
    assert kpi["variacao_percentual"] == pytest.approx((kpi["area_desmatada_km2"] - anterior) / anterior * 100, rel=1e-6)
    maior = max(BIOMAS, key=lambda b: esperado["biomas"][b][ultimo])
    assert d["bioma_critico"] == maior
    assert [p["ano"] for p in d["serie_historica"]] == list(ANOS)
    assert d["insight"].startswith("Brasil: a área desmatada em 2023 foi de ")
    assert d["atualizado_em"] is not None and d["atualizado_em"].endswith(("Z", "+00:00"))


def test_overview_de_um_estado_e_periodo(cliente, esperado):
    pa = id_de(cliente, nome="Pará")
    d = cliente.get(f"/api/v1/overview?localidade={pa}&ano_inicio=2018&ano_fim=2021").json()
    assert d["kpis"][0]["region"] == "PA" and d["kpis"][0]["ano_referencia"] == 2021
    assert [p["ano"] for p in d["serie_historica"]] == [2018, 2019, 2020, 2021]
    i = list(ANOS).index(2021)
    # o Pará tem PRODES e MapBiomas: a API usa o PRODES
    assert d["kpis"][0]["area_desmatada_km2"] == pytest.approx(esperado["estados"]["PA"][i])


def test_overview_de_bioma_usa_o_nome_como_regiao(cliente):
    d = cliente.get(f"/api/v1/overview?localidade={id_de(cliente, nome='Cerrado')}").json()
    assert d["kpis"][0]["region"] == "Cerrado"


def test_localidade_so_com_mapbiomas_usa_mapbiomas_em_km2(cliente):
    ac = id_de(cliente, nome="Acre")
    d = cliente.get(f"/api/v1/overview?localidade={ac}&ano_inicio=2004&ano_fim=2004").json()
    assert d["kpis"][0]["area_desmatada_km2"] == pytest.approx(100.0)  # 10.000 ha = 100 km²


def test_erros_do_overview(cliente):
    assert cliente.get("/api/v1/overview?localidade=99999").status_code == 404
    assert cliente.get("/api/v1/overview?ano_inicio=2020&ano_fim=2010").status_code == 422
    assert cliente.get("/api/v1/overview?ano_inicio=2090&ano_fim=2095").status_code == 404
    sem_dado = id_de(cliente, nome="Roraima")
    r = cliente.get(f"/api/v1/overview?localidade={sem_dado}")
    assert r.status_code == 404 and "Roraima" in r.json()["detail"]


def test_climate_correlation(cliente, esperado):
    d = cliente.get("/api/v1/climate-correlation").json()
    assert [p["ano"] for p in d["serie"]] == list(ANOS)
    ind = d["indicadores"]
    assert -1 <= ind["coef_correlacao_temperatura"] <= 1 and -1 <= ind["coef_correlacao_precipitacao"] <= 1
    temps = [p["temperatura_media_c"] for p in d["serie"]]
    assert ind["anomalia_termica_c"] == pytest.approx(temps[-1] - sum(temps) / len(temps))
    assert all(15 < t < 35 and p["precipitacao_mm"] > 0 for t, p in zip(temps, d["serie"]))
    assert d["insight"].startswith("Brasil: entre 2004 e 2023")
    # estado e bioma com estação
    for nome in ("Pará", "Cerrado"):
        assert cliente.get(f"/api/v1/climate-correlation?localidade={id_de(cliente, nome=nome)}").status_code == 200


def test_climate_correlation_sem_estacao_e_periodo(cliente):
    sem_clima = id_de(cliente, nome="Pampa")  # sem estação mapeada
    assert cliente.get(f"/api/v1/climate-correlation?localidade={sem_clima}").status_code == 404
    d = cliente.get("/api/v1/climate-correlation?ano_inicio=2015&ano_fim=2019").json()
    assert [p["ano"] for p in d["serie"]] == [2015, 2016, 2017, 2018, 2019]


def test_projection_geral_e_regional(cliente, esperado):
    d = cliente.get("/api/v1/projection").json()
    assert d["regional"] is None
    g = d["geral"]
    assert [p["ano"] for p in g["projecao"]] == list(range(2024, 2031))
    assert [p["ano"] for p in g["serie_historica"]] == list(range(2018, 2024))
    for p in g["projecao"]:
        assert 0 <= p["intervalo_inferior"] <= p["valor_projetado_km2"] <= p["intervalo_superior"]
    assert g["insight"].startswith("Brasil: se a tendência atual continuar")

    pa = id_de(cliente, nome="Pará")
    r = cliente.get(f"/api/v1/projection?localidade={pa}&horizonte=3").json()
    assert len(r["regional"]["projecao"]) == 3 and len(r["geral"]["projecao"]) == 3
    assert r["regional"]["insight"].startswith("Pará: ")
    brasil = id_de(cliente, tipo="PAIS")
    assert cliente.get(f"/api/v1/projection?localidade={brasil}").json()["regional"] is None


def test_projection_erros(cliente):
    assert cliente.get("/api/v1/projection?localidade=99999").status_code == 404
    assert cliente.get("/api/v1/projection?horizonte=0").status_code == 422
    assert cliente.get(f"/api/v1/projection?localidade={id_de(cliente, nome='Roraima')}").status_code == 404


def test_projecao_tem_a_tendencia_dos_dados(cliente):
    """Séries do teste caem ~4%/ano da base: a projeção deve continuar caindo."""
    g = cliente.get("/api/v1/projection").json()["geral"]
    assert g["projecao"][-1]["valor_projetado_km2"] < g["serie_historica"][0]["area_km2"]


def test_health(cliente):
    assert cliente.get("/api/v1/health").json() == {"status": "ok"}


# ---------------------------------------------------------------- LLM (opcional)
def test_insights_com_llm_aceitam_so_texto_fiel(conn, esperado, monkeypatch):
    chamadas = []

    def falso_gemini(api_key, modelo):
        def reescrever(texto):
            chamadas.append(texto)
            # devolve o mesmo texto com uma pequena mudança de estilo (mesmos números)
            return texto.replace("a área desmatada", "o desmatamento")
        return reescrever

    monkeypatch.setattr(config, "GEMINI_API_KEY", "chave")
    monkeypatch.setattr(config, "GEMINI_MODEL", "modelo-x")
    monkeypatch.setattr(config, "USAR_LLM", True)
    monkeypatch.setattr(textos, "criar_reescritor_gemini", falso_gemini)
    n = insights.executar(conn)
    conn.commit()
    assert len(chamadas) == n
    with conn.cursor() as cur:
        cur.execute("SELECT texto_gerado FROM insight WHERE tela='VISAO_GERAL' LIMIT 1")
        assert "o desmatamento em 2023" in cur.fetchone()[0]


def test_llm_que_inventa_numero_e_ignorado_e_sem_chave_usa_template(conn, esperado, monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "chave")
    monkeypatch.setattr(config, "GEMINI_MODEL", "modelo-x")
    monkeypatch.setattr(config, "USAR_LLM", True)
    monkeypatch.setattr(textos, "criar_reescritor_gemini", lambda k, m: (lambda t: "O desmatamento caiu 987654% em 2023."))
    insights.executar(conn)
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM insight WHERE texto_gerado LIKE '%987654%'")
        assert cur.fetchone()[0] == 0
