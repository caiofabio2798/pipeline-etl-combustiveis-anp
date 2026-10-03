from src.extract import executar_downloads
from src.treatment import preparar_arquivos_extraidos
from src.transform import preparar_transformacao_arquivos
from src.load import (
    solicitar_credenciais_postgres,
    criar_banco_se_nao_existir,
    carregar_silver_postgres,
)


def main() -> None:
    print("Iniciando pipeline ETL/ELT - Dados de Combustíveis ANP")

    try:
        # 1. Solicita credenciais do PostgreSQL uma única vez
        credenciais = solicitar_credenciais_postgres()

        # 2. Cria o banco do projeto, caso não exista
        criar_banco_se_nao_existir(credenciais)

        # 3. Executa etapa de extração
        executar_downloads()

        # 4. Executa preparação dos arquivos
        preparar_arquivos_extraidos()

        # 5. Executa transformação dos dados
        preparar_transformacao_arquivos()

        # 6. Carrega a base silver no PostgreSQL
        carregar_silver_postgres(credenciais)

        print("Pipeline finalizado com sucesso")

    except Exception as erro:
        print(f"Pipeline finalizado com erro: {erro}")


if __name__ == "__main__":
    main()