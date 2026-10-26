from . import config
from .common import carregar_desmatamento


def executar(conn):
    n = carregar_desmatamento(conn, config.PRODES_ESTADOS, "ESTADO", "PRODES")
    n += carregar_desmatamento(conn, config.PRODES_BIOMAS, "BIOMA", "PRODES")
    return n
