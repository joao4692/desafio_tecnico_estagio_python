from pathlib import Path

from ibge.extracao import campos_vazios, extrair_dados

PASTA_FIXTURES = Path(__file__).parent / "fixtures"


def ler_fixture(nome: str) -> str:
    return (PASTA_FIXTURES / nome).read_text(encoding="utf-8")


def test_extrair_dados_recife():
    dados = extrair_dados(ler_fixture("pe_recife.html"))
    assert dados.prefeito == "JOÃO HENRIQUE DE ANDRADE LIMA CAMPOS"
    assert dados.gentilico == "recifense"
    assert dados.populacao_estimada == 1588983
    assert dados.ano_populacao == 2026
    assert dados.area_km2 == 218.843
    assert dados.ano_area == 2025


def test_populacao_e_a_estimada_e_nao_a_do_censo():
    dados = extrair_dados(ler_fixture("pe_recife.html"))
    assert dados.populacao_estimada != 1488920


def test_extrair_dados_nome_com_apostrofo():
    dados = extrair_dados(ler_fixture("al_olho-dagua-das-flores.html"))
    assert dados.prefeito == "JOSÉ LUIZ VASCONCELLOS DOS ANJOS"
    assert dados.gentilico == "olho-daguense"
    assert dados.populacao_estimada == 21137


def test_pagina_do_brasil_nao_tem_dados_de_municipio():
    dados = extrair_dados(ler_fixture("redirecionada_brasil.html"))
    assert dados.prefeito is None
    assert dados.gentilico is None
    assert dados.populacao_estimada is None


def test_campos_vazios_sao_listados():
    dados = extrair_dados(ler_fixture("redirecionada_brasil.html"))
    assert campos_vazios(dados) == ["prefeito", "gentilico", "populacao_estimada", "ano_populacao"]


def test_recife_nao_tem_campos_vazios():
    dados = extrair_dados(ler_fixture("pe_recife.html"))
    assert campos_vazios(dados) == []


def test_tracinho_vira_vazio():
    html = '<div class="indicador"><div class="ind-label"><p>Prefeito</p></div><p class="ind-value">-</p></div>'
    dados = extrair_dados(html)
    assert dados.prefeito is None


def test_html_sem_indicadores():
    dados = extrair_dados("<html><body>página vazia</body></html>")
    assert campos_vazios(dados) == ["prefeito", "gentilico", "populacao_estimada", "ano_populacao", "area_km2", "ano_area"]