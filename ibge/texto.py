import unicodedata


def sem_acento(texto: str) -> str:
    texto_separado = unicodedata.normalize("NFD", texto)
    resultado = ""
    for letra in texto_separado:
        if not unicodedata.combining(letra):
            resultado += letra
    return resultado


def chave_ordenacao(nome: str) -> str:
    return sem_acento(nome).lower()

#gerar slug do nome do municipio

def gerar_slug(nome: str) -> str:
    texto = sem_acento(nome).lower()
    texto = texto.replace("'", "").replace("’", "")
    slug = ""
    for letra in texto:
        if letra.isalnum():
            slug += letra
        else:
            slug += "-"
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")

# converter numeros br

def numero_br(texto: str) -> float | None:
    texto = texto.strip()
    if texto == "" or texto == "-":
        return None
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")
    return float(texto)

#extrair ano

def extrair_ano(texto: str) -> int | None:
    texto = texto.strip()
    texto = texto.replace("[", "").replace("]", "")
    if texto.isdigit() and len(texto) == 4:
        return int(texto)
    return None

