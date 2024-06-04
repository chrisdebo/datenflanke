import streamlit as st
import utils.helpers as helpers
import utils.plots as plots

# Setup the layout
st.set_page_config(layout="wide")

# Daten laden
dataframe = helpers.preload_data()

# Header with logo and app name placeholder
st.sidebar.image('images/logo.jpg', use_column_width=True)

# Dictionary für Filteroptionen erstellen
leagues = helpers.create_leagues_dict_with_flags()
seasons = helpers.create_seasons_dict()
quality = helpers.create_quality_dict()

# Sidebar-Einstellungen
st.sidebar.header('Spieler suchen:', divider=True)
selected_league_display = st.sidebar.selectbox('Wettbewerb', options=list(leagues.keys()))
selected_season_display = st.sidebar.selectbox('Saison', options=list(seasons.keys()))

# Zugriff auf die tatsächlichen Werte
selected_league = leagues[selected_league_display]
selected_season = seasons[selected_season_display]

# Dataframe welcher geladen werden soll
data = helpers.get_data_by_league_and_season(dataframe, selected_league, selected_season)
# Formular zur Spielerauswahl in der Seitenleiste
position = st.sidebar.selectbox('Position', ['Abwehrspieler', 'Außenverteidiger', 'Mittelfeldspieler', 'Flügelspieler', 'Angreifer'])
# Anzahl der Minuten die ein Spieler mindestens gespielt haben muss
minutes_played_min = st.sidebar.number_input('Minimale Spielzeit', min_value=0, max_value=4200, value=0, step=1)


# Main content area
st.markdown('# Spielersuche')
st.markdown('### Wähle maximal 5 Spielerqualitäten aus:')

# Qualitäten auswählen
qualities = list(quality.keys())
qualities.remove('Zusammenfassung')
qualities = st.multiselect('Qualitäten', qualities, max_selections=5)

quality_values = {}
# Für jede Qualität eine Auswahl erstellen
# Alle Elemente sollen nebeneinander angezeigt werden
# Create columns for each quality
if len(qualities) > 0:
    columns = st.columns(len(qualities))
    for i, quality_name in enumerate(qualities):
        # Abrufen des zugehörigen Werts aus dem quality dictionary
        quality_value = quality[quality_name]
        phrase = 'Wichtigkeit: ' + quality_name
        quality_values[quality_value] = columns[i].selectbox(phrase, options=[5, 3, 1], format_func=lambda x: "Wenig" if x == 1 else "Mittel" if x == 3 else "Sehr", index=1)

    st.markdown('---')  # This creates a horizontal line

# Variablen übergeben aus denen der Spieler gesucht werden sollen
best_of = helpers.search_player(selected_league, selected_season, position, minutes_played_min, quality_values)

# zeilennamen ändern
top_10_chart_data = best_of.copy()
best_of.columns = ['Spieler', 'Team', 'Position', 'Minuten gespielt', 'Score']
# für den ersten Eintrag den Spieler plotten in einem expander
if len(qualities) > 0:
    # Für die ersten 10 Einträge den Spieler plotten in einem expander
    for i in range(min(10, len(best_of))):
        with st.expander('#' + str(i+1) + ' ' + best_of.iloc[i]['Spieler'] + ' | ' + best_of.iloc[i]['Team'] + ' | ' + str(best_of.iloc[i]['Minuten gespielt']) + ' Minuten gespielt | Score: ' + '{:.2f}'.format(best_of.iloc[i]['Score'])):
            player = best_of.iloc[i]['Spieler']
            # Auswahl der Qualität
            selected_quality_display = st.selectbox(best_of.iloc[i]['Spieler'], options=list(quality.keys()), key=i, label_visibility='hidden')
            selected_quality = quality[selected_quality_display]
            # Variablen übergeben die geplottet werden sollen
            attributes = helpers.get_attributes_details(selected_quality, position)
            # Plot erstellen
            chart = plots.create_player_plot(data, attributes, player, position, selected_league_display, selected_season_display, selected_quality_display)
            st.altair_chart(chart, use_container_width=True)

if len(qualities) > 0:
    with st.expander('Alle Spieler in einer CSV-Tabelle anzeigen'):
        # erste spalte mit den zahlen entfernen in der darstellung
        st.dataframe(
            best_of,
            hide_index=True
        )

    st.markdown('---')  # This creates a horizontal line

if len(qualities) > 0:
# Create the scatter plot
    chart = plots.create_top10_plot(top_10_chart_data)
    st.altair_chart(chart, use_container_width=True)

# Footer
st.markdown('---')  # This creates a horizontal line
st.write('This Webapp was created by Christoph Debowiak - [chrisdebo @GitHub](https://github.com/chrisdebo)')
