from pathlib import Path
import pandas as pd
import numpy as np
import unicodedata


BASE_DIR = Path(__file__).resolve().parent.parent

EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
SILVER_DIR = BASE_DIR / "data" / "silver"

def criar_pasta(caminho: Path) -> None:
    caminho.mkdir(parents=True, exist_ok=True)

def tratamento_dados_csv(
    diretorio_origem: Path = EXTRACTED_DIR,
    diretorio_destino: Path = SILVER_DIR
) -> None:
    arquivos = list(diretorio_origem.glob("*.csv"))

    criar_pasta(diretorio_destino)

    caracteres_substituicoes = {
    '"': '_', '#': '_', '$': 'S', '%': '_', '&': '_', "'": '_', '+': '_',
    ':': '_', ';': '_', '`': '_', '}': '_', '°': '_', '¿': '_', 'm³': 'm3','mA3': 'm3',
    '\x80': '', '\x81': '', '\x82': '', '\x83': '', '\x87': '',
    '\x89': '', '\x8a': '', '\x8d': '', '\x93': '', '\x94': '',
    '\x95': '', '\x9a': '', '\xa0': ''
}
    def remover_acentos(valor):
        if isinstance(valor, str):
            valor = unicodedata.normalize('NFKD', valor).encode('ASCII', 'ignore').decode('ASCII')
        return valor
    
    def substituir_caracteres_especiais(valor):
        if isinstance(valor, str):
            for caractere, substituicao in caracteres_substituicoes.items():
                valor = valor.replace(caractere, substituicao)
            valor = valor.strip()
        return valor
    
    def processar_valor(valor):
        valor = remover_acentos(valor)
        valor = substituir_caracteres_especiais(valor)
        return valor
    
    def padronizar_nome_coluna(coluna):
        coluna = processar_valor(coluna)
        coluna = coluna.strip()
        coluna = coluna.replace(" ", "_")
        coluna = coluna.replace("-", "_")
        coluna = coluna.replace("/", "_")
        coluna = coluna.replace("(", "")
        coluna = coluna.replace(")", "")
        coluna = coluna.lower()
        return coluna

    dfs = []

    for arquivo in arquivos:
        try:
            print(f"Lendo arquivo: {arquivo.name}")

            df = pd.read_csv(
                arquivo,
                sep=";",
                encoding="latin1",
                low_memory=False
            )

            df.columns = [padronizar_nome_coluna(coluna) for coluna in df.columns]

            for col in df.select_dtypes(include="object").columns:
                df[col] = df[col].map(processar_valor)

            dfs.append(df)

            print(f"Arquivo tratado: {arquivo.name}")

        except Exception as erro:
            print(f"Erro ao tratar o arquivo {arquivo.name}: {erro}")

    if not dfs:
        print("Nenhum arquivo foi tratado com sucesso.")
        return

    print("Unificando arquivos tratados...")

    df_final = pd.concat(dfs, ignore_index=True)

    arquivo_saida = diretorio_destino / "base_combustiveis_tratada.csv"

    df_final.to_csv(
        arquivo_saida,
        sep=";",
        index=False,
        encoding="utf-8"
    )

    print(f"Arquivo salvo em: {arquivo_saida}")

def inclusao_dados_coluna(
    arquivo_origem: Path = SILVER_DIR / "base_combustiveis_tratada.csv",
    diretorio_destino: Path = SILVER_DIR
) -> None:
    criar_pasta(diretorio_destino)

    print("Iniciando inclusão de colunas na base silver...")

    df = pd.read_csv(
        arquivo_origem,
        sep=";",
        encoding="utf-8",
        dtype=str,
        low_memory=False
    )

    df["data_da_coleta"] = pd.to_datetime(
        df["data_da_coleta"],
        dayfirst=True,
        errors="coerce"
    )

    mes_map = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro"
    }

    df["ano"] = pd.to_numeric(
        df["data_da_coleta"].dt.year,
        errors="coerce"
    ).astype("Int64")

    df["numero_mes"] = pd.to_numeric(
        df["data_da_coleta"].dt.month,
        errors="coerce"
    ).astype("Int64")

    df["mes"] = df["numero_mes"].map(mes_map)

    df["semestre"] = None
    df.loc[df["numero_mes"].between(1, 6), "semestre"] = "1-semestre"
    df.loc[df["numero_mes"].between(7, 12), "semestre"] = "2-semestre"

    uf_map = {
        "AC": "Acre",
        "AL": "Alagoas",
        "AP": "Amapa",
        "AM": "Amazonas",
        "BA": "Bahia",
        "CE": "Ceara",
        "DF": "Distrito Federal",
        "ES": "Espirito Santo",
        "GO": "Goias",
        "MA": "Maranhao",
        "MT": "Mato Grosso",
        "MS": "Mato Grosso do Sul",
        "MG": "Minas Gerais",
        "PA": "Para",
        "PB": "Paraiba",
        "PR": "Parana",
        "PE": "Pernambuco",
        "PI": "Piaui",
        "RJ": "Rio de Janeiro",
        "RN": "Rio Grande do Norte",
        "RS": "Rio Grande do Sul",
        "RO": "Rondonia",
        "RR": "Roraima",
        "SC": "Santa Catarina",
        "SP": "Sao Paulo",
        "SE": "Sergipe",
        "TO": "Tocantins"
    }

    coluna_estado = "estado___sigla"

    if coluna_estado not in df.columns:
        print("Colunas disponíveis:")
        print(df.columns.tolist())
        raise KeyError(f"Coluna não encontrada: {coluna_estado}")

    df["estado_nome"] = (
        df[coluna_estado]
        .str.upper()
        .map(uf_map)
        .fillna(df[coluna_estado])
    )

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)


    df["valor_de_venda"] = (
        df["valor_de_venda"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    df["valor_de_venda"] = pd.to_numeric(
        df["valor_de_venda"],
        errors="coerce"
    )

    df1 = df.drop('regiao___sigla', axis=1)

    final_df = df1.rename(columns={
        'iregiao___sigla':'regiao_sigla',
        'estado___sigla':'estado_sigla'
    })

    arquivo_saida = diretorio_destino / "base_combustiveis_tratada.parquet"

    final_df.to_parquet(
        arquivo_saida,
        index=False
    )

    print(f"Arquivo silver final salvo em: {arquivo_saida}")

def preparar_transformacao_arquivos() -> None:
    print("Iniciando preparação para tratamento")

    tratamento_dados_csv()
    print("Processo de tratamento dos arquivos")

    inclusao_dados_coluna()
    print("processo de criação concluído")


if __name__ == "__main__":
    preparar_transformacao_arquivos()