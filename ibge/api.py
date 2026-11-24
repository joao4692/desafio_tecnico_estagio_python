import httpx

from ibge.erros import ErroApi

from ibge.modelos import Estado, Municipio
from ibge.texto import chave_ordenacao

URL_API = "https://servicodados.ibge.gov.br/api/v1/localidades"


def buscar_json(url: str):
    try:
        resposta = httpx.get(url, timeout=15)
        resposta.raise_for_status()
        return resposta.json()
    except httpx.TimeoutException:
        raise ErroApi("a API do IBGE demorou demais para responder")
    except httpx.HTTPStatusError as erro:
        raise ErroApi(f"a API do IBGE respondeu com erro {erro.response.status_code}")
    except httpx.RequestError:
        raise ErroApi("não foi possível conectar à API do IBGE")
    except ValueError:
        raise ErroApi("a API do IBGE devolveu uma resposta inválida")

#LIstar estados 

def ler_estados(dados: list) -> list[Estado]:
    estados = []
    for item in dados:
        estado = Estado(
            sigla=item["sigla"],
            nome=item["nome"],
            regiao=item["regiao"]["nome"],
        )
        estados.append(estado)
    estados.sort(key=lambda estado: chave_ordenacao(estado.nome))
    return estados


def listar_estados() -> list[Estado]:
    dados = buscar_json(URL_API + "/estados")
    if not dados:
        raise ErroApi("a API do IBGE não devolveu nenhum estado")
    try:
        return ler_estados(dados)
    except (KeyError, TypeError):
        raise ErroApi("a API do IBGE devolveu os estados num formato inesperado")


#Listar municipios de um estado

def ler_municipios(dados: list, estado: Estado) -> list[Municipio]:
    municipios = []
    for item in dados:
        municipio = Municipio(
            codigo_ibge=str(item["id"]),
            nome=item["nome"],
            uf=estado.sigla,
            regiao=estado.regiao,
        )
        municipios.append(municipio)
    municipios.sort(key=lambda municipio: chave_ordenacao(municipio.nome))
    return municipios


def listar_municipios(estado: Estado) -> list[Municipio]:
    dados = buscar_json(f"{URL_API}/estados/{estado.sigla}/municipios")
    if not dados:
        raise ErroApi(f"a API do IBGE não devolveu nenhum município para {estado.sigla}")
    try:
        return ler_municipios(dados, estado)
    except (KeyError, TypeError):
        raise ErroApi("a API do IBGE devolveu os municípios num formato inesperado")

