"""Pipeline de dados (RF01, RF09, RF15, RF18). Rode com: docker compose run --rm etl

Para uma fonte só:
    docker compose run --rm etl python run.py --fontes prodes

Só recalcular o Brasil, a projeção e os textos (sem reler os arquivos):
    docker compose run --rm etl python run.py --fontes agregados,projecao,insights
"""
from pipeline.run_etl import main

if __name__ == "__main__":
    main()
