from ibge.modelos import Estado, Municipio


def mostrar_estados(estados: list[Estado]) -> None:
    print("\nEstados disponíveis:")
    for numero, estado in enumerate(estados, start=1):
        print(f"{numero}) {estado.nome} ({estado.sigla})")


def perguntar(texto: str) -> str:
    return input(texto).strip()


def mostrar_mensagem(texto: str) -> None:
    print(texto)


def mostrar_erro(texto: str) -> None:
    print(f"[ERRO] {texto}")


def mostrar_municipios(municipios: list[Municipio]) -> None:
    print(f"\nMunicípios selecionados ({len(municipios)}):")
    for municipio in municipios:
        print(f"  {municipio.codigo_ibge} - {municipio.nome}")
