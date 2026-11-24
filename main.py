import sys
import argparse


from ibge import controlador, visao
from ibge.erros import ErroApi, ErroPortal

def ler_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Coleta dados dos municípios de uma UF no portal Cidades e Estados do IBGE."
    )
    parser.add_argument("--uf", help="sigla ou número da UF (ex.: PE). Sem isso, abre o menu.")
    parser.add_argument("--limite", help="quantidade de municípios (padrão: 5).")
    return parser.parse_args()





def main() -> None:
    try:
        args = ler_argumentos()
        controlador.executar(uf=args.uf, limite_texto=args.limite)
    except (ErroApi, ErroPortal) as erro:
        visao.mostrar_erro(f"não foi possível continuar: {erro}")
        sys.exit(1)
    except KeyboardInterrupt:
        visao.mostrar_mensagem("\nExecução interrompida pelo usuário.")
        sys.exit(1)


if __name__ == "__main__":
    main()
