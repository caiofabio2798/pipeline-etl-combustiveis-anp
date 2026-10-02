# Pipeline ETL - Dados de Combustíveis ANP

Este projeto tem como objetivo construir um pipeline ETL em Python para extrair, organizar, tratar e carregar dados públicos de preços de combustíveis disponibilizados pela ANP.

O pipeline foi desenvolvido com foco em boas práticas de Engenharia de Dados, utilizando uma estrutura em camadas, ambiente virtual, organização modular do código e carga final dos dados tratados em PostgreSQL.

---

## Objetivo do Projeto

Construir um pipeline de dados capaz de:

- Baixar arquivos públicos da ANP.
- Organizar os dados brutos em uma camada Bronze.
- Descompactar e preparar os arquivos CSV.
- Consolidar múltiplos arquivos em uma única base tratada.
- Padronizar textos, nomes de colunas e campos de data.
- Criar colunas auxiliares como ano, mês, semestre e nome do estado.
- Salvar a base final na camada Silver.
- Carregar a base tratada em uma tabela PostgreSQL.

---

## Fonte dos Dados

Os dados utilizados neste projeto são públicos e disponibilizados pela ANP/Gov.br.

A base contém informações sobre preços de combustíveis coletados em diferentes revendas, municípios, estados e períodos.

---

## Arquitetura do Pipeline

O projeto foi estruturado em camadas:

```text
Fonte ANP/Gov.br
      ↓
Download dos arquivos
      ↓
data/bronze
      ↓
Descompactação e organização
      ↓
data/extracted
      ↓
Tratamento e consolidação
      ↓
data/silver
      ↓
PostgreSQL
```

### Camadas

| Camada | Descrição |
|---|---|
| Bronze | Armazena os arquivos originais baixados da fonte oficial |
| Extracted | Armazena os CSVs extraídos e preparados para tratamento |
| Silver | Armazena a base consolidada, tratada e enriquecida |
| PostgreSQL | Recebe a base final para consumo analítico |

---

## Tecnologias Utilizadas

- Python
- Pandas
- NumPy
- Requests
- Pathlib
- PyArrow
- SQLAlchemy
- Psycopg2
- PostgreSQL
- DBeaver
- Git e GitHub

---

## Estrutura do Projeto

```text
pipeline-etl-combustiveis-anp/
│
├── data/
│   ├── bronze/
│   │   └── .gitkeep
│   ├── extracted/
│   │   └── .gitkeep
│   └── silver/
│       └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── treatment.py
│   ├── transform.py
│   └── load.py
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Descrição dos Arquivos

### `main.py`

Arquivo principal responsável por orquestrar a execução do pipeline.

Fluxo executado:

```text
Download → Preparação dos arquivos → Transformação → Carga no PostgreSQL
```

---

### `src/extract.py`

Responsável por realizar o download dos arquivos da ANP.

Principais responsabilidades:

- Criar a pasta `data/bronze`.
- Baixar arquivos `.zip` e `.csv`.
- Evitar downloads duplicados.
- Armazenar os arquivos brutos na camada Bronze.

---

### `src/treatment.py`

Responsável por preparar os arquivos baixados.

Principais responsabilidades:

- Descompactar arquivos `.zip`.
- Copiar arquivos `.csv` da camada Bronze para a camada Extracted.
- Organizar os arquivos para a etapa de transformação.

---

### `src/transform.py`

Responsável pelo tratamento e consolidação dos dados.

Principais responsabilidades:

- Ler os CSVs da pasta `data/extracted`.
- Padronizar nomes de colunas.
- Remover acentos e caracteres especiais.
- Consolidar os arquivos em uma base única.
- Criar colunas auxiliares:
  - Ano
  - Número do mês
  - Nome do mês
  - Semestre
  - Nome do estado
  - ID sequencial
- Salvar a base final na camada Silver.

---

### `src/load.py`

Responsável pela carga dos dados tratados no PostgreSQL.

Principais responsabilidades:

- Ler a base final da camada Silver.
- Solicitar as credenciais do PostgreSQL no terminal.
- Criar o schema `silver`, caso não exista.
- Criar ou substituir a tabela `silver.precos_combustiveis`.
- Carregar os dados tratados no banco.

---

## Como Clonar o Projeto

Para clonar o repositório, execute:

```bash
git clone https://github.com/caiofabio2798/pipeline-etl-combustiveis-anp.git
```

Acesse a pasta do projeto:

```bash
cd pipeline-etl-combustiveis-anp
```

---

## Como Criar o Ambiente Virtual

Crie o ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell, ative o ambiente:

```bash
.\.venv\Scripts\activate
```

Após a ativação, o terminal deve exibir algo parecido com:

```bash
(.venv) PS C:\caminho\do\projeto>
```

---

## Como Instalar as Dependências

Com a `.venv` ativada, execute:

```bash
python -m pip install --upgrade pip
```

Depois instale as bibliotecas do projeto:

```bash
python -m pip install -r requirements.txt
```

---

## Configuração do PostgreSQL

Antes de executar a carga no banco, é necessário ter o PostgreSQL instalado e um banco criado.

Exemplo de criação do banco:

```sql
CREATE DATABASE db_combustiveis_anp;
```

O schema `silver` será criado automaticamente pelo pipeline, caso não exista.

A tabela final será criada automaticamente pelo Python com o nome:

```text
silver.precos_combustiveis
```

---

## Como Executar o Pipeline

Com o ambiente virtual ativado, execute:

```bash
python main.py
```

Durante a etapa de carga no PostgreSQL, o terminal solicitará as credenciais:

```text
Informe as credenciais do PostgreSQL
Usuário [postgres]:
Senha:
Host [localhost]:
Porta [5432]:
Nome do banco [db_combustiveis_anp]:
```

Caso pressione `Enter` nos campos com valor padrão, o pipeline utilizará os valores sugeridos.

---

## Saídas Geradas

Após a execução do pipeline, os dados serão organizados nas seguintes pastas:

```text
data/bronze
```

Contém os arquivos brutos baixados da ANP.

```text
data/extracted
```

Contém os arquivos CSV extraídos e preparados.

```text
data/silver
```

Contém a base consolidada e tratada.

Exemplo de arquivo final:

```text
base_combustiveis_tratada_final.parquet
```

ou

```text
base_combustiveis_tratada_final.csv
```

dependendo da configuração utilizada no pipeline.

---

## Validação no PostgreSQL

Após a carga, é possível validar os dados no DBeaver ou em outro cliente SQL.

Quantidade de registros:

```sql
SELECT COUNT(*)
FROM silver.precos_combustiveis;
```

Amostra dos dados:

```sql
SELECT *
FROM silver.precos_combustiveis
LIMIT 10;
```

Registros por produto:

```sql
SELECT
    produto,
    COUNT(*) AS total_registros
FROM silver.precos_combustiveis
GROUP BY produto
ORDER BY total_registros DESC;
```

Período da base:

```sql
SELECT
    MIN(data_da_coleta) AS menor_data,
    MAX(data_da_coleta) AS maior_data
FROM silver.precos_combustiveis;
```

---

## Observações Sobre Dados e Versionamento

Os arquivos de dados não são versionados no GitHub.

As seguintes pastas são ignoradas pelo `.gitignore`:

```text
data/bronze/
data/extracted/
data/silver/
```

Isso evita subir arquivos grandes, como:

- `.csv`
- `.zip`
- `.parquet`

A estrutura das pastas é mantida com arquivos `.gitkeep`.

---

## Status do Projeto

- [x] Estruturação do projeto Python
- [x] Criação de ambiente virtual
- [x] Download dos dados públicos
- [x] Organização em camada Bronze
- [x] Extração dos arquivos compactados
- [x] Organização em camada Extracted
- [x] Tratamento e consolidação dos dados
- [x] Criação da camada Silver
- [x] Carga no PostgreSQL
- [ ] Conexão com Power BI
- [ ] Criação de camada Gold
- [ ] Automatização/orquestração do pipeline

---

## Possíveis Evoluções

Algumas melhorias futuras para o projeto:

- Criar camada Gold com agregações analíticas.
- Conectar o PostgreSQL ao Power BI.
- Criar dashboard de análise de preços de combustíveis.
- Adicionar testes de qualidade dos dados.
- Salvar logs de execução.
- Criar controle incremental de arquivos já processados.
- Publicar a base em ambiente cloud.
- Orquestrar o pipeline com ferramentas como Airflow ou Prefect.

---

## Autor

Projeto desenvolvido por Caio Fabio.

GitHub: [caiofabio2798](https://github.com/caiofabio2798)