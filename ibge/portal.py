

from contextlib import contextmanager

from playwright.sync_api import Error as ErroPlaywright
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as TempoEsgotadoPlaywright
from playwright.sync_api import sync_playwright

from ibge.erros import ErroPortal
from ibge.modelos import Municipio
from ibge.texto import gerar_slug

URL_PORTAL = "https://www.ibge.gov.br/cidades-e-estados"
PAUSA_ENTRE_PAGINAS = 2000


def montar_url(uf: str, slug: str) -> str:
    return f"{URL_PORTAL}/{uf.lower()}/{slug}.html"


def url_pelo_nome(municipio: Municipio) -> str:
    return montar_url(municipio.uf, gerar_slug(municipio.nome))


@contextmanager
def navegador_aberto():
    with sync_playwright() as playwright:
        try:
            navegador = playwright.chromium.launch(headless=False)
        except ErroPlaywright:
            raise ErroPortal("não foi possível abrir o navegador (rode 'playwright install chromium' e confira se há interface gráfica)")
        try:
            yield navegador.new_page()
        finally:
            navegador.close()


def abrir_pagina(pagina: Page, url: str) -> str:
    try:
        pagina.goto(url, wait_until="domcontentloaded", timeout=30000)
        pagina.wait_for_selector(".indicador", timeout=20000)
    except TempoEsgotadoPlaywright:
        raise ErroPortal(f"a página demorou demais para carregar: {url}")
    except ErroPlaywright:
        raise ErroPortal(f"não foi possível abrir a página: {url}")
    return pagina.content()

#conferir se a cidade é certa

def codigo_da_pagina(pagina: Page) -> str:
    try:
        codigo = pagina.get_attribute("#responseMunicipios", "data-codigo", timeout=5000)
    except TempoEsgotadoPlaywright:
        return ""
    if codigo is None:
        return ""
    return codigo.strip()


def abrir_municipio(pagina: Page, url: str, codigo_ibge: str) -> str:
    html = abrir_pagina(pagina, url)
    if pagina.url != url:
        raise ErroPortal(f"a página foi redirecionada para {pagina.url}")
    codigo = codigo_da_pagina(pagina)
    if codigo != codigo_ibge:
        raise ErroPortal(f"a página mostra o código '{codigo}', mas o esperado era {codigo_ibge}")
    return html


def abrir_com_plano_b(pagina: Page, municipio: Municipio) -> tuple[str, str]:
    url_nome = url_pelo_nome(municipio)
    try:
        return abrir_municipio(pagina, url_nome, municipio.codigo_ibge), url_nome
    except ErroPortal as erro_nome:
        url_codigo = montar_url(municipio.uf, municipio.codigo_ibge)
        try:
            return abrir_municipio(pagina, url_codigo, municipio.codigo_ibge), url_codigo
        except ErroPortal as erro_codigo:
            raise ErroPortal(f"pelo nome: {erro_nome} | pelo código: {erro_codigo}")


def pausar(pagina: Page) -> None:
    pagina.wait_for_timeout(PAUSA_ENTRE_PAGINAS)

