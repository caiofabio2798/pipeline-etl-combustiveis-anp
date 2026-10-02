from pathlib import Path
import time
import requests


URLS = [
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2025-01.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2024-02.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2024-01.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2023-02.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2023-01.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2022-02.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/precos-semestrais-ca.zip",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2021-01.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2021-02.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2020-01.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2020-02.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2019-02.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2019-01.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2018-02.csv",
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2018-01.csv",
]


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def criar_pasta(caminho: Path) -> None:
    caminho.mkdir(parents=True, exist_ok=True)
    print(f"Pasta disponível: {caminho}")


def obter_nome_arquivo(url: str) -> str:
    return url.split("/")[-1]


def baixar_arquivo(
    url: str,
    pasta_destino: Path,
    tentativas: int = 5,
    timeout: int = 180,
    chunk_size: int = 1024 * 1024
) -> bool:
    """
    Baixa um arquivo com tentativas automáticas.

    Retorna:
        True  -> download concluído
        False -> download falhou
    """

    nome_arquivo = obter_nome_arquivo(url)
    caminho_final = pasta_destino / nome_arquivo
    caminho_temp = pasta_destino / f"{nome_arquivo}.part"

    if caminho_final.exists() and caminho_final.stat().st_size > 0:
        print(f"Arquivo já existe, pulando: {nome_arquivo}")
        return True

    for tentativa in range(1, tentativas + 1):
        try:
            print(f"Baixando: {nome_arquivo} | tentativa {tentativa}/{tentativas}")

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            with requests.get(
                url,
                stream=True,
                timeout=timeout,
                headers=headers
            ) as response:
                response.raise_for_status()

                tamanho_esperado = response.headers.get("content-length")

                if tamanho_esperado is not None:
                    tamanho_esperado = int(tamanho_esperado)

                bytes_baixados = 0

                with open(caminho_temp, "wb") as arquivo:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            arquivo.write(chunk)
                            bytes_baixados += len(chunk)

                if tamanho_esperado is not None and bytes_baixados != tamanho_esperado:
                    raise IOError(
                        f"Download incompleto. "
                        f"Esperado: {tamanho_esperado} bytes, "
                        f"baixado: {bytes_baixados} bytes."
                    )

                caminho_temp.rename(caminho_final)

                print(f"Download concluído: {nome_arquivo}")
                return True

        except Exception as erro:
            print(f"Erro ao baixar {nome_arquivo}: {erro}")

            if caminho_temp.exists():
                caminho_temp.unlink()

            if tentativa < tentativas:
                tempo_espera = tentativa * 5
                print(f"Aguardando {tempo_espera} segundos para tentar novamente...")
                time.sleep(tempo_espera)
            else:
                print(f"Falha definitiva no download: {nome_arquivo}")
                return False


def executar_downloads() -> None:
    criar_pasta(BRONZE_DIR)

    arquivos_com_erro = []

    for url in URLS:
        sucesso = baixar_arquivo(url, BRONZE_DIR)

        if not sucesso:
            arquivos_com_erro.append(url)

    if arquivos_com_erro:
        print("\nAlguns arquivos não foram baixados:")
        for url in arquivos_com_erro:
            print(f"- {url}")

        raise RuntimeError("Pipeline interrompido. Existem arquivos com erro no download.")

    print("\nTodos os downloads foram concluídos com sucesso.")