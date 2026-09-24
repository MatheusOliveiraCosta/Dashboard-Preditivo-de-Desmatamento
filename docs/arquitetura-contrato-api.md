# EcoMonitor Brasil — Arquitetura + Contrato de API

## Arquitetura (visão em camadas)

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Frontend    │─────▶│   API (Backend)   │─────▶│  Camada de   │
│  (Vue)       │◀─────│   FastAPI          │◀─────│  Dados       │
└─────────────┘      └──────────────────┘      └─────────────┘
                                                        │
                                          (futuro, outro card)
                                      PostgreSQL + jobs de ETL
                                      (PRODES / MapBiomas / INMET)
```

- **Frontend (Vue)**: consome a API, não acessa dados diretamente.
- **API (FastAPI)**: expõe os endpoints deste contrato. Na fase atual retorna dados mock (card "Docker Compose + API mock").
- **Camada de dados**: hoje é só a interface/contrato definida aqui. O schema real do banco (DER) e a ingestão (ETL) são tarefas futuras separadas, ainda não decididas.

Stack definida: Python + FastAPI, PostgreSQL com PostGIS (dados geográficos), deploy em nuvem (Render/Railway).

## Contrato de API

| Endpoint | Método | Query params | Retorna |
|---|---|---|---|
| `/api/v1/overview` | GET | `uf`, `ano` | KPIs + pontos do mapa |
| `/api/v1/climate-correlation` | GET | `uf`, `start`, `end` | série cruzando desmatamento x clima |
| `/api/v1/projection` | GET | `uf`, `horizon` | série temporal + intervalo de confiança |
| `/api/v1/export/csv` | GET | `dataset` | arquivo CSV |
| `/api/v1/export/png` | GET | `chart` | imagem do gráfico |

### Exemplo de resposta — `/api/v1/overview`

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
  "mapa": [
    { "lat": -3.1, "lon": -60.0, "intensidade": 0.7 }
  ]
}
```

*(Os demais endpoints seguem o mesmo padrão: resposta JSON tipada, sem implementação real ainda — isso fica para os próximos cards de backend.)*
