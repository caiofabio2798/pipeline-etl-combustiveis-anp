from pathlib import Path
from sqlalchemy import create_engine, text
import getpass
import pandas as pd
from sqlalchemy import create_engine


BASE_DIR = Path(__file__).resolve().parent.parent

SILVER_DIR = BASE_DIR / "data" / "silver"
ARQUIVO_SILVER = SILVER_DIR / "base_combustiveis_tratada.parquet"


def solicitar_credenciais_postgres() -> dict:
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
        "database": db_name
    }


def criar_conexao_postgres():
    credenciais = solicitar_credenciais_postgres()

    url_conexao = (
        f"postgresql+psycopg2://{credenciais['user']}:{credenciais['password']}"
        f"@{credenciais['host']}:{credenciais['port']}/{credenciais['database']}"
    )

    engine = create_engine(url_conexao)

    return engine


def carregar_silver_postgres() -> None:
    print("Iniciando carga da base silver no PostgreSQL...")

    if not ARQUIVO_SILVER.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_SILVER}")

    df = pd.read_parquet(
        ARQUIVO_SILVER
    )

    engine = criar_conexao_postgres()

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))

    df.to_sql(
        name="precos_combustiveis",
        con=engine,
        schema="silver",
        if_exists="replace",
        index=False,
        chunksize=10000
    )

    print("Carga concluída com sucesso na tabela silver.precos_combustiveis")


if __name__ == "__main__":
    carregar_silver_postgres()