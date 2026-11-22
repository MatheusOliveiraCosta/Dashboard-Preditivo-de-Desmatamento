# Dashboard-Preditivo-de-Desmatamento
Desenvolvimento de um Dashboard Preditivo de Dados Ambientais, concebido primariamente como uma ferramenta interativa de divulgação científica. O sistema solucionará o distanciamento entre o dado bruto e o cidadão, centralizando e cruzando dados tabulares históricos em uma plataforma web didática.
# EcoMonitor Brasil — Dashboard Preditivo de Desmatamento

Projeto da disciplina Oficina de Integração (UTFPR), em parceria com o projeto de extensão
"Despertar para a Ciência". Dados públicos: PRODES/INPE, MapBiomas e INMET.

```
ecomonitor-frontend/   Vue 3 + TypeScript (as 4 telas)
backend/               API FastAPI (somente leitura)
etl/                   carga dos dados, Brasil, projeção e textos de insight
database/              schema.sql (PostgreSQL) e migrações
docs/                  arquitetura e contrato da API
tests/                 testes de ponta a ponta (ETL → banco → API)
```

Contrato da API, regras dos dados e etapas do ETL: [`docs/arquitetura-contrato-api.md`](docs/arquitetura-contrato-api.md).

## 📁 Como baixar os arquivos da `main` e rodar (Git LFS + Docker)

Os arquivos `.zip` do INMET (`2024.zip`, `2025.zip` e `2026.zip`) estão versionados com **Git LFS**. Sem ele, o Git baixa apenas arquivos de texto pequenos (ponteiros) e o ETL falha ao tentar ler os dados.

### 1. Instale e ative o Git LFS

- **Windows:** baixe e instale em <https://git-lfs.com/> e reinicie o VS Code/terminal.
- **Linux / GitHub Codespaces:**
  ```bash
  sudo apt-get update && sudo apt-get install -y git-lfs
  ```
- Em qualquer sistema, ative o Git LFS uma única vez:
  ```bash
  git lfs install
  ```

### 2. Baixe a `main` atualizada e puxe os `.zip` reais

Na pasta raiz do projeto, execute:

```bash
git checkout main
git pull origin main
git lfs pull
```

> Confira em `data/raw/inmet/` se os arquivos `.zip` têm mais de 85 MB cada (e não apenas alguns bytes) e se `data/raw/prodes/prodes_estados.csv` está presente.

*(Opcional — série histórica completa de 2004 a 2026: caso os 21 arquivos `.zip` estejam disponíveis na aba **Releases** do repositório, baixe-os e coloque todos dentro de `data/raw/inmet/` antes do próximo passo.)*

### 3. Suba o banco no Docker e rode o ETL

Como o GitHub não envia o banco de dados já preenchido, execute o ETL para carregar os arquivos no PostgreSQL local:

```bash
cp .env.example .env
docker compose up -d db
docker compose run --rm etl
docker compose up -d
```

Verifique se os containers estão ativos com `docker compose ps` e acesse <http://localhost:8000/docs>.

## Rodando com dados reais

1. `cp .env.example .env` (e ajuste as senhas, se quiser).
2. Coloque os arquivos de entrada em `data/raw/` (a pasta não vai para o Git por padrão):
  - `prodes/prodes_estados.csv` e `prodes/prodes_biomas.csv`
  - `mapbiomas/mapbiomas_estados.csv` e `mapbiomas/mapbiomas_biomas.csv` (opcional)
  - `inmet/` com os CSV ou ZIP das estações do BDMEP + `inmet/estacoes_bioma.csv`

   Para o Brasil ficar completo, carregue os **6 biomas** do PRODES.
3. Suba o banco e a API: `docker compose up -d db backend`
4. Rode o ETL: `docker compose run --rm etl`
   (só Brasil, projeção e textos: `docker compose run --rm etl python run.py --fontes agregados,projecao,insights`)
5. Confira: <http://localhost:8000/docs>
6. Frontend: em `ecomonitor-frontend`, `cp .env.example .env`, troque `VITE_USE_MOCK=true` por `false` e rode `npm install && npm run dev`.

Banco já existente de uma versão anterior? Aplique a migração (não precisa apagar dados):
`docker compose exec -T db psql -U postgres -d ecomonitor < database/migracoes/001_pais_e_insight_unico.sql`

### Textos com o Gemini (opcional)

Sem configuração, os textos de insight saem de templates. Para o Gemini reescrevê-los, defina
`GEMINI_API_KEY` e `GEMINI_MODEL` no `.env` (o nome do modelo muda com o tempo; confira em
<https://ai.google.dev/gemini-api/docs/models>). O texto do modelo só é usado se não trouxer nenhum
número diferente do cálculo; senão, vale o template. Para desligar: `... python run.py --sem-llm`.

## Testes

Precisam de um PostgreSQL (o banco informado é **apagado e recriado**):

```
pip install -r etl/requirements.txt -r backend/requirements-dev.txt
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecomonitor_test pytest
```

Os testes geram arquivos de entrada no formato real, rodam o ETL de verdade e consultam a API; um deles
compara a resposta da API com os mocks do frontend para garantir que o contrato não se separa.
