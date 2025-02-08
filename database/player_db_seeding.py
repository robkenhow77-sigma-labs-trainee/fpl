import json
import psycopg


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


def seed(players: list[tuple], conn: psycopg.Connection) -> None:
    sql = """
    INSERT INTO player (player_name, position_id, team_id)
    VALUES (%s, %s, %s)
    """
    with connection.cursor() as cur:
        cur.executemany(sql, players)
        conn.commit()


if __name__ == "__main__":
    conn_string = "postgresql:///fantasy_football?host=localhost"
    connection = psycopg.connect(conn_string)
    players_info = get_players()
    players_for_db = extract_info(players_info)
    print(players_for_db)
    seed(players_for_db, connection)