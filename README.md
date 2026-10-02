# Pipeline ETL - Dados de Combustíveis ANP

Este projeto tem como objetivo construir um pipeline ETL em Python para extrair, organizar, tratar e carregar dados públicos de preços de combustíveis disponibilizados pela ANP.

## Arquitetura do Pipeline

O projeto foi organizado em camadas:

- **Bronze**: arquivos brutos baixados da fonte oficial.
- **Extracted**: arquivos CSV extraídos dos arquivos compactados.
- **Silver**: base consolidada, padronizada e enriquecida.
- **PostgreSQL**: carga da base tratada em banco relacional para consumo analítico.

## Tecnologias utilizadas

- Python
- Pandas
- Requests
- Pathlib
- PyArrow
- PostgreSQL
- SQLAlchemy
- DBeaver

## Estrutura do projeto

```text
projeto_dados_glp/
│
├── data/
│   ├── bronze/
│   ├── extracted/
│   └── silver/
│
├── src/
│   ├── extract.py
│   ├── treatment.py
│   ├── transform.py
│   └── load.py
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md