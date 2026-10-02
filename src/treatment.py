from pathlib import Path
import zipfile
import shutil
import os
import pandas as pd
import unicodedata


BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = BASE_DIR / "data" / "bronze"
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"

def criar_pasta(caminho: Path) -> None:
    caminho.mkdir(parents=True, exist_ok=True)


def descompactar_varios_zips(
    diretorio_origem: Path = BRONZE_DIR,
    diretorio_destino: Path = EXTRACTED_DIR,
) -> None:
    criar_pasta(diretorio_destino)

    arquivos_zip = list(diretorio_origem.glob("*.zip"))

    if not arquivos_zip:
        print("Nenhum arquivo ZIP encontrado na pasta bronze.")
        return

    for caminho_zip in arquivos_zip:
        try:
            print(f"Descompactando ZIP: {caminho_zip.name}")

            with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
                zip_ref.extractall(diretorio_destino)

            print(f"ZIP descompactado: {caminho_zip.name}")

        except zipfile.BadZipFile:
            print(f"Arquivo ZIP corrompido ou inválido: {caminho_zip.name}")

        except Exception as erro:
            print(f"Erro ao processar {caminho_zip.name}: {erro}")


def copiar_csvs_bronze_para_extracted(
    diretorio_origem: Path = BRONZE_DIR,
    diretorio_destino: Path = EXTRACTED_DIR,
) -> None:
    criar_pasta(diretorio_destino)

    print(f"Buscando CSVs em: {diretorio_origem}")

    arquivos_csv = list(diretorio_origem.glob("*.csv"))

    print(f"Total de CSVs encontrados na bronze: {len(arquivos_csv)}")

    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado na pasta bronze.")
        return

    for caminho_csv in arquivos_csv:
        destino_csv = diretorio_destino / caminho_csv.name

        if destino_csv.exists():
            print(f"CSV já existe em extracted, pulando: {caminho_csv.name}")
            continue

        shutil.copy2(caminho_csv, destino_csv)
        print(f"CSV copiado para extracted: {caminho_csv.name}")


def renomear_arquivos_csv(
    diretorio_origem: Path = EXTRACTED_DIR,
    prefixo: str = "pre_tratamento_"
) -> None:
    arquivos_csv = list(diretorio_origem.glob("*.csv"))

    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado para renomear.")
        return

    for caminho_antigo in arquivos_csv:
        nome_antigo = caminho_antigo.name

        if nome_antigo.startswith(prefixo):
            print(f"Arquivo já renomeado, pulando: {nome_antigo}")
            continue

        novo_nome = f"{prefixo}{nome_antigo}"
        caminho_novo = diretorio_origem / novo_nome

        if caminho_novo.exists():
            print(f"Arquivo de destino já existe, pulando: {novo_nome}")
            continue

        caminho_antigo.rename(caminho_novo)

        print(f"Renomeado: {nome_antigo} -> {novo_nome}")


def preparar_arquivos_extraidos() -> None:
    print("Iniciando preparação dos arquivos extraídos...")

    descompactar_varios_zips()
    copiar_csvs_bronze_para_extracted()

    print("Preparação dos arquivos extraídos finalizada.")

    renomear_arquivos_csv()
    print("Arquivos renomeados...")


if __name__ == "__main__":
    preparar_arquivos_extraidos()