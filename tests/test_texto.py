from ibge.texto import chave_ordenacao, extrair_ano, gerar_slug, numero_br, sem_acento

def test_sem_acento():
    assert sem_acento("São Paulo") == "Sao Paulo"
    assert sem_acento("João") == "Joao"
    assert sem_acento("áéíóú") == "aeiou"
    assert sem_acento("çÇ") == "cC"
    assert sem_acento("ñÑ") == "nN"
    assert sem_acento("àèìòù") == "aeiou"
    assert sem_acento("âêîôû") == "aeiou"
    assert sem_acento("äëïöü") == "aeiou"
    assert sem_acento("ãõ") == "ao"

def test_chave_ordenacao_ignora_acento_e_maiuscula():
    assert chave_ordenacao("Água Preta") == "agua preta"
    nomes = ["Água Preta", "Agrestina", "Afrânio"]
    nomes.sort(key=chave_ordenacao)
    assert nomes == ["Afrânio", "Agrestina", "Água Preta"]


def test_gerar_slug_nome_simples():
    assert gerar_slug("Recife") == "recife"
    assert gerar_slug("Abreu e Lima") == "abreu-e-lima"
    assert gerar_slug("Armação dos Búzios") == "armacao-dos-buzios"


def test_gerar_slug_com_apostrofo():
    assert gerar_slug("Olho d'Água das Flores") == "olho-dagua-das-flores"
    assert gerar_slug("Sant'Ana do Livramento") == "santana-do-livramento"
    assert gerar_slug("Conquista D'Oeste") == "conquista-doeste"


def test_gerar_slug_com_hifen_e_apostrofo():
    assert gerar_slug("Olhos-d'Água") == "olhos-dagua"


def test_numero_br():
    assert numero_br("1.588.983") == 1588983
    assert numero_br("218,843") == 218.843
    assert numero_br("8.509.360,850") == 8509360.85


def test_numero_br_ausente():
    assert numero_br("-") is None
    assert numero_br("") is None


def test_extrair_ano():
    assert extrair_ano("\xa0\xa0\xa0[2025]") == 2025
    assert extrair_ano("[2026]") == 2026


def test_extrair_ano_invalido():
    assert extrair_ano("") is None
    assert extrair_ano("[abc]") is None