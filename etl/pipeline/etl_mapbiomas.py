from . import config
from .common import carregar_desmatamento


def executar(conn):
    # banco guarda km²; 1 ha = 0,01 km²
    fator = 0.01 if config.MAPBIOMAS_UNIDADE == "ha" else 1.0
    n = carregar_desmatamento(conn, config.MAPBIOMAS_ESTADOS, "ESTADO", "MAPBIOMAS", fator)
    n += carregar_desmatamento(conn, config.MAPBIOMAS_BIOMAS, "BIOMA", "MAPBIOMAS", fator)
    return n
