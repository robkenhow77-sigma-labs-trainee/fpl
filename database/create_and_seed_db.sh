
psql fantasy_football -f create_db.sql
psql fantasy_football -f seed_db.sql
python3 player_and_gameweek.py
python3 create_prem_table_db.py
