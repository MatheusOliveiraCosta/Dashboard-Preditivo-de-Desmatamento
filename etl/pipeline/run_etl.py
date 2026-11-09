import argparse
import sys
import traceback
from datetime import datetime, timezone

from . import (agregados, config, etl_inmet, etl_mapbiomas, etl_prodes, insights, modelo,
               seed_localidades)
from .common import conectar

ETAPAS = {
    "prodes": etl_prodes.executar,
    "mapbiomas": etl_mapbiomas.executar,
    "inmet": etl_inmet.executar,
    # etapas derivadas (rodam depois das fontes)
    "agregados": agregados.executar,   # Brasil = soma dos biomas / média dos estados
    "projecao": modelo.executar,       # modelo de regressão (RF09/RF10)
    "insights": insights.executar,     # textos de insight (RF18)
}


def atualizar_status(conn, sucesso):
    agora = datetime.now(timezone.utc).replace(tzinfo=None) if sucesso else None
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO status_sistema (id, ultima_atualizacao_sucesso, status_ultima_execucao)
            VALUES (1, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                ultima_atualizacao_sucesso = COALESCE(
                    EXCLUDED.ultima_atualizacao_sucesso,
                    status_sistema.ultima_atualizacao_sucesso),
                status_ultima_execucao = EXCLUDED.status_ultima_execucao
            """,
            (agora, "SUCESSO" if sucesso else "FALHA"),
        )


def main():
    parser = argparse.ArgumentParser(description="ETL EcoMonitor")
    parser.add_argument("--fontes", default=",".join(ETAPAS),
                        help="lista separada por vírgula: " + ",".join(ETAPAS))
    parser.add_argument("--sem-llm", action="store_true",
                        help="gera os insights só com templates, sem chamar o Gemini")
    args = parser.parse_args()
    config.USAR_LLM = not args.sem_llm
    fontes = [f.strip() for f in args.fontes.split(",") if f.strip()]
    invalidas = [f for f in fontes if f not in ETAPAS]
    if invalidas:
        parser.error(f"fontes inválidas: {invalidas}")

    conn = conectar()
    ok = True
    etapas = [("localidades", seed_localidades.executar)] + [(f, ETAPAS[f]) for f in fontes]
    for nome, fn in etapas:
        try:
            n = fn(conn)
            conn.commit()
            print(f"[{nome}] {n} linhas")
        except Exception:
            conn.rollback()
            ok = False
            print(f"[{nome}] FALHOU")
            traceback.print_exc()

    atualizar_status(conn, ok)
    conn.commit()
    conn.close()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
