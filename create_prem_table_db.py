import psycopg
import pandas as pd

from table import make_table_df


def make_table_data_for_db(table_df: pd.DataFrame):
    df_dict = table_df.to_dict(orient="records")
    return [
        (row['position'], row['name'], row['played'],
        row['won'], row['drawn'], row['lost'],
        row['goals For'], row['goals Against'], row['goal difference'],
        row['points'], row['previous game'], row['game -2'],
        row['game -3'], row['game -4'], row['game -5'], row['game -6'])
        for row in df_dict
    ]


def create_table(conn: psycopg.Connection):
    sql = """
    DROP TABLE IF EXISTS prem_table;
    CREATE TABLE prem_table (
        position SMALLINT,
        name VARCHAR(100),
        played SMALLINT,
        won SMALLINT,
        drawn SMALLINT,
        lost SMALLINT,
        goals_for SMALLINT,
        goals_against SMALLINT,
        goal_difference SMALLINT,
        points SMALLINT,
        previous_game VARCHAR(1),
        game_2 VARCHAR(1),
        game_3 VARCHAR(1),
        game_4 VARCHAR(1),
        game_5 VARCHAR(1),
        game_6 VARCHAR(1)
        )
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()


def insert_data_to_db(conn: psycopg.Connection, table_data: list[tuple]):
    sql = """
        INSERT INTO prem_table
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    with conn.cursor() as cur:
        cur.executemany(sql, table_data)
        conn.commit()
        

if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)
    table_df = make_table_df()
    table_data_for_db = make_table_data_for_db(table_df)
    create_table(connection)
    insert_data_to_db(connection, table_data_for_db)
    connection.close()