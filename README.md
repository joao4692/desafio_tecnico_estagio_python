# Coleta de dados dos municípios no portal Cidades e Estados do IBGE

Aplicação de terminal em Python que:

1. lista as UFs pela **API de Localidades do IBGE** (httpx);
2. deixa o usuário escolher a UF e a quantidade de municípios;
3. busca os municípios da UF na API e pega os primeiros em ordem alfabética;
4. abre a página de cada município no portal **Cidades e Estados** com um navegador real (Playwright);
5. extrai prefeito, gentílico, população estimada e área territorial do HTML (BeautifulSoup4);
6. grava tudo em `output/municipios_{uf}.xlsx` (pandas).

Nenhuma UF, município ou código está fixo no código: tudo vem da API.

---

## Requisitos

- Python **3.11 ou superior**
- Um computador **com interface gráfica** (o navegador abre uma janela; veja [Limitações](#limitações))
- Internet

## Instalação

**Linux / macOS:**

```bash
git clone https://github.com/joao4692/desafio_tecnico_estagio_python.git
cd desafio_tecnico_estagio_python

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/joao4692/desafio_tecnico_estagio_python.git
cd desafio_tecnico_estagio_python

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
playwright install chromium
```

Se o PowerShell recusar o `Activate.ps1` ("a execução de scripts foi desabilitada"), rode antes
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (vale só para aquela janela).

O último comando baixa o navegador Chromium que o Playwright controla.

## Como executar

### Pelo menu (padrão)

```bash
python main.py
```

O programa mostra as 27 UFs, numeradas e em ordem alfabética:

```
Escolha a UF (número ou sigla): pe
Quantidade [5]:
```

- **UF:** pode digitar o **número** da lista (`17`) ou a **sigla** (`pe` ou `PE`).
- **Quantidade:** Enter usa o padrão de **5**. Qualquer número de 1 até o total de municípios da UF é aceito.
- Respostas inválidas (`99`, `xx`, `0`, `-2`, `zero`) mostram uma mensagem e perguntam de novo.
- Um limite maior que o total da UF é reduzido ao total, com aviso.

### Direto pela linha de comando

```bash
python main.py --uf pe --limite 5
```

Útil para repetir a mesma execução. Se o `--uf` ou o `--limite` forem inválidos, o programa avisa e abre o menu.

### Exemplo de saída

```
UF escolhida: Pernambuco (PE), 185 municípios na API

Abrindo o portal do IBGE (uma janela do navegador vai abrir)...
[1/5] Abreu e Lima...
   OK, código confere (https://www.ibge.gov.br/cidades-e-estados/pe/abreu-e-lima.html)
...
Páginas abertas: 5 de 5 | Ocorrências: 0

Planilha salva em: .../output/municipios_pe.xlsx
```

Cada município leva cerca de 5 segundos (carregamento da página + pausa de 2 segundos entre páginas).

### Testes

```bash
pytest -v
```

Os testes rodam **sem internet e sem navegador**, sobre páginas reais do portal salvas em `tests/fixtures/`.

---

## Resultado: `output/municipios_{uf}.xlsx`

**Aba `municipios`** (sempre a primeira), com as colunas nesta ordem:

| Coluna | Origem | Tipo |
|---|---|---|
| `codigo_ibge` | API | texto (identificador, não quantidade) |
| `municipio`, `uf`, `regiao` | API | texto |
| `prefeito`, `gentilico` | portal | texto |
| `populacao_estimada`, `ano_populacao` | portal | inteiro (aceita vazio) |
| `area_km2` | portal | decimal |
| `ano_area` | portal | inteiro (aceita vazio) |
| `url_fonte` | página realmente consultada | texto |
| `data_coleta` | data da execução | data |

Linhas sem duplicados (pelo `codigo_ibge`) e em ordem alfabética, ignorando acentos.

**Aba `resumo`:** UF, data da coleta, municípios processados, páginas abertas, páginas com falha e
total de ocorrências.

**Aba `ocorrencias`:** tudo o que não saiu como esperado, com o motivo:
URL pelo nome que não abriu, página que não abriu de jeito nenhum e campos não encontrados.

---

## Fontes

- API de Localidades do IBGE:
  - `https://servicodados.ibge.gov.br/api/v1/localidades/estados`
  - `https://servicodados.ibge.gov.br/api/v1/localidades/estados/{UF}/municipios`
- Portal Cidades e Estados: `https://www.ibge.gov.br/cidades-e-estados/{uf}/{municipio}.html`

---

## Como funciona

```
main.py               argumentos (--uf, --limite) e tratamento final de erros
ibge/
  controlador.py      orquestra o fluxo: menu → API → portal → extração → Excel
  visao.py            tudo o que aparece no terminal (único lugar com print/input)
  api.py              API de Localidades (httpx)
  portal.py           navegação no portal (Playwright)
  extracao.py         leitura do HTML (BeautifulSoup4)
  exportacao.py       planilha (pandas)
  texto.py            regras de texto: slug da URL, acentos, números no formato brasileiro
  modelos.py          formato dos dados (dataclasses)
  erros.py            erros do projeto (ErroApi, ErroPortal)
tests/                testes com pytest + páginas reais salvas
```

Cada biblioteca externa é usada em **um único arquivo**. Os erros de cada biblioteca são traduzidos
para os erros do projeto no próprio arquivo, e o controlador decide o que fazer com eles.

### URL de cada município

O nome vira um *slug*: sem acento, minúsculo, espaços viram hífen e o apóstrofo some.

| Nome na API | URL |
|---|---|
| Abreu e Lima | `pe/abreu-e-lima.html` |
| Olho d'Água das Flores | `al/olho-dagua-das-flores.html` |

### Conferência da página

Uma URL que não existe **não dá erro**: o portal responde normalmente e redireciona para a página do
Brasil, que também tem indicadores (área de 8,5 milhões de km²). Por isso, antes de aceitar uma página,
o programa confere duas coisas:

1. o endereço final é o mesmo que foi pedido (não houve redirecionamento);
2. o código IBGE escrito na página (`data-codigo`) é igual ao da API.

Se a URL pelo nome falhar, o programa tenta a URL pelo código (`pe/2611606.html`), que o portal também
aceita. O uso desse plano B é registrado na aba `ocorrencias`, com o motivo.

### Extração

Cada dado é encontrado pelo **texto do rótulo** ("Prefeito", "População estimada"...) dentro dos blocos
de indicador, e não pela posição na página. O ano vem do `[2025]` ao lado do valor.
A página mostra duas populações; é usada a **estimada**, como pede o enunciado.

---

## Limitações e dados ausentes

- **O navegador abre uma janela.** O portal usa uma proteção (Cloudflare) que bloqueia o navegador
  sem janela (*headless*): ele recebe "403" e a página "Just a moment...". Com a janela visível, a página
  abre normalmente. Por isso o programa precisa de interface gráfica e não roda em servidor sem tela.
  Não foram usados truques para enganar a proteção.
- **Dado ausente fica vazio, nunca é inventado.** Quando um campo não existe na página, ou o portal mostra
  `-`, a célula fica em branco e o motivo vai para a aba `ocorrencias`. Exemplo real: **Brasília (DF) não
  tem prefeito** (o DF tem governador), e o portal mostra `-` nesse campo.
- **Instabilidade do portal.** A mesma URL pode abrir num dia e falhar no outro. Nesse caso o plano B pela
  URL com o código costuma resolver, e a ocorrência registra o motivo.
- **Portal ou internet fora do ar:**
  - se a **API** não responde no início, o programa para com a mensagem
    `não foi possível conectar à API do IBGE` (sem a lista de municípios não há o que coletar);
  - se o **portal** cai no meio da coleta, cada município que falha fica com os campos vazios, vira
    ocorrência, e o programa segue para o próximo. A planilha é salva com o que deu certo.
- **Tempo:** cerca de 5 segundos por município, de propósito, para não sobrecarregar o portal.

### Problemas comuns

| Mensagem | Solução |
|---|---|
| `não foi possível abrir o navegador` | rode `playwright install chromium`; confira se há interface gráfica |
| `não foi possível conectar à API do IBGE` | confira a conexão com a internet |
| `ModuleNotFoundError` | ative o ambiente virtual (`source .venv/bin/activate` ou `.venv\Scripts\Activate.ps1`) |
| `PermissionError` ao salvar a planilha | feche o arquivo `.xlsx` no Excel e rode de novo (o Windows bloqueia arquivos abertos) |

---

## Decisões técnicas

| Problema | Escolha | Alternativa descartada |
|---|---|---|
| Organização do código | MVC leve: tela, regras e orquestração separadas; uma biblioteca por arquivo | camadas extras (repository, service): cerimônia demais para ~9 arquivos |
| Portal bloqueia navegador sem janela | navegador visível (`headless=False`) | plugins "stealth" ou user-agent falso para enganar a proteção |
| Saber quando a página carregou | esperar o bloco `.indicador` aparecer | `networkidle` (nunca termina neste portal) e pausa fixa (lenta e frágil) |
| URL inválida responde 200 e mostra o Brasil | conferir URL final + código IBGE da página; plano B pela URL com o código | confiar no status HTTP ou na presença de indicadores |
| Achar cada dado no HTML | pelo texto do rótulo, só dentro dos blocos `.indicador` | posição fixa ou XPath absoluto (quebram com mudança de layout); busca no HTML inteiro (o rótulo também aparece na tabela de fontes) |
| `-` no lugar do valor | tratar como ausente: célula vazia + ocorrência | gravar o `-`, ou escrever "não se aplica" (seria inventar) |
| Inteiro com vazio vira decimal no pandas (`1588983.0`) | tipo `Int64`, que aceita vazio | `int` comum |
| Código IBGE | texto | número (ninguém soma códigos, e o Excel pode alterar o formato) |
| Resumo e ocorrências | abas separadas, depois da principal | misturar na aba principal (quebraria a estrutura obrigatória) |
| Erros das bibliotecas | traduzidos em `ErroApi`/`ErroPortal` no arquivo de cada biblioteca e tratados no controlador | tratar erros do httpx/Playwright espalhados pelo código |
| Testes | pytest sobre páginas reais salvas | testes que acessam o portal (lentos, instáveis e com acessos desnecessários) |
