ESTADOS = [
    ("Acre", "AC", "Norte"), ("Amapá", "AP", "Norte"), ("Amazonas", "AM", "Norte"),
    ("Pará", "PA", "Norte"), ("Rondônia", "RO", "Norte"), ("Roraima", "RR", "Norte"),
    ("Tocantins", "TO", "Norte"),
    ("Alagoas", "AL", "Nordeste"), ("Bahia", "BA", "Nordeste"), ("Ceará", "CE", "Nordeste"),
    ("Maranhão", "MA", "Nordeste"), ("Paraíba", "PB", "Nordeste"),
    ("Pernambuco", "PE", "Nordeste"), ("Piauí", "PI", "Nordeste"),
    ("Rio Grande do Norte", "RN", "Nordeste"), ("Sergipe", "SE", "Nordeste"),
    ("Distrito Federal", "DF", "Centro-Oeste"), ("Goiás", "GO", "Centro-Oeste"),
    ("Mato Grosso", "MT", "Centro-Oeste"), ("Mato Grosso do Sul", "MS", "Centro-Oeste"),
    ("Espírito Santo", "ES", "Sudeste"), ("Minas Gerais", "MG", "Sudeste"),
    ("Rio de Janeiro", "RJ", "Sudeste"), ("São Paulo", "SP", "Sudeste"),
    ("Paraná", "PR", "Sul"), ("Rio Grande do Sul", "RS", "Sul"),
    ("Santa Catarina", "SC", "Sul"),
]

BIOMAS = ["Amazônia", "Caatinga", "Cerrado", "Mata Atlântica", "Pampa", "Pantanal"]

SQL = """
    INSERT INTO localidade (nome, sigla_uf, tipo, regiao)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (nome, tipo) DO NOTHING
"""


def executar(conn):
    with conn.cursor() as cur:
        for nome, uf, regiao in ESTADOS:
            cur.execute(SQL, (nome, uf, "ESTADO", regiao))
        for nome in BIOMAS:
            cur.execute(SQL, (nome, None, "BIOMA", None))
    return len(ESTADOS) + len(BIOMAS)
