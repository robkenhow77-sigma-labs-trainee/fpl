DROP TABLE IF EXISTS team CASCADE;
DROP TABLE IF EXISTS player CASCADE;
DROP TABLE IF EXISTS position CASCADE;
DROP TABLE IF EXISTS league CASCADE;
DROP TABLE IF EXISTS gameweek CASCADE;


CREATE TABLE team ( 
    team_id SERIAL PRIMARY KEY NOT NULL,
    team_name VARCHAR(30) NOT NULL
);

CREATE TABLE position (
    position_id SMALLINT PRIMARY KEY NOT NULL,
    position VARCHAR(30) NOT NULL
);

CREATE TABLE player (
    player_id SERIAL PRIMARY KEY NOT NULL,
    player_name VARCHAR(30) NOT NULL,
    team_id SMALLINT NOT NULL,
    position_id SMALLINT NOT NULL,

    FOREIGN KEY (position_id) REFERENCES position(position_id),
    FOREIGN KEY (team_id) REFERENCES team(team_id)
);

CREATE TABLE league ( 
    team_id SMALLINT NOT NULL,
    league_position SMALLINT NOT NULL,
    played SMALLINT NOT NULL,
    won SMALLINT NOT NULL,
    drawn SMALLINT NOT NULL,
    lost SMALLINT NOT NULL,
    goals_for SMALLINT NOT NULL,
    goals_against SMALLINT NOT NULL,
    goal_difference SMALLINT NOT NULL,
    points SMALLINT NOT NULL,
    previous_game VARCHAR(1) NOT NULL,
    game_2 VARCHAR(1) NOT NULL,
    game_3 VARCHAR(1) NOT NULL,
    game_4 VARCHAR(1) NOT NULL,
    game_5 VARCHAR(1) NOT NULL,
    game_6 VARCHAR(1) NOT NULL,

    FOREIGN KEY (team_id) REFERENCES team(team_id)
);


CREATE TABLE gameweek (
    gameweek SERIAL PRIMARY KEY NOT NULL,
    player_id SMALLINT NOT NULL,
    result VARCHAR(1) NOT NULL,
    points SMALLINT NOT NULL,
    game_started SMALLINT NOT NULL,
    minutes_played SMALLINT NOT NULL,
    goals_scored SMALLINT NOT NULL,
    assists SMALLINT NOT NULL,
    expected_goals DECIMAL(5, 2) NOT NULL,
    expected_assists DECIMAL(5, 2) NOT NULL,
    expected_goal_involvements DECIMAL(5,2) NOT NULL,
    clean_sheets SMALLINT NOT NULL,
    goals_conceded SMALLINT NOT NULL,
    expected_goals_conceded DECIMAL(5,2) NOT NULL,
    own_goals SMALLINT NOT NULL,
    penalties_saved SMALLINT NOT NULL,
    penalties_missed SMALLINT NOT NULL,
    yellow_cards SMALLINT NOT NULL,
    red_cards SMALLINT NOT NULL,
    saves SMALLINT NOT NULL,
    bonus_points SMALLINT NOT NULL,
    bonus_point_system SMALLINT NOT NULL,
    influence DECIMAL(5,1) NOT NULL,
    creativity DECIMAL(5,1) NOT NULL,
    threat DECIMAL(5,1) NOT NULL,
    ict_index DECIMAL(5,1) NOT NULL,
    net_transfers INTEGER NOT NULL,
    total_selected_by INTEGER NOT NULL,
    price DECIMAL(5, 2) NOT NULL,

    FOREIGN KEY (player_id) REFERENCES player(player_id)
);