"""Garante que a API devolve a MESMA estrutura dos mocks do frontend (ecomonitor-frontend/src/mocks),
isto é, que o frontend funciona trocando VITE_USE_MOCK=false sem ajustes."""
import json

import pytest

from tests.conftest import RAIZ
from tests.test_integracao import cliente, esperado, id_de  # noqa: F401  (fixtures)

MOCKS = RAIZ / "ecomonitor-frontend" / "src" / "mocks"


def carregar(nome):
    return json.loads((MOCKS / nome).read_text(encoding="utf-8"))


def comparar(api, mock, caminho="$"):
    """Mesmas chaves em todos os níveis; null em qualquer um dos lados é aceito."""
    if api is None or mock is None:
        return
    assert type(api) is type(mock) or {type(api), type(mock)} <= {int, float}, f"{caminho}: tipos diferentes"
    if isinstance(mock, dict):
        assert set(api) == set(mock), f"{caminho}: chaves diferentes: {sorted(set(api) ^ set(mock))}"
        for chave in mock:
            comparar(api[chave], mock[chave], f"{caminho}.{chave}")
    elif isinstance(mock, list) and mock and api:
        comparar(api[0], mock[0], f"{caminho}[0]")


@pytest.mark.parametrize("arquivo, rota", [
    ("overview.json", "/api/v1/overview"),
    ("climate-correlation.json", "/api/v1/climate-correlation"),
    ("localidades.json", "/api/v1/localidades"),
])
def test_estrutura_igual_aos_mocks(cliente, arquivo, rota):  # noqa: F811
    comparar(cliente.get(rota).json(), carregar(arquivo))


def test_estrutura_da_projecao_igual_ao_mock(cliente):  # noqa: F811
    estado = id_de(cliente, nome="Pará")
    comparar(cliente.get(f"/api/v1/projection?localidade={estado}").json(), carregar("projection.json"))
