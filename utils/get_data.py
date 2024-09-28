from collections import Counter
import pandas as pd
import streamlit as st
from utils.helpers import *


@st.cache_resource
def db_connection():
    # Verbindung zur Datenbank
    conn = st.connection('whoscored_db', type='sql')
    return conn


@st.cache_data
def get_data_league(league, season):
    # Verbindung
    conn = db_connection()

    # Generieren des Tabellennamens basierend auf den Parametern
    actions_table = f"{league}_{season}_actions"
    vaep_table = f"{league}_{season}_vaep"

    # SQL-Query
    sql_query = f"""
                SELECT ba.game_id, ba.original_event_id, ba.period_id, ba.time_seconds,
                       ba.start_x, ba.end_x, ba.start_y, ba.end_y,
                       ba.type_id, 
                       ba.bodypart_id, 
                       ba.result_id,
                       p.player_name, 
                       ba.vaep_value,
                       ba.offensive_value, 
                       ba.defensive_value, 
                       t.team_name
                FROM {actions_table} ba 
                INNER JOIN teams t ON t.team_id = ba.team_id  
                INNER JOIN players p ON p.player_id = ba.player_id
                """

    # Daten abfragen
    data = conn.query(sql_query)
    return data


@st.cache_data
def get_games(league, season):
    # Verbindung
    conn = db_connection()

    # Generieren des Tabellennamens für die Spiele basierend auf den Parametern
    games_table = f"{league}_{season}_games"

    # SQL-Query
    sql_query = f"""
                SELECT bg.game_id, bg.season_id, bg.competition_id, bg.game_day, bg.game_date, bg.home_score, bg.away_score, bg.duration, bg.referee, bg.venue, bg.attendance, bg.home_manager, bg.away_manager, t.team_name AS home_team, t1.team_name AS away_team
                FROM {games_table} bg 
                    INNER JOIN teams t ON ( t.team_id = bg.home_team_id  )  
                    INNER JOIN teams t1 ON ( t1.team_id = bg.away_team_id  )   
                """
    games = conn.query(sql_query)
    return games


@st.cache_data
def join_data_with_games(data, games):
    # Stelle sicher, dass 'game_id' in beiden DataFrames vorhanden ist
    if 'game_id' in data.columns and 'game_id' in games.columns:
        # Verknüpfen der DataFrames
        merged_data = pd.merge(data, games, on='game_id', how='left')
        return merged_data
    else:
        print("Fehler: 'game_id' ist nicht in beiden DataFrames vorhanden.")
        return None


@st.cache_data
def get_player_games(league, season):
    # Verbindung
    conn = db_connection()

    # Generieren des Tabellennamens für die Spieler-Spiele basierend auf den Parametern
    player_games_table = f"{league}_{season}_player_games"

    # SQL-Query
    sql_query = f"""
                SELECT bpg.game_id, bpg.team_id, bpg.is_starter, bpg.minutes_played, bpg.starting_position, p.player_name
                FROM {player_games_table} bpg 
                    INNER JOIN players p ON ( p.player_id = bpg.player_id  )  
                """
    player_games = conn.query(sql_query)
    return player_games

@st.cache_data
def process_player_data(player_games):
    # Gruppieren nach Spieler und Aggregieren der Minuten und Positionen
    grouped = player_games.groupby('player_name').agg({'minutes_played': 'sum', 'starting_position': lambda x: list(x)})

    # Berechnen der häufigsten Startposition, ignoriere 'Sub' wenn andere Positionen vorhanden sind
    # Berechnen der häufigsten Startposition
    def most_common_position(positions):
        if all(pos == 'Sub' for pos in positions):
            # Alle Positionen sind 'Sub'
            return 'Sub'
        else:
            # Entferne 'Sub' aus der Liste, falls andere Positionen vorhanden sind
            filtered_positions = [pos for pos in positions if pos != 'Sub']
            positions_counter = Counter(filtered_positions)
            return positions_counter.most_common(1)[0][0] if filtered_positions else 'Sub'

    # Anwenden der Funktion für die häufigste Startposition
    grouped['most_common_position'] = grouped['starting_position'].apply(most_common_position)

    # Entfernen der ursprünglichen starting_position Spalte
    grouped.drop(columns=['starting_position'], inplace=True)

    # Zurücksetzen des Index, um player_name als Spalte zu haben
    return grouped.reset_index()

@st.cache_data
def calculate_vaep_ratings(data, player_games):
    # Add a count column to data
    data["count"] = 1

    # Group player_games by player_name and sum minutes_played
    mp = player_games[["player_name", "minutes_played", "most_common_position"]].groupby(
        "player_name").sum().reset_index()

    # Merge data with the summed minutes_played
    stats = data.merge(mp)

    # Calculate VAEP ratings and normalize for minutes played
    stats["vaep_rating"] = stats.vaep_value * 90 / stats.minutes_played
    stats["offensive_rating"] = stats.offensive_value * 90 / stats.minutes_played
    stats["defensive_rating"] = stats.defensive_value * 90 / stats.minutes_played

    return stats, mp

# function preload_data to load all data from the database in cache
def preload_data():
    # Load all data from the database
    leagues = [
        "bundesliga",
        # "premier_league",
        # "laliga",
        # "ligue_1",
        # "seria_a",
        # "champions_league",
        # "europa_league",
        "bundesliga2",
        # "eredivisie",
        # "jupiler_pro_league",
        # "championship",
        # "liga_portugal",
        # "super_lig",
    ]
    seasons = ["2023_2024"]
    for league in leagues:
        for season in seasons:
            get_data_league(league, season)
            get_games(league, season)
            get_player_games(league, season)
            print("Data preloaded for", league, season)

    get_data_league('bundesliga', "2024_2025")
    get_games('bundesliga', "2024_2025")
    get_player_games('bundesliga', "2024_2025")

