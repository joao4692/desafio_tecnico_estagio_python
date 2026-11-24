from datetime import date
from pathlib import Path

import pandas as pd

from ibge.modelos import DadosPortal, Ocorrencia, PaginaVisitada
from ibge.texto import chave_ordenacao

PASTA_SAIDA = Path(__file__).resolve().parent.parent / "output"




COLUNAS = [
    "codigo_ibge",
    "municipio",
    "uf",
    "regiao",
    "prefeito",
    "gentilico",
    "populacao_estimada",
    "ano_populacao",
    "area_km2",
    "ano_area",
    "url_fonte",
    "data_coleta",
]

COLUNAS_INTEIRAS = ["populacao_estimada", "ano_populacao", "ano_area"]


def montar_linha(visitada: PaginaVisitada, data_coleta: date) -> dict:
    municipio = visitada.municipio
    dados = visitada.dados
    if dados is None:
        dados = DadosPortal()
    return {
        "codigo_ibge": municipio.codigo_ibge,
        "municipio": municipio.nome,
        "uf": municipio.uf,
        "regiao": municipio.regiao,
        "prefeito": dados.prefeito,
        "gentilico": dados.gentilico,
        "populacao_estimada": dados.populacao_estimada,
        "ano_populacao": dados.ano_populacao,
        "area_km2": dados.area_km2,
        "ano_area": dados.ano_area,
        "url_fonte": visitada.url_fonte,
        "data_coleta": data_coleta,
    }


def montar_tabela(paginas: list[PaginaVisitada], data_coleta: date) -> pd.DataFrame:
    linhas = []
    for visitada in paginas:
        linhas.append(montar_linha(visitada, data_coleta))
    tabela = pd.DataFrame(linhas, columns=COLUNAS)
    tabela = tabela.drop_duplicates(subset="codigo_ibge")
    tabela["ordem"] = tabela["municipio"].map(chave_ordenacao)
    tabela = tabela.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)
    for coluna in COLUNAS_INTEIRAS:
        tabela[coluna] = tabela[coluna].astype("Int64")
    tabela["area_km2"] = tabela["area_km2"].astype("float")
    return tabela




def montar_resumo(uf: str, data_coleta: date, paginas: list[PaginaVisitada], ocorrencias: list[Ocorrencia]) -> pd.DataFrame:
    com_dados = 0
    for visitada in paginas:
        if visitada.dados is not None:
            com_dados += 1
    linhas = [
        {"item": "uf", "valor": uf.upper()},
        {"item": "data_coleta", "valor": data_coleta.isoformat()},
        {"item": "municipios_processados", "valor": len(paginas)},
        {"item": "paginas_abertas", "valor": com_dados},
        {"item": "paginas_com_falha", "valor": len(paginas) - com_dados},
        {"item": "ocorrencias", "valor": len(ocorrencias)},
    ]
    return pd.DataFrame(linhas)


def montar_ocorrencias(ocorrencias: list[Ocorrencia]) -> pd.DataFrame:
    linhas = []
    for ocorrencia in ocorrencias:
        linhas.append({
            "codigo_ibge": ocorrencia.codigo_ibge,
            "municipio": ocorrencia.municipio,
            "motivo": ocorrencia.motivo,
        })
    return pd.DataFrame(linhas, columns=["codigo_ibge", "municipio", "motivo"])


def salvar_excel(uf: str, tabela: pd.DataFrame, resumo: pd.DataFrame, ocorrencias: pd.DataFrame) -> Path:
    PASTA_SAIDA.mkdir(exist_ok=True)
    caminho = PASTA_SAIDA / f"municipios_{uf.lower()}.xlsx"
    with pd.ExcelWriter(caminho) as arquivo:
        tabela.to_excel(arquivo, sheet_name="municipios", index=False)
        resumo.to_excel(arquivo, sheet_name="resumo", index=False)
        ocorrencias.to_excel(arquivo, sheet_name="ocorrencias", index=False)
    return caminho
