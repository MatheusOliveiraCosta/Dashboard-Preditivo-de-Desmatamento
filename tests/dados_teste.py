"""Gera arquivos de entrada no MESMO formato que o ETL lê (PRODES/MapBiomas em CSV e
estações do INMET no layout do BDMEP), com valores sintéticos e determinísticos."""
from datetime import date, timedelta
from pathlib import Path

ANOS = range(2004, 2024)

# sigla -> (nome, base km²/ano). Só estes estados têm dado.
ESTADOS = {"AM": ("Amazonas", 1500), "PA": ("Pará", 4000), "MT": ("Mato Grosso", 2500),
           "GO": ("Goiás", 600), "SP": ("São Paulo", 80), "BA": ("Bahia", 700)}
BIOMAS = {"Amazônia": 9000, "Caatinga": 700, "Cerrado": 6000,
          "Mata Atlântica": 300, "Pampa": 60, "Pantanal": 150}
# estação INMET -> (UF, bioma)
ESTACOES = {"A001": ("AM", "Amazônia"), "A002": ("PA", "Amazônia"), "A003": ("MT", "Cerrado"),
            "A004": ("GO", "Cerrado"), "A005": ("SP", "Mata Atlântica"), "A006": ("BA", "Caatinga")}


def valor_prodes(base, ano, k):
    """Série decrescente com oscilação, sempre positiva."""
    return round(base * (1.6 - 0.04 * (ano - 2004) + 0.05 * ((ano * 7 + k * 3) % 5)), 1)


def _csv(caminho: Path, cabecalho, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join([cabecalho, *linhas]) + "\n", encoding="utf-8")


def _estacao(uf, codigo, k):
    linhas = ["REGIÃO:;N", f"UF:;{uf}", f"ESTAÇÃO:;ESTACAO {codigo}", f"CODIGO (WMO):;{codigo}",
              "LATITUDE:;-3,1", "LONGITUDE:;-60,0", "ALTITUDE:;50", "DATA DE FUNDAÇÃO:;01/01/2000",
              "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);TEMPERATURA DO AR - BULBO SECO, HORARIA (°C);"]
    dia = date(2003, 8, 1)  # o ETL usa o ano PRODES (agosto a julho)
    while dia <= date(2023, 7, 31):
        prec = (1 + ((dia.toordinal() * 13 + k) % 9)) * 0.7
        temp = 24 + k * 0.3 + 0.05 * (dia.year - 2003) + ((dia.toordinal() + k) % 7) * 0.2
        prec_txt = "-9999" if dia.toordinal() % 50 == 0 else f"{prec:.1f}".replace(".", ",")
        temp_txt = f"{temp:.1f}".replace(".", ",")
        linhas.append(f"{dia:%Y/%m/%d};0000 UTC;{prec_txt};{temp_txt};")
        dia += timedelta(days=1)
    return "\n".join(linhas) + "\n"


def criar_dados(raiz: Path):
    """Cria data/raw/... em `raiz` e devolve os valores esperados para conferência."""
    prodes = raiz / "raw" / "prodes"
    mapbiomas = raiz / "raw" / "mapbiomas"
    inmet = raiz / "raw" / "inmet"

    estados = {sigla: [valor_prodes(base, a, k) for a in ANOS] for k, (sigla, (_, base)) in enumerate(ESTADOS.items())}
    biomas = {nome: [valor_prodes(base, a, k) for a in ANOS] for k, (nome, base) in enumerate(BIOMAS.items())}

    _csv(prodes / "prodes_estados.csv", "estado,ano,area_km2",
         [f"{sigla},{a},{v}" for sigla, vals in estados.items() for a, v in zip(ANOS, vals)])
    _csv(prodes / "prodes_biomas.csv", "bioma,ano,area_km2",
         [f"{nome},{a},{v}" for nome, vals in biomas.items() for a, v in zip(ANOS, vals)])

    # MapBiomas (em hectares): Pará (também tem PRODES, que deve prevalecer) e Acre (só MapBiomas)
    _csv(mapbiomas / "mapbiomas_estados.csv", "estado,ano,area_ha",
         [f"{uf},{a},{10000 + 100 * (a - 2004)}" for uf in ("PA", "AC") for a in ANOS])

    inmet.mkdir(parents=True, exist_ok=True)
    for k, (codigo, (uf, _)) in enumerate(ESTACOES.items()):
        (inmet / f"INMET_{uf}_{codigo}.CSV").write_bytes(_estacao(uf, codigo, k).encode("latin-1"))
    _csv(inmet / "estacoes_bioma.csv", "codigo,bioma", [f"{c},{b}" for c, (_, b) in ESTACOES.items()])

    return {"estados": estados, "biomas": biomas}
