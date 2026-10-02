from src.extract import executar_downloads
from src.treatment import preparar_arquivos_extraidos
from src.transform import preparar_transformacao_arquivos
from src.load import carregar_silver_postgres


def main() -> None:
    print("Iniciando pipeline ETL/ELT - Dados de Combustíveis ANP")

    try:
        executar_downloads()
        preparar_arquivos_extraidos()
        preparar_transformacao_arquivos()
        carregar_silver_postgres()

        print("Pipeline finalizado com sucesso")

    except Exception as erro:
        print(f"Pipeline finalizado com erro: {erro}")


if __name__ == "__main__":
    main()