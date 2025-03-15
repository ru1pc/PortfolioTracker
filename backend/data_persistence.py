import sqlite3
import pandas as pd
import os
import re

from utils.logger import logger

DATABASE_PATH = "db/database.db"


def initialize_db(df=None):
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    #Initialize the SQLite database and create table if they don't exist.
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        if df is not None:
            columns_sql = ", ".join([re.sub(r"[^a-zA-Z0-9_]", "_", col) for col in df.columns])
           
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS transactions (
                    {columns_sql}
                )
            """)
            logger.info("Intialized 'transactions' table.")
            conn.commit()

             # Verificar o esquema da tabela
            cursor.execute("PRAGMA table_info(transactions);")
            schema = cursor.fetchall()
            logger.info("Table schema: %s", schema)
            
            # Se quiser testar a inserção e leitura de dados
            if not df.empty:
                df.to_sql("transactions", conn, if_exists="append", index=False)
                logger.info("Inserted data into 'transactions' table.")

                # Ler os dados da tabela
                df_read = pd.read_sql("SELECT * FROM transactions", conn)
                logger.info("Data read from 'transactions':\n%s", df_read)
                print(df_read)

  #  except Exception as e:
  #      logger.error(f"Failed to initialize database: {e}")
    finally:
        conn.close()

def check_db():
    try: 
        conn = sqlite3.connect(DATABASE_PATH)
        # Load the 'transactions' table into a DataFrame
        df = pd.read_sql("SELECT * FROM transactions", conn)
        print(df)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def save_to_db(df, table_name="transactions"):
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        logger.info(f"💾 Data saved to database: {table_name}")
    except Exception as e:
        logger.error(f"Failed to save data to database: {e}")
    finally:
        conn.close()

def load_from_db(table_name="transactions"):

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        logger.info(f"📂 Data loaded from database: {table_name}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from database: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    finally:
        conn.close()