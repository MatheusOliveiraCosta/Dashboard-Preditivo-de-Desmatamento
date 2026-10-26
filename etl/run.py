"""Pipeline de dados (RF01, RF09, RF15). Rode com: docker compose run --rm etl"""
import os

import psycopg2


def main():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    with conn, conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM localidade")
        print("Conexão OK. Localidades no banco:", cur.fetchone()[0])
    conn.close()
    # TODO: 1) ler CSVs do PRODES/MapBiomas/INMET em /data
    #       2) limpar/unificar com pandas e gravar no banco
    #       3) treinar regressão (scikit-learn) e gravar em `projecao`


if __name__ == "__main__":
    main()
