import utils.database as db
import pandas as pd
import streamlit as st

from utils import chatbot
from utils.db_connection_string import create_connection_string
import stqdm
import utils.plots as plots


def create_leagues_dict_with_flags():
    leagues = {
        "Bundesliga 🇩🇪": "bundesliga",
        "Premier League 🇬🇧": "premier_league",
        "La Liga 🇪🇸": "laliga",
        "Ligue 1 🇫🇷": "ligue_1",
        "Serie A 🇮🇹": "seria_a",
        "Champions League 🇪🇺": "champions_league",
        "Europa League 🇪🇺": "europa_league",
        "2. Bundesliga 🇩🇪": "bundesliga2",
        "Eredivisie 🇳🇱": "eredivisie",
        "Jupiler Pro League 🇧🇪": "jupiler_pro_league",
        "Championship 🇬🇧": "championship",
        "Liga Portugal 🇵🇹": "liga_portugal",
        "Super Lig 🇹🇷": "super_lig",
    }
    return leagues


def create_seasons_dict():
    seasons = {
        "2023/24": "2023_2024",
        "2022/23": "2022_2023"
    }
    return seasons


def create_quality_dict():
    quality = {
        'Zusammenfassung': 'summary',
        'Abschlussqualität': 'finishing_z',
        'Abstauberqualität': 'poaching_z',
        'Aktive Verteidigung': 'active_defense_z',
        'Ballbehauptung': 'hold_up_play_z',
        'Ballprogression': 'progression_z',
        'Defensives Kopfballspiel': 'defensive_heading_z',
        'Dribbling': 'dribble_z',
        'Effektivität': 'effectiveness_z',
        'Intelligente Verteidigung': 'intelligent_defense_z',
        'Laufqualität': 'run_quality_z',
        'Mannschaftsunterstützung': 'providing_teammates_z',
        'Offensives Kopfballspiel': 'aerial_threat_z',
        'Passqualität': 'passing_quality_z',
        'Pressing': 'pressing_z',
        'Ruhe am Ball': 'composure_z',
        'Spielbeteiligung': 'involvement_z',
        'Strafraumgefahr': 'box_threat_z'
    }
    return quality


def describe_level(z_score):
    if z_score >= 1.5:
        description = "überragend"
    elif z_score >= 1:
        description = "sehr gut"
    elif z_score >= 0.5:
        description = "gut"
    elif z_score >= -0.5:
        description = "durchschnittlich"
    elif z_score >= -1:
        description = "unterdurchschnittlich"
    else:
        description = "schlecht"

    return description


def create_x_labels() -> dict:
    x_labels = {
        -1.5: "schlecht",
        -0.75: "unterdurchschnittlich",
        0: "durchschnittlich",
        0.75: "gut",
        1.25: "sehr gut",
        1.75: "überragend"
    }
    return x_labels


def create_y_labels() -> dict:
    y_labels = {
        'aerials_won_z': 'Gewonnene Luftzweikämpfe',
        'aerials_z': 'Luftzweikämpfe',
        'defensive_actions_z': 'Defensive Aktionen',
        'touches_z': 'Ballkontakte',
        'ball_progression_vaep_z': 'Ballprogression VAEP',
        'ball_progression_count_z': 'Ballprogressionen',
        'passes_into_final_third_vaep_z': 'Pässe ins letzte Drittel VAEP',
        'vaep_buildup_z': 'VAEP Spielaufbau',
        'passes_vaep_z': 'Pässe VAEP',
        'crosses_vaep_z': 'Flanken VAEP',
        'passes_into_final_third_count_z': 'Pässe ins letzte Drittel',
        'passes_in_final_third_count_z': 'Pässe im letzten Drittel',
        'count_creative_passes_z': 'Kreative Pässe',
        'assists_z': 'Vorlagen',
        'second_assists_z': 'Vor-Vorlagen',
        'vaep_created_with_passes_z': 'VAEP durch Pässe',
        'deep_completions_z': 'Tiefe Pässe angekommen',
        'xA_z': 'Assists VAEP',
        'dribbles_success_z': 'Erfolgreiche Dribblings',
        'dribbles_vaep_z': 'Dribblings VAEP',
        'xG_created_with_dribbles_z': 'Erwartete Tore durch Dribblings',
        'pressure_resistance_z': 'Druckresistenz',
        'touches_in_box_z': 'Ballkontakte im Strafraum',
        'box_entries_z': 'Strafraumeintritte',
        'goals_z': 'Tore',
        'vaep_shots_z': 'Schüsse VAEP',
        'penalty_area_receptions_z': 'Ballannahmen im Strafraum',
        'shot_conversion_z': 'Schussquote',
        'goals_vaep_z': 'Tore VAEP',
        'ball_recoveries_z': 'Ballrückeroberungen',
        'counterpressing_recoveries_z': 'Gegenpressing Rückeroberungen',
        'interceptions_z': 'Abfangaktionen',
        'defensive_intensity_z': 'Defensive Intensität',
        'counterpressing_interceptions_z': 'Gegenpressing Abfangaktionen',
        'high_turnovers_z': 'Hohe Ballverluste',
        'vaep_per_shot_z': 'VAEP pro Schuss',
        'losses_z': 'Ballverluste',
        'aerials_won_offensive_value_z': 'Off. Wert gewonnener Luftzweikämpfe',
        'attacking_aerials_won_offensive_value_z': 'Off. VAEP Wert off. Luftzweikämpfe',
        'attacking_aerials_won_z': 'Off. Luftzweikämpfe',
        'headed_plays_z': 'Kopfballaktionen',
        'defensive_aerials_won_z': 'Defensive gewonnene Luftzweikämpfe',
        'defensive_aerials_won_defensive_value_z': 'Defensiver Wert gewonnener Luftzweikämpfe',
        'aerials_won_defensive_value_z': 'Defensiver Wert gewonnener Luftzweikämpfe',
        'tackles_success_z': 'Erfolgreiche Tacklings',
        'defensive_actions_defensive_value_z': 'Def. Wert def. Aktionen',
        'possessions_won_z': 'Gewonnene Ballbesitze',
        'ball_runs_vaep_z': 'Ballläufe VAEP',
        'deep_runs_vaep_z': 'Tiefe Läufe VAEP',
        'carries_offensive_value_z': 'Offensiver Wert Dribblings',
        'xG_z': 'Erwartete Tore',
        'link_up_plays_attack_z': 'Angriffsverbindungen',
        'long_ball_receptions_z': 'Lange Ballannahmen',
        'involvement_z': 'Spielbeteiligung',
        'progression_z': 'Ballprogression',
        'composure_z': 'Ruhe am Ball',
        'aerial_threat_z': 'Offensives Kopfballspiel',
        'defensive_heading_z': 'Defensives Kopfballspiel',
        'active_defense_z': 'Aktive Verteidigung',
        'intelligent_defense_z': 'Intelligente Verteidigung',
        'passing_quality_z': 'Passqualität',
        'providing_teammates_z': 'Mannschaftsunterstützung',
        'box_threat_z': 'Strafraumgefahr',
        'effectiveness_z': 'Effektivität',
        'pressing_z': 'Pressing',
        'run_quality_z': 'Laufqualität',
        'finishing_z': 'Abschlussqualität',
        'poaching_z': 'Abstauberqualität',
        'dribble_z': 'Dribbling',
        'hold_up_play_z': 'Ballbehauptung'
    }
    return y_labels


def get_attributes_summary(position) -> list:
    if position == 'Abwehrspieler':
        a = ['involvement_z', 'progression_z', 'composure_z', 'aerial_threat_z', 'defensive_heading_z',
             'active_defense_z', 'intelligent_defense_z']
    elif position == 'Mittelfeldspieler':
        a = ['involvement_z', 'progression_z', 'passing_quality_z', 'providing_teammates_z', 'box_threat_z',
             'active_defense_z', 'intelligent_defense_z', 'effectiveness_z']
    elif position == 'Angreifer':
        a = ['involvement_z', 'pressing_z', 'run_quality_z', 'finishing_z', 'poaching_z',
             'aerial_threat_z', 'providing_teammates_z', 'hold_up_play_z']
    elif position == 'Flügelspieler':
        a = ['involvement_z', 'passing_quality_z', 'providing_teammates_z', 'dribble_z', 'box_threat_z',
             'finishing_z', 'run_quality_z', 'pressing_z', 'effectiveness_z']
    elif position == 'Außenverteidiger':
        a = ['involvement_z', 'progression_z', 'passing_quality_z', 'providing_teammates_z', 'run_quality_z',
             'active_defense_z', 'intelligent_defense_z']
    else:
        a = []
    return a


def get_attributes_details(attribute, position) -> list:
    if attribute == 'hold_up_play_z':
        stats = ['link_up_plays_attack_z', 'long_ball_receptions_z', 'aerials_won_z', 'pressure_resistance_z',
                 'losses_z']
    elif attribute == 'providing_teammates_z':
        stats = ['assists_z', 'xA_z', 'deep_completions_z', 'count_creative_passes_z', 'second_assists_z',
                 'vaep_created_with_passes_z']
    elif attribute == 'dribble_z':
        stats = ['dribbles_success_z', 'dribbles_vaep_z', 'xG_created_with_dribbles_z', 'pressure_resistance_z']
    elif attribute == 'involvement_z':
        stats = ['aerials_z', 'defensive_actions_z', 'touches_z', 'vaep_buildup_z']
    elif attribute == 'box_threat_z':
        stats = ['touches_in_box_z', 'box_entries_z', 'goals_z', 'vaep_shots_z', 'penalty_area_receptions_z']
    elif attribute == 'passing_quality_z':
        stats = ['passes_vaep_z', 'crosses_vaep_z', 'passes_into_final_third_count_z', 'passes_in_final_third_count_z',
                 'count_creative_passes_z']
    elif attribute == 'poaching_z':
        stats = ['xG_z', 'vaep_per_shot_z', 'goals_z', 'penalty_area_receptions_z']
    elif attribute == 'run_quality_z':
        stats = ['ball_runs_vaep_z', 'box_entries_z', 'deep_runs_vaep_z', 'carries_offensive_value_z',
                 'penalty_area_receptions_z']
    elif attribute == 'finishing_z':
        stats = ['goals_z', 'shot_conversion_z', 'goals_vaep_z']
    elif attribute == 'active_defense_z':
        stats = ['defensive_actions_defensive_value_z', 'defensive_actions_z', 'possessions_won_z']
    elif attribute == 'defensive_heading_z':
        stats = ['aerials_won_z', 'aerials_won_defensive_value_z', 'defensive_aerials_won_z',
                 'defensive_aerials_won_defensive_value_z']
    elif attribute == 'aerial_threat_z':
        stats = ['aerials_won_z', 'aerials_won_offensive_value_z', 'attacking_aerials_won_z',
                 'attacking_aerials_won_offensive_value_z', 'headed_plays_z']
    elif attribute == 'composure_z':
        stats = ['high_turnovers_z', 'losses_z', 'pressure_resistance_z']
    elif attribute == 'progression_z':
        stats = ['ball_progression_vaep_z', 'passes_into_final_third_vaep_z', 'passes_in_final_third_count_z']
    elif attribute == 'pressing_z':
        stats = ['defensive_intensity_z', 'counterpressing_recoveries_z', 'counterpressing_interceptions_z']
    elif attribute == 'effectiveness_z':
        stats = ['passes_vaep_z', 'dribbles_vaep_z', 'high_turnovers_z', 'ball_recoveries_z', 'vaep_per_shot_z']
    elif attribute == 'intelligent_defense_z':
        stats = ['ball_recoveries_z', 'counterpressing_recoveries_z', 'interceptions_z']
    else:
        stats = get_attributes_summary(position)

    return stats


def get_attributes_list() -> list:
    attributes = ['involvement_z', 'progression_z', 'composure_z', 'aerial_threat_z', 'defensive_heading_z',
                  'active_defense_z', 'intelligent_defense_z', 'passing_quality_z', 'providing_teammates_z',
                  'box_threat_z', 'effectiveness_z', 'pressing_z', 'run_quality_z', 'finishing_z', 'poaching_z',
                  'dribble_z', 'hold_up_play_z']
    return sorted(attributes)


def get_data_by_league_and_season(preloaded_data_df, league, season):
    # Filter the dataframe for the given league and season
    filtered_df = preloaded_data_df[(preloaded_data_df['league'] == league) & (preloaded_data_df['season'] == season)]

    if not filtered_df.empty:
        # Assuming there's only one row per league-season combination
        return filtered_df.iloc[0]['data']
    else:
        # Handle case where no data is found for the given league and season
        print(f"No data found for league: {league}, season: {season}")
        return None


@st.cache_data
def preload_data():
    # Load all data from the database
    leagues = [
        "bundesliga",
        "premier_league",
        "laliga",
        "ligue_1",
        "seria_a",
        "champions_league",
        "europa_league",
        "bundesliga2",
        "eredivisie",
        "jupiler_pro_league",
        "championship",
        "liga_portugal",
        "super_lig",
    ]

    seasons = ["2022_2023", "2023_2024"]
    #seasons = ["2023_2024"]
    #leagues = ["bundesliga"]

    # Initialize an empty list to store the data
    data_list = []

    for season in stqdm.stqdm(seasons):
        for league in stqdm.stqdm(leagues, leave=False):
            data = db.dataframe_from_sql(league, season, create_connection_string())
            data_list.append({'league': league, 'season': season, 'data': data})
            print("Data preloaded for", league, season)

    # Create a new dataframe with columns league, season, and data
    preloaded_data_df = pd.DataFrame(data_list)

    return preloaded_data_df

def search_player(league, season, position, minutes_played_min, quality_values):
    data = get_data_by_league_and_season(preload_data(), league, season)
    # Filter the data for the given position and minutes played
    data = data[(data['position'] == position) & (data['minutes_played'] >= minutes_played_min)]
    # for every key in quality_value, get the z_score from the data and multiply it with the value from quality_values
    # create a new column with the sum of all quality values
    data['quality'] = 0
    for key in quality_values:
        data['quality'] += data[key] * quality_values[key] / 5
    # sort the data by the quality column
    data = data.sort_values(by='quality', ascending=False)

    # dataframe aufbereiten
    data = data[['player_name', 'team_name', 'position', 'minutes_played', 'quality']]
    # kein index anzeige
    data.reset_index(drop=True, inplace=True)
    # zeilen umbenennen
    #data.columns = ['Spieler', 'Team', 'Position', 'Minuten gespielt', 'Score']

    return data

def display_team_players(data: pd.DataFrame, team: str, position: str, quality: dict, selected_league_display: str, selected_season_display: str):
    """
    Displays an expander for each player in the specified team and creates a plot for each player.

    Parameters:
    data (pd.DataFrame): The dataset containing player information.
    team (str): The team to highlight.
    position (str): The position to filter players by.
    quality (dict): A dictionary of qualities.
    selected_league_display (str): The league display name.
    selected_season_display (str): The season display name.
    """
    team_data = data[(data['team_name'] == team) & (data['position'] == position)]

    if team_data.empty:
        st.info(f"Keine Spieler gefunden für '{team}' mit der Position '{position}' und der eingestellten Anzahl an gespielten Minuten.")
        return

    for i in range(len(team_data)):
        player = team_data.iloc[i]
        with st.expander(f"# {i+1} {player['player_name']} | {player['team_name']} | {player['minutes_played']} Minuten gespielt"):
            # Auswahl der Qualität
            selected_quality_display = st.selectbox(player['player_name'], options=list(quality.keys()), key=i, label_visibility='hidden')
            selected_quality = quality[selected_quality_display]
            # Variablen übergeben die geplottet werden sollen
            attributes = get_attributes_details(selected_quality, position)
            # Plot erstellen
            chart = plots.create_player_plot(data, attributes, player['player_name'], position, selected_league_display, selected_season_display, selected_quality_display)
            if chart:
                st.altair_chart(chart, use_container_width=True)
                with st.spinner('Schreibe Spielerbewertung...'):
                    evaluation = chatbot.get_player_evaluation(player['player_name'], attributes, data)
                    st.success(evaluation)
            else:
                st.write(f"No data available for player {player['player_name']} in position {position}.")
