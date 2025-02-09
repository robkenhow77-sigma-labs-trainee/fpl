import pandas as pd
import psycopg
from psycopg.rows import dict_row
import altair as alt

from fixture_analysis import get_fixture_predictions

def get_keepers(conn: psycopg.Connection):
    sql = """
    select player_name, *
    from gameweek
    left join player using (player_id)
    left join position using (position_id)
    where position like 'Goalkeeper'
        and gameweek.gameweek > (select max(gameweek.gameweek) from gameweek) - 10 ;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return cur.fetchall()


def get_midfielders(conn: psycopg.Connection):
    sql = """
    select player_name, *
    from gameweek
    left join player using (player_id)
    left join position using (position_id)
    where position like 'Midfielder'
        and gameweek.gameweek > (select max(gameweek.gameweek) from gameweek) -5 ;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return cur.fetchall()


def get_forwards(conn: psycopg.Connection):
    sql = """
    select player_name, *
    from gameweek
    left join player using (player_id)
    left join position using (position_id)
    where position like 'Forward'
        and gameweek.gameweek > (select max(gameweek.gameweek) from gameweek) -5 ;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return cur.fetchall()


def analyse_keepers(keeps: list[dict]):
    df = pd.DataFrame(keeps)
    price = df[["player_name", "price", "gameweek"]]
    price = price[price["gameweek"] == price["gameweek"].max()]
    df = df[['player_name','gameweek', 'minutes_played',
       'result', 'points',
       'clean_sheets',
       'expected_goals_conceded',
       'saves',
       'bonus_points']]
    df = df.groupby('player_name').sum().sort_values('clean_sheets')
    df = df[df["minutes_played"] > df['minutes_played'].mean()]
    df["expected_goals_conceded"] = df["expected_goals_conceded"].astype(float)
    return df



if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)
    # fixture_predictions = get_fixture_predictions(connection)

    keepers = get_keepers(connection)
    midfielders = get_midfielders(connection)
    forwards = get_forwards(connection)

    keepers_df = analyse_keepers(keepers)
    print(keepers_df)
    
    chart = alt.Chart(keepers_df, title=alt.Title('Keepers', orient='bottom', anchor='start', offset=30)).mark_bar().encode(
    x=alt.X('points:Q'),
    y=alt.Y('saves:Q')
    )
    chart.save('chart.png', inline=True)
    



    connection.close()
