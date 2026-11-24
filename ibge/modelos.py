# FORMATO COMBINADO PARA OS DADOS DE ENTRADA E SAÍDA DO IBGE

from dataclasses import dataclass

@dataclass
class Estado:
    sigla: str
    nome: str
    regiao: str


@dataclass
class Municipio:
    codigo_ibge: str
    nome: str
    uf: str
    regiao: str


#DADOS DO PORTAL
@dataclass
class DadosPortal:
    prefeito: str | None = None
    gentilico: str | None = None
    populacao_estimada: int | None = None
    ano_populacao: int | None = None
    area_km2: float | None = None
    ano_area: int | None = None


@dataclass
class Ocorrencia:
    codigo_ibge: str
    municipio: str
    motivo: str


@dataclass
class PaginaVisitada:
    municipio: Municipio
    url_fonte: str
    html: str | None = None
    dados: DadosPortal | None = None
