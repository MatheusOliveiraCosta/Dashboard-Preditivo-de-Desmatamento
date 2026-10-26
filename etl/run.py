"""Pipeline de dados (RF01, RF09, RF15). Rode com: docker compose run --rm etl

Para uma fonte só:
    docker compose run --rm etl python run.py --fontes prodes
"""
from pipeline.run_etl import main

if __name__ == "__main__":
    main()
