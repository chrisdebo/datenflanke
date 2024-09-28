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
        "2024/25": "2024_2025",
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

    seasons = ["2022_2023", "2023_2024", '2024_2025']
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

def create_team_colors():
    team_colors = {
        'AC Milan': '#FB090B',  # Rot
        'Augsburg': '#BA3733',  # Rot
        'Atletico': '#CB3524',  # Rot-Weiß
        'Arsenal': '#EF0107',  # Rot
        'Aston Villa': '#670E36',  # Weinrot
        'Athletic Bilbao': '#BB0000',  # Dunkelrot
        'Atalanta': '#1F2F56',  # Dunkelblau
        'Auxerre': '#123163',  # Blau
        'AC Ajaccio': '#ED1C24',  # Rot
        'AEK Athens': '#FFE600',  # Gelb
        'AEK Larnaca': '#0033A0',  # Blau
        'AZ Alkmaar': '#FF0000',  # Rot
        'Adana Demirspor': '#0055A4',  # Blau
        'Ajax': '#FF4500',  # Orange
        'Alanyaspor': '#FF8C00',  # Orange
        'Almere City FC': '#FF0000',  # Rot
        'Almeria': '#BA0C2F',  # Dunkelrot
        'Anderlecht': '#0000FF',  # Blau
        'Angers': '#000000',  # Schwarz
        'Ankaragucu': '#0047AB',  # Dunkelblau
        'Antalyaspor': '#E32636',  # Rot
        'Aris Limassol': '#FFFF00',  # Gelb
        'Arminia Bielefeld': '#004C8C',  # Blau
        'Arouca': '#FFD700',  # Gold

        'Barcelona': '#004D98',  # Blau und Rot
        'Bayern': '#DC052D',  # Rot
        'Benfica': '#E20E0E',  # Rot
        'Besiktas': '#000000',  # Schwarz
        'Bochum': '#1E73BE',  # Blau
        'Borussia Dortmund': '#DAA520',  # Gelb
        'Borussia M.Gladbach': '#00A66C',  # Grün
        'Brentford': '#FFC20E',  # Gelb
        'Brighton': '#0057B8',  # Blau
        'Bristol City': '#FF0000',  # Rot
        'Burnley': '#6C1D45',  # Burgund
        'Birmingham': '#0072CE',  # Blau
        'Blackburn': '#0000FF',  # Blau
        'Blackpool': '#FFA500',  # Orange
        'Boavista': '#000000',  # Schwarz
        'Bodoe/Glimt': '#FFD700',  # Gold
        'Bologna': '#1E73BE',  # Blau
        'Bournemouth': '#DA291C',  # Rot
        'Braga': '#AD2121',  # Rot
        'Cadiz': '#FFCD00',  # Dunkelgelb
        'Cagliari': '#D4001F',  # Rot
        'Celtic': '#008000',  # Grün
        'Chelsea': '#034694',  # Blau
        'Clermont Foot': '#800020',  # Burgund
        'Club Bruges': '#0053A0',  # Blau
        'Copenhagen': '#00A9E0',  # Hellblau
        'Crystal Palace': '#1B458F',  # Blau
        'Darmstadt': '#EA6A47',  # Orange
        'Deportivo Alaves': '#0D47A1',  # Blau
        'Dinamo Zagreb': '#002366',  # Dunkelblau
        'Eintracht Frankfurt': '#E1000F',  # Rot
        'Elche': '#005C1F',  # Dunkelgrün
        'Empoli': '#1E90FF',  # Hellblau
        'Espanyol': '#1E90FF',  # Blau
        'Everton': '#003399',  # Blau

        'Cambuur': '#FFD700',  # Gold
        'Cardiff': '#0000FF',  # Blau
        'Casa Pia AC': '#8B0000',  # Dunkelrot
        'Celta Vigo': '#00529F',  # Dunkelblau
        'Cercle Bruges': '#008000',  # Grün
        'Chaves': '#FFD700',  # Gold
        'Coventry': '#007FFF',  # Blau
        'Cremonese': '#E30613',  # Rot
        'Dynamo Kyiv': '#0000FF',  # Blau
        'Eintracht Braunschweig': '#FDB913',  # Gold
        'Elversberg': '#0047AB',  # Dunkelblau
        'Estoril': '#FFD700',  # Gold
        'Estrela da Amadora': '#FF4500',  # Orange
        'Eupen': '#000000',  # Schwarz
        'Excelsior': '#FF0000',  # Rot

        'FC Koln': '#E31E24',  # Rot
        'FC Midtjylland': '#D41243',  # Dunkelrot
        'FC Sheriff': '#FEDD00',  # Gold
        'FC Utrecht': '#FF4500',  # Orange
        'FC Zuerich': '#0000FF',  # Blau
        'FK Crvena Zvezda': '#C8102E',  # Rot
        'Feyenoord': '#FF0000',  # Rot
        'Fiorentina': '#7C2D83',  # Violett
        'Fortuna Duesseldorf': '#E31E24',  # Gold
        'Freiburg': '#E30613',  # Rot
        'Fulham': '#CC0000',  # Rot
        'Galatasaray': '#FF6700',  # Orange
        'Genoa': '#CF1020',  # Rot und Blau
        'Getafe': '#0050BC',  # Blau
        'Girona': '#ED1C24',  # Rot
        'Granada': '#CF142B',  # Dunkelrot
        'Greuther Fuerth': '#009E60',  # Grün
        'Hertha Berlin': '#005CA9',  # Blau
        'Hoffenheim': '#0077C0',  # Blau
        'Huddersfield': '#0BDA51',  # Hellgrün
        'Hull': '#FFA500',  # Orange

        'FC Emmen': '#FFD700',  # Gold
        'FC Groningen': '#008000',  # Grün
        'FC Heidenheim': '#003b79',  # Blau
        'FC Volendam': '#F08080',  # Hellrot
        'Famalicao': '#0000FF',  # Blau
        'Farense': '#FF4500',  # Orange
        'Fatih Karagumruk': '#FF0000',  # Rot
        'Fenerbahce': '#FFFF00',  # Gelb
        'Ferencvaros': '#008000',  # Grün
        'Fortuna Sittard': '#FFD700',  # Gold
        'Frosinone': '#FFDE00',  # Goldgelb
        'Gaziantep FK': '#FF0000',  # Rot
        'Genk': '#0000FF',  # Blau
        'Gent': '#2E8B57',  # Seegrün
        'Gil Vicente': '#FFD700',  # Gold
        'Giresunspor': '#228B22',  # Waldgrün
        'Go Ahead Eagles': '#FFFF00',  # Gelb
        'HJK': '#0000CD',  # Dunkelblau
        'Haecken': '#FFD700',  # Gold
        'Hamburg': '#0000FF',  # Blau
        'Hannover': '#D11241',  # Dunkelrot
        'Hansa Rostock': '#0000FF',  # Blau
        'Hatayspor': '#FF6347',  # Tomatenrot
        'Heracles': '#000000',  # Schwarz
        'Holstein Kiel': '#0000FF',  # Blau

        'Inter': '#0057A1',  # Blau
        'Juventus': '#000000',  # Schwarz
        'LASK': '#000000',  # Schwarz
        'Las Palmas': '#FFC72C',  # Dunkelgelb
        'Lazio': '#87CEEB',  # Himmelblau
        'Le Havre': '#004B87',  # Dunkelblau
        'Lecce': '#FFCB05',  # Gelb
        'Leeds': '#FFCD00',  # Gelb
        'Leicester': '#0053A0',  # Blau
        'Lens': '#FDE103',  # Dunkelgelb
        'Lille': '#DA251D',  # Rot
        'Lorient': '#FFA500',  # Orange
        'Lyon': '#2F407B',  # Dunkelblau
        'Marseille': '#1E7FCB',  # Blau
        'Metz': '#E30613',  # Rot
        'Monaco': '#ED2939',  # Rot
        'Montpellier': '#E7005A',  # Pink
        'Nantes': '#FFEC00',  # Dunkelgelb
        'Nice': '#ED1C24',  # Rot
        'PSG': '#004170',  # Dunkelblau
        'PSV Eindhoven': '#FF0000',  # Rot
        'Porto': '#0050B5',  # Blau
        'Preston': '#FFFFFF',  # Weiß
        'QPR': '#0000FF',  # Blau
        'RBL': '#D40511',  # Rot
        'Rangers': '#0C1C8C',  # Blau
        'Rayo Vallecano': '#CE2029',  # Rot
        'Real Betis': '#004D98',  # Blau
        'Real Madrid': '#FFFFFF',  # Weiß
        'Real Sociedad': '#0069AA',  # Blau
        'Real Valladolid': '#560319',  # Dunkelrot
        'Reims': '#ED1C24',  # Rot
        'Rennes': '#ED1C24',  # Rot
        'Rio Ave': '#008000',  # Grün
        'Roma': '#9D2933',  # Weinrot
        'Royal Antwerp': '#FA1A1A',  # Rot

        'PEC Zwolle': '#0000FF',  # Blau
        'Pacos de Ferreira': '#FFD700',  # Gold
        'Paderborn': '#0000FF',  # Blau
        'Panathinaikos': '#008000',  # Grün
        'Pendikspor': '#FF4500',  # Orange
        'Plymouth': '#008000',  # Grün
        'Portimonense': '#000000',  # Schwarz
        'Qarabag FK': '#0000FF',  # Blau
        'RFC Seraing': '#FFD700',  # Gold
        'RKC Waalwijk': '#0000FF',  # Blau
        'RWD Molenbeek': '#FF0000',  # Rot
        'Rakow Czestochowa': '#0000FF',  # Blau
        'Reading': '#0000FF',  # Blau
        'Rizespor': '#00FF00',  # Grün
        'Rotherham': '#FF0000',  # Rot

        'Salzburg': '#D80027',  # Rot
        'Sampdoria': '#1C39BB',  # Blau
        'Sassuolo': '#008F39',  # Grün
        'Schalke': '#0055A4',  # Blau
        'Sevilla': '#ED1C24',  # Rot
        'Shakhtar': '#FF6A00',  # Orange
        'Sheff Utd': '#EE2737',  # Rot
        'Southampton': '#D71920',  # Rot
        'Sporting': '#009A3E',  # Grün
        'Stuttgart': '#e32219',  # Rot
        'Sunderland': '#FF0000',  # Rot
        'Swansea': '#FFA500',  # Orange

        'SC Heerenveen': '#0000FF',  # Blau
        'Salernitana': '#8A1538',  # Weinrot
        'Santa Clara': '#FF0000',  # Rot
        'Servette FC': '#DD0000',  # Rot
        'Sheff Wed': '#003399',  # Blau
        'Sivasspor': '#FF4500',  # Orange
        'Slavia Prague': '#C8102E',  # Rot
        'Sparta Prague': '#FF0000',  # Rot
        'Sparta Rotterdam': '#FF4500',  # Orange
        'Spezia': '#000080',  # Dunkelblau
        'Sporting Charleroi': '#000000',  # Schwarz
        'St. Pauli': '#FFD700',  # Gold
        'St.Truiden': '#FADA5E',  # Gold
        'Standard Liege': '#ED2939',  # Rot
        'Stoke': '#E03A3E',  # Rot
        'Strasbourg': '#1E73BE',  # Blau
        'Sturm Graz': '#000000',  # Schwarz
        'Sandhausen': '#000000',  # Schwarz

        'Torino': '#8B0000',  # Dunkelrot
        'Tottenham': '#132257',  # Dunkelblau
        'Toulouse': '#800080',  # Lila
        'Trabzonspor': '#D52B1E',  # Rot
        'Troyes': '#1E90FF',  # Blau
        'Twente': '#FF0000',  # Rot
        'Udinese': '#000000',  # Schwarz
        'Union Berlin': '#000000',  # Schwarz
        'Valencia': '#F47920',  # Dunkelorange
        'Verona': '#1E90FF',  # Hellblau
        'Villarreal': '#FFC72C',  # Dunkelgelb
        'Vitesse': '#FFD700',  # Gold
        'Watford': '#FBEC5D',  # Gelb
        'Werder Bremen': '#137F49',  # Dunkelgrün
        'West Ham': '#7A263A',  # Burgund
        'Wolfsburg': '#6DBA42',  # Grün
        'Wolves': '#FDB913',  # Gold
        'Young Boys': '#FDEE00',  # Gelb

        'TSC Backa Topola': '#FF4500',  # Orange
        'Union St.Gilloise': '#FFD700',  # Gold
        'Vitoria de Guimaraes': '#0000FF',  # Blau
        'Vizela': '#0000CD',  # Dunkelblau
        'WBA': '#0000CD',  # Dunkelblau
        'Westerlo': '#FFD700',  # Gold
        'Wigan': '#0000FF',  # Blau
        'Zulte Waregem': '#FF0000',  # Rot
        'Wehen Wiesbaden': '#FFD700',  # Gold
        'Umraniyespor': '#FF4500',  # Orange

    }
    return team_colors