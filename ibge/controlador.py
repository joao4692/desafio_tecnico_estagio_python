

from datetime import date

from ibge import api, exportacao, extracao, portal, visao
from ibge.erros import ErroPortal
from ibge.modelos import Estado, Municipio, Ocorrencia, PaginaVisitada

LIMITE_PADRAO = 5


def escolher_estado(resposta: str, estados: list[Estado]) -> Estado | None:
    if resposta.isdigit():
        numero = int(resposta)
        if 1 <= numero <= len(estados):
            return estados[numero - 1]
        return None
    for estado in estados:
        if estado.sigla == resposta.upper():
            return estado
    return None


def interpretar_limite(resposta: str, total: int) -> int | None:
    if resposta == "":
        return min(LIMITE_PADRAO, total)
    if not resposta.isdigit():
        return None
    limite = int(resposta)
    if limite == 0:
        return None
    if limite > total:
        return total
    return limite


#mostra total de municipios se o limite for maior que o total
def avisar_se_reduziu(resposta: str, total: int) -> None:
    if resposta.isdigit() and int(resposta) > total:
        visao.mostrar_mensagem(f"Aviso: este estado tem {total} municípios; vou usar {total}.")


#controle pedido perguntar até acertar
def pedir_estado(estados: list[Estado]) -> Estado:
    visao.mostrar_estados(estados)
    while True:
        resposta = visao.perguntar("Escolha a UF (número ou sigla): ")
        estado = escolher_estado(resposta, estados)
        if estado is not None:
            return estado
        visao.mostrar_erro("opção inválida. Digite o número da lista ou a sigla (ex.: PE).")


def pedir_limite(total: int) -> int:
    while True:
        resposta = visao.perguntar(f"Quantidade [{LIMITE_PADRAO}]: ")
        limite = interpretar_limite(resposta, total)
        if limite is None:
            visao.mostrar_erro(f"digite um número de 1 a {total}, ou Enter para {LIMITE_PADRAO}.")
        else:
            avisar_se_reduziu(resposta, total)

    #dados do estado
def obter_estado(estados: list[Estado], uf: str | None) -> Estado:
    if uf is not None:
        estado = escolher_estado(uf, estados)
        if estado is not None:
            return estado
        visao.mostrar_erro(f"UF '{uf}' não encontrada. Escolha pelo menu.")
    return pedir_estado(estados)


def obter_limite(total: int, limite_texto: str | None) -> int:
    if limite_texto is not None:
        limite = interpretar_limite(limite_texto, total)
        if limite is not None:
            avisar_se_reduziu(limite_texto, total)
            return limite
        visao.mostrar_erro(f"limite '{limite_texto}' inválido. Informe pelo menu.")
    return pedir_limite(total)


def salvar_planilha(sigla: str, paginas: list[PaginaVisitada], ocorrencias: list[Ocorrencia]) -> None:
    data_coleta = date.today()
    tabela = exportacao.montar_tabela(paginas, data_coleta)
    resumo = exportacao.montar_resumo(sigla, data_coleta, paginas, ocorrencias)
    tabela_ocorrencias = exportacao.montar_ocorrencias(ocorrencias)
    caminho = exportacao.salvar_excel(sigla, tabela, resumo, tabela_ocorrencias)
    visao.mostrar_mensagem(f"\nPlanilha salva em: {caminho}")


def executar(uf: str | None = None, limite_texto: str | None = None) -> None:
    estados = api.listar_estados()
    estado = obter_estado(estados, uf)
    municipios = api.listar_municipios(estado)
    limite = obter_limite(len(municipios), limite_texto)
    selecionados = municipios[:limite]
    visao.mostrar_mensagem(f"\nUF escolhida: {estado.nome} ({estado.sigla}), {len(municipios)} municípios na API")
    visao.mostrar_municipios(selecionados)
    visao.mostrar_mensagem("\nAbrindo o portal do IBGE (uma janela do navegador vai abrir)...")
    paginas, ocorrencias = visitar_municipios(selecionados)
    extrair_dados_das_paginas(paginas, ocorrencias)

    abertas = 0
    for pagina in paginas:
        if pagina.html is not None:
            abertas += 1
    visao.mostrar_mensagem(f"\nPáginas abertas: {abertas} de {len(paginas)} | Ocorrências: {len(ocorrencias)}")
    for ocorrencia in ocorrencias:
        visao.mostrar_mensagem(f"  - {ocorrencia.municipio}: {ocorrencia.motivo}")
    salvar_planilha(estado.sigla, paginas, ocorrencias)


def visitar_municipios(municipios: list[Municipio]) -> tuple[list[PaginaVisitada], list[Ocorrencia]]:
    paginas = []
    ocorrencias = []
    with portal.navegador_aberto() as pagina:
        for posicao, municipio in enumerate(municipios, start=1):
            visao.mostrar_progresso(posicao, len(municipios), municipio.nome)
            url_nome = portal.url_pelo_nome(municipio)
            try:
                html, url = portal.abrir_com_plano_b(pagina, municipio)
                paginas.append(PaginaVisitada(municipio, url, html))
                visao.mostrar_mensagem(f"   OK, código confere ({url})")
                if url != url_nome:
                    motivo = f"URL pelo nome não encontrada ({url_nome}); usada a URL pelo código"
                    ocorrencias.append(Ocorrencia(municipio.codigo_ibge, municipio.nome, motivo))
            except ErroPortal as erro:
                paginas.append(PaginaVisitada(municipio, url_nome))
                ocorrencias.append(Ocorrencia(municipio.codigo_ibge, municipio.nome, str(erro)))
                visao.mostrar_erro(str(erro))
            if posicao < len(municipios):
                portal.pausar(pagina)
    return paginas, ocorrencias



def extrair_dados_das_paginas(paginas: list[PaginaVisitada], ocorrencias: list[Ocorrencia]) -> None:
    for visitada in paginas:
        if visitada.html is None:
            continue
        visitada.dados = extracao.extrair_dados(visitada.html)
        vazios = extracao.campos_vazios(visitada.dados)
        if len(vazios) > 0:
            motivo = "campos não encontrados na página: " + ", ".join(vazios)
            ocorrencias.append(Ocorrencia(visitada.municipio.codigo_ibge, visitada.municipio.nome, motivo))


