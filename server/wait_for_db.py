import os
import time
import psycopg2
from psycopg2 import OperationalError
import dj_database_url

def wait_for_db():
    """Aguarda o banco de dados estar disponível antes de continuar"""
    if 'DATABASE_URL' not in os.environ:
        print("DATABASE_URL não encontrada, assumindo SQLite local")
        return

    db_config = dj_database_url.parse(os.environ['DATABASE_URL'])

    max_tries = 30
    for i in range(max_tries):
        try:
            conn = psycopg2.connect(
                host=db_config['HOST'],
                port=db_config['PORT'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                dbname=db_config['NAME'],
                sslmode='require'
            )
            conn.close()
            print(f"Banco de dados conectado com sucesso após {i+1} tentativa(s)")
            return
        except OperationalError as e:
            print(f"Tentativa {i+1}/{max_tries} falhou: {e}")
            if i < max_tries - 1:
                time.sleep(2)
            else:
                raise Exception(f"Não foi possível conectar ao banco após {max_tries} tentativas")

if __name__ == "__main__":
    wait_for_db()
