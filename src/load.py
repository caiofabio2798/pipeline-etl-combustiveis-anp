from pathlib import Path
import getpass
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = BASE_DIR / "data" / "silver"

ARQUIVO_SILVER = SILVER_DIR / "base_combustiveis_tratada_final.parquet"


def solicitar_credenciais_postgres() -> dict:
    """
    Solicita as credenciais do PostgreSQL pelo terminal.

    Os valores entre colchetes são valores padrão.
    Caso o usuário pressione Enter sem digitar nada, o valor padrão será usado.
    """

    print("\nInforme as credenciais do PostgreSQL")

    db_user = input("Usuário [postgres]: ") or "postgres"
    db_password = getpass.getpass("Senha: ")
    db_host = input("Host [localhost]: ") or "localhost"
    db_port = input("Porta [5432]: ") or "5432"
    db_name = input("Nome do banco [db_combustiveis_anp]: ") or "db_combustiveis_anp"

    return {
        "user": db_user,
        "password": db_password,
        "host": db_host,
        "port": db_port,
        "database": db_name,
    }


def criar_banco_se_nao_existir(credenciais: dict) -> None:
    """
    Conecta no banco padrão 'postgres' e cria o banco do projeto,
    caso ele ainda não exista.
    """

    nome_banco = credenciais["database"]

    print(f"\nVerificando existência do banco: {nome_banco}")

    conexao = psycopg2.connect(
        dbname="postgres",
        user=credenciais["user"],
        password=credenciais["password"],
        host=credenciais["host"],
        port=credenciais["port"],
    )

    conexao.autocommit = True

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (nome_banco,)
            )

            banco_existe = cursor.fetchone()

            if banco_existe:
                print(f"Banco já existe: {nome_banco}")
            else:
                cursor.execute(f'CREATE DATABASE "{nome_banco}"')
                print(f"Banco criado com sucesso: {nome_banco}")

    finally:
        conexao.close()


def criar_engine_postgres(credenciais: dict):
    """
    Cria a conexão SQLAlchemy com o banco do projeto.
    """

    url_conexao = (
        f"postgresql+psycopg2://{credenciais['user']}:{credenciais['password']}"
        f"@{credenciais['host']}:{credenciais['port']}/{credenciais['database']}"
    )

    return create_engine(url_conexao)


def criar_schema_silver(engine) -> None:
    """
    Cria o schema silver, caso ainda não exista.
    """

    print("Verificando existência do schema silver...")

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))

    print("Schema silver disponível.")


def carregar_silver_postgres(credenciais: dict) -> None:
    """
    Lê a base final da camada silver e carrega no PostgreSQL.

    A tabela silver.precos_combustiveis é criada automaticamente pelo pandas.to_sql().
    Caso a tabela já exista, ela será substituída.
    """

    print("\nIniciando carga da base silver no PostgreSQL...")

    if not ARQUIVO_SILVER.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_SILVER}")

    print(f"Lendo arquivo Parquet: {ARQUIVO_SILVER.name}")

    df = pd.read_csv(
        ARQUIVO_SILVER,
        sep=";",
        encoding="utf-8",
        low_memory=False
    )

    print(f"Linhas carregadas do Parquet: {len(df):,}")
    print(f"Colunas carregadas: {len(df.columns)}")

    engine = criar_engine_postgres(credenciais)

    criar_schema_silver(engine)

    print("Carregando dados na tabela silver.precos_combustiveis...")

    df.to_sql(
        name="precos_combustiveis",
        con=engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=10000,
    )

    print("Carga concluída com sucesso na tabela silver.precos_combustiveis")


if __name__ == "__main__":
    credenciais_postgres = solicitar_credenciais_postgres()
    criar_banco_se_nao_existir(credenciais_postgres)
    carregar_silver_postgres(credenciais_postgres)