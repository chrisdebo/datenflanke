import streamlit as st
import utils.helpers as helpers
import utils.plots as plots
from utils.chatbot import get_player_evaluation, get_player_evaluation_german

# Setup the layout
#st.set_page_config(layout="wide")

# Daten laden
dataframe = helpers.preload_data()

# Header with logo and app name placeholder
st.sidebar.image('images/logo.jpg', use_column_width=True)

# Dictionary für Filteroptionen erstellen
leagues = helpers.create_leagues_dict_with_flags()
seasons = helpers.create_seasons_dict()
quality = helpers.create_quality_dict()

# Sidebar-Einstellungen
st.sidebar.header('Spieler auswählen:', divider=True)
selected_league_display = st.sidebar.selectbox('Wettbewerb', options=list(leagues.keys()))
selected_season_display = st.sidebar.selectbox('Saison', options=list(seasons.keys()))

# Zugriff auf die tatsächlichen Werte
selected_league = leagues[selected_league_display]
selected_season = seasons[selected_season_display]

# Dataframe welcher geladen werden soll
data = helpers.get_data_by_league_and_season(dataframe, selected_league, selected_season)
# Formular zur Spielerauswahl in der Seitenleiste
position = st.sidebar.selectbox('Position', ['Abwehrspieler', 'Außenverteidiger', 'Mittelfeldspieler', 'Flügelspieler', 'Angreifer'])
# Spieler aus Dataframe laden und Filter für Position
players =sorted(data[data['position'] == position]['player_name'])
# Auswahl in der Sidebar
player = st.sidebar.selectbox('Spieler', players)
# Auswahl der Qualität
selected_quality_display = st.sidebar.selectbox('Qualität',  options=list(quality.keys()))
selected_quality = quality[selected_quality_display]

# Main content area
st.header('Bewertung von ' + player + ' ' + selected_quality_display, divider=True)

# Variablen übergeben die geplottet werden sollen
attributes = helpers.get_attributes_details(selected_quality, position)


# Plot erstellen
chart = plots.create_player_plot(data, attributes, player, position, selected_league_display, selected_season_display, selected_quality_display)
st.altair_chart(chart, use_container_width=True)


# Beschreibung der Spielerbewertung
with st.spinner('Schreibe Spielerbewertung...'):
    st.write('🏴󠁧󠁢󠁥󠁮󠁧󠁿')
    evaluation = get_player_evaluation(player, attributes, data)
    st.success(evaluation)

    # Beschreibung der Spielerbewertung
with st.spinner('Schreibe Spielerbewertung...'):
    st.write('🇩🇪󠁧󠁢󠁥󠁿')
    evaluation = get_player_evaluation_german(player, attributes, data)
    st.success(evaluation)

# # Noch ein Plot mit einem Attribut als Beispiel
# attributes = get_attributes_details('hold_up_play_z')
# # Plot erstellen
# chart = plots.create_player_plot(data, attributes, player, position, selected_league_display, selected_season_display)
# st.altair_chart(chart, use_container_width=True)

# Footer
st.markdown('---')  # This creates a horizontal line
st.write('This Webapp was created by Christoph Debowiak - [chrisdebo @GitHub](https://github.com/chrisdebo)')