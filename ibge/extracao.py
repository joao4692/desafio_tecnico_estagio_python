from dataclasses import asdict

from bs4 import BeautifulSoup, Tag

from ibge.modelos import DadosPortal
from ibge.texto import extrair_ano, numero_br





def achar_indicador(sopa: BeautifulSoup, rotulo: str) -> Tag | None:
    for bloco in sopa.select(".indicador"):
        titulo = bloco.select_one(".ind-label p")
        if titulo is not None and titulo.get_text(strip=True) == rotulo:
            return bloco
    return None


def ler_valor(bloco: Tag) -> str | None:
    valor = bloco.select_one(".ind-value")
    if valor is None:
        return None
    texto = valor.find(string=True, recursive=False)
    if texto is None or texto.strip() in ("", "-"):
        return None
    return texto.strip()


def ler_ano(bloco: Tag) -> int | None:
    ano = bloco.select_one(".ind-value small")
    if ano is None:
        return None
    return extrair_ano(ano.get_text())



def ler_indicador(sopa: BeautifulSoup, rotulo: str) -> tuple[str | None, int | None]:
    bloco = achar_indicador(sopa, rotulo)
    if bloco is None:
        return None, None
    return ler_valor(bloco), ler_ano(bloco)


def converter_numero(texto: str | None) -> float | None:
    if texto is None:
        return None
    try:
        return numero_br(texto)
    except ValueError:
        return None


def extrair_dados(html: str) -> DadosPortal:
    sopa = BeautifulSoup(html, "html.parser")
    prefeito, _ = ler_indicador(sopa, "Prefeito")
    gentilico, _ = ler_indicador(sopa, "Gentílico")
    texto_populacao, ano_populacao = ler_indicador(sopa, "População estimada")
    texto_area, ano_area = ler_indicador(sopa, "Área Territorial")
    populacao = converter_numero(texto_populacao)
    if populacao is not None:
        populacao = int(populacao)
    return DadosPortal(
        prefeito=prefeito,
        gentilico=gentilico,
        populacao_estimada=populacao,
        ano_populacao=ano_populacao,
        area_km2=converter_numero(texto_area),
        ano_area=ano_area,
    )



def campos_vazios(dados: DadosPortal) -> list[str]:
    vazios = []
    for campo, valor in asdict(dados).items():
        if valor is None:
            vazios.append(campo)
    return vazios



