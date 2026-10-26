from fastapi import HTTPException

from app import mock_data


def resolver_localidade(codigo: str | None) -> str | None:
    """Ausente = Brasil (None). Código desconhecido = 404."""
    if codigo is None:
        return None
    if mock_data.obter_localidade(codigo) is None:
        raise HTTPException(404, f"Localidade '{codigo}' não encontrada. Veja /api/v1/localidades.")
    return codigo


def validar_periodo(inicio: int, fim: int) -> None:
    if inicio > fim:
        raise HTTPException(422, "O ano inicial não pode ser maior que o ano final.")
