# EcoMonitor Brasil - Arquitetura + Contrato de API

## Arquitetura (visão em camadas)
```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Frontend    │─────▶│   API (Backend)   │─────▶│  Camada de   │
│  (Vue)       │◀─────│   FastAPI          │◀─────│  Dados       │
└─────────────┘      └──────────────────┘      └─────────────┘
                                                        │
                                      PostgreSQL + jobs de ETL
                                      (PRODES / MapBiomas / INMET)
```

- **Frontend (Vue)**: consome a API, não acessa dados diretamente.
- **API (FastAPI)**: expõe os endpoints deste contrato, na mesma base de código do serviço de dados/modelo.
- **Camada de dados**: schema já definido no DER (tabelas `localidade`, `desmatamento_anual`, `dado_climatico`, `projecao`, `insight`, `status_sistema`); a ingestão (ETL) roda de forma agendada, não em tempo real.

Stack definida: Python + FastAPI, PostgreSQL (sem PostGIS não há geometria envolvida, só coordenadas simples e dados tabulares), deploy em nuvem (Render/Railway).

## Contrato de API

| Endpoint | Método | Query params | Retorna |
|---|---|---|---|
| `/api/v1/localidades` | GET | - | Lista de estados/biomas para o filtro |
| `/api/v1/overview` | GET | `localidade` (opcional; ausente = Brasil), `ano_inicio`, `ano_fim` | KPIs + série histórica + insight + data de atualização |
| `/api/v1/climate-correlation` | GET | `localidade`, `start`, `end` | série cruzando desmatamento x clima + insight |
| `/api/v1/projection` | GET | `localidade`, `horizon` | série histórica + projeção regional **e** nacional + insight |

*(Exportação de CSV/PNG saiu do contrato fica client-side no Vue: CSV a partir dos dados já carregados, PNG via exportação do próprio canvas do gráfico, sem precisar de endpoint no backend.)*

### Exemplo de resposta `/api/v1/overview`

```json
{
  "kpis": [
    {
      "region": "AM",
      "area_desmatada_km2": 1234.5,
      "variacao_percentual": 3.2,
      "ano_referencia": 2024
    }
  ],
  "serie_historica": [
    { "ano": 2004, "area_km2": 27772 },
    { "ano": 2023, "area_km2": 9001 }
  ],
  "insight": "A área desmatada em 2023 caiu 22% em relação a 2022.",
  "atualizado_em": "2026-08-15T00:00:00Z"
}
```

*(Os demais endpoints seguem o mesmo padrão: resposta JSON tipada, sem implementação real ainda isso fica para os próximos cards de backend.)*
