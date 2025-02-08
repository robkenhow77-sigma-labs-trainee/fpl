import json
from time import sleep

import psycopg
from psycopg.rows import dict_row


def get_players():
    with open("stats.json", "r", encoding="UTF-8") as file:
        return json.load(file)


def map_position(position: str) -> int:
    mapping = {
        'Goalkeeper': 1,
        'Defender': 2,
        'Midfielder': 3,
        'Forward': 4,
        'Manager': 5
        }
    return mapping[position]


def map_club(club: str) -> int:
   mapping = {
    "Arsenal": 1,

    "Aston Villa": 2,
    "Villa": 2,

    "Bournemouth": 3,

    "Brentford": 4,

    "Brighton & Hove Albion": 5,
    'Brighton': 5,

    "Chelsea": 6,

    "Crystal Palace": 7,
    "Palace": 7,

    "Everton": 8,

    "Fulham": 9,

    "Ipswich Town": 10,
    'Ipswich': 10,

    "Leicester City": 11,
    'Leicester': 11,

    "Liverpool": 12,

    "Manchester City": 13,
    'Man City': 13,

    "Manchester United": 14,
    "Man Utd": 14,

    
    "Newcastle United": 15,
    'Newcastle': 15,

    
    "Nottingham Forest": 16,
    "Nott'm Forest": 16,

    "Southampton": 17,
    "Saints": 17,

    "Tottenham Hotspur": 18,
    "Spurs": 18,

    "West Ham United": 19,
    "West Ham": 19,

    "Wolverhampton Wanderers": 20,
    'Wolves': 20
    }
   return mapping[club]


def extract_info(data: list[dict]):
    players = []
    for player in data:
        players.append((
            player["name"],
            map_position(player["position"]),
            map_club(player["club"])
        ))
    return players


def upload_players(players: list[tuple], conn: psycopg.Connection) -> None:
    sql = """
    INSERT INTO player (player_name, position_id, team_id)
    VALUES (%s, %s, %s)
    """
    with connection.cursor() as cur:
        cur.executemany(sql, players)
        conn.commit()


def get_player_id_mapping(conn: psycopg.Connection):
    sql = """
    SELECT player_id, player_name FROM player;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        data = cur.fetchall()
        return {player["player_name"]: player["player_id"] for player in data}


def get_player_gameweek(player: list[dict], player_mapping: dict):
    player_stats = []
    gameweeks = player["stats"]
    for week in gameweeks:
        player_id = player_mapping[player["name"]]
        player_stats.append((
                week["GW"],
                player_id,
                week["Result"],
                week["Pts"],
                week["ST"],
                week["MP"],
                week["GS"],
                week["A"],
                week["xG"],
                week["xA"],
                week["xGI"],
                week["CS"],
                week["GC"],
                week["xGC"],
                week["OG"],
                week["PS"],
                week["PM"],
                week["YC"],
                week["RC"],
                week["S"],
                week["BP"],
                week["BPS"],
                week["I"],
                week["C"],
                week["T"],
                week["II"],
                week["NT"],
                week["TSB"],
                week["\u00a3"].replace("£", ""),
            ))
    return player_stats


def upload_gameweeks(players: list[dict], player_mapping, conn: psycopg.Connection):
    cur = conn.cursor()
    sql = """
    INSERT INTO gameweek (
        gameweek,
        player_id,
        result,
        points,
        game_started,
        minutes_played,
        goals_scored,
        assists,
        expected_goals,
        expected_assists,
        expected_goal_involvements,
        clean_sheets,
        goals_conceded,
        expected_goals_conceded,
        own_goals,
        penalties_saved,
        penalties_missed,
        yellow_cards,
        red_cards,
        saves,
        bonus_points,
        bonus_point_system,
        influence,
        creativity,
        threat,
        ict_index,
        net_transfers,
        total_selected_by,
        price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

    """
    for player in players:
        data = get_player_gameweek(player, player_mapping)
        cur.executemany(sql, data)
        conn.commit()
    cur.close()


if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)
    players_info = get_players()
    player_id_mapping = get_player_id_mapping(connection)

    # Players table
    players_for_db = extract_info(players_info)
    upload_players(players_for_db, connection)
    print("uploaded players")
    sleep(5)

    # Gameweek table
    upload_gameweeks(players_info, player_id_mapping, connection)
    connection.close()