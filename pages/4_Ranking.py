import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
from matplotlib import pyplot as plt, patches

# Custom modules
import utils.helpers as helpers
import utils.plots as plots
from utils.passwords import inject_ga
from utils import get_data

inject_ga()

# Set up the page configuration
st.set_page_config(layout="wide")

# Preload data
get_data.preload_data()

# Sidebar - Logo and Header
st.sidebar.image('images/logo.png', use_column_width=True)
st.sidebar.header('', divider=True)

# Create dictionaries for filter options
leagues = helpers.create_leagues_dict_with_flags()
seasons = helpers.create_seasons_dict()
actiontypes = helpers.create_actiontypes_dict()
bodyparts = helpers.create_bodyparts_dict()

# Convert actiontypes and bodyparts dictionaries to lists
actiontype_labels = list(actiontypes.keys())
bodypart_labels = list(bodyparts.keys())

# Sidebar - League and Season Selection
selected_league_display = st.sidebar.selectbox('League', options=list(leagues.keys()))
selected_season_display = st.sidebar.selectbox('Season', options=list(seasons.keys()))

# Access actual values
selected_league = leagues[selected_league_display]
selected_season = seasons[selected_season_display]

# Create DataFrames for actiontypes, results, and bodyparts
actiontypes_df = helpers.create_actiontypes_dataframe()
results_df = helpers.create_results_dataframe()
bodyparts_df = helpers.create_bodyparts_dataframe()

# Main DataFrame
data = get_data.get_data_league(selected_league, selected_season)

# Get list of all teams
all_teams = ['All'] + sorted(data['team_name'].unique())
selected_teams = st.sidebar.multiselect('Team', options=all_teams, default='All')

# Merge DataFrames with main DataFrame
data = pd.merge(data, actiontypes_df, on='type_id', how='left')
data = pd.merge(data, results_df, on='result_id', how='left')
data = pd.merge(data, bodyparts_df, on='bodypart_id', how='left')

# Retrieve and process player games data
player_games = get_data.get_player_games(selected_league, selected_season)
player_games = get_data.process_player_data(player_games)

# Set variables
today = datetime.today().date()
team_colors = helpers.create_team_colors()

# Calculate VAEP Ratings and normalize for minutes played
vaep_ratings = get_data.calculate_vaep_ratings(data, player_games)
stats = vaep_ratings[0]
mp = vaep_ratings[1]

# Slider for selecting a range of minutes played
max_minutes_played = stats['minutes_played'].max()
values_minutes_played = st.sidebar.slider(
    'Select a range of minutes played',
    0,
    max_minutes_played,
    (60, max_minutes_played)
)

# Multiselect for positions, action types, and body parts with an 'All' option
all_positions = ['All'] + sorted(stats['most_common_position'].unique())
all_actiontypes = ['All'] + sorted(stats['actiontype_name'].unique())
all_bodyparts = ['All'] + sorted(stats['bodypart_name'].unique())

selected_positions = st.sidebar.multiselect('Positions', options=all_positions, default='All')
selected_actiontype_labels = st.sidebar.multiselect('Actiontypes', options=actiontype_labels, default='All')
selected_bodypart_labels = st.sidebar.multiselect('Bodyparts', options=bodypart_labels, default='All')

# Map selected labels to their corresponding IDs
selected_actiontypes = (
    [actiontypes[label] for label in selected_actiontype_labels if label != "All"]
    if "All" not in selected_actiontype_labels else list(actiontypes.values())[1:]
)
selected_bodyparts = (
    [bodyparts[label] for label in selected_bodypart_labels if label != "All"]
    if "All" not in selected_bodypart_labels else list(bodyparts.values())[1:]
)

# Ensure 'All' selection includes all options
if 'All' in selected_positions or not selected_positions:
    selected_positions = all_positions[1:]
if 'All' in selected_teams or not selected_teams:
    selected_teams = all_teams[1:]

# Vordefinierte Zonen
zones = {
    'Strafraum': {'min_x': 88.5, 'max_x': 105, 'min_y': 13.84, 'max_y': 54.16},
    'Mittelfeld': {'min_x': 35, 'max_x': 70, 'min_y': 0, 'max_y': 68},
    'Rechter Flügel': {'min_x': 0, 'max_x': 105, 'min_y': 0, 'max_y': 22.7},
    'Linker Flügel': {'min_x': 0, 'max_x': 105, 'min_y': 45.3, 'max_y': 68},
    'Zentrum': {'min_x': 0, 'max_x': 105, 'min_y': 22.7, 'max_y': 45.3},
    'Gegnerische Hälfte': {'min_x': 52.5, 'max_x': 105, 'min_y': 0, 'max_y': 68},
    'Eigene Hälfte': {'min_x': 0, 'max_x': 52.5, 'min_y': 0, 'max_y': 68}
}

# Positionsfilter in der Sidebar
st.sidebar.markdown("### Positionsfilter")
zone_options = list(zones.keys())
selected_zones = st.sidebar.multiselect('Zonen auswählen', options=zone_options, default=[])

# Filter data based on selections
filtered_stats = stats[
    (stats['minutes_played'] >= values_minutes_played[0]) &
    (stats['minutes_played'] <= values_minutes_played[1]) &
    (stats['team_name'].isin(selected_teams)) &
    (stats['most_common_position'].isin(selected_positions)) &
    (stats['actiontype_name'].isin(selected_actiontypes)) &
    (stats['bodypart_name'].isin(selected_bodyparts))
    ]

# Positionsfilter anwenden
if selected_zones:
    zone_filters = []
    for zone_name in selected_zones:
        zone = zones[zone_name]
        zone_filter = (
                (filtered_stats['start_x'] >= zone['min_x']) &
                (filtered_stats['start_x'] <= zone['max_x']) &
                (filtered_stats['start_y'] >= zone['min_y']) &
                (filtered_stats['start_y'] <= zone['max_y'])
        )
        zone_filters.append(zone_filter)

    # Kombinieren der Filter für die ausgewählten Zonen
    combined_zone_filter = zone_filters[0]
    for zf in zone_filters[1:]:
        combined_zone_filter |= zf  # Logisches OR

    # Anwenden des kombinierten Zonenfilters
    filtered_stats = filtered_stats[combined_zone_filter]
else:
    # Keine Zonen ausgewählt, alle Events einbeziehen
    pass  # Kein Positionsfilter wird angewendet

# Pivot table for risk calculations
df_risk_filtered = pd.pivot_table(
    filtered_stats,
    values='vaep_value',
    index=['player_name'],
    columns=['result_name'],
    aggfunc=np.sum,
    fill_value=0
).reset_index()

# Ensure 'success' and 'fail' columns exist
for result in ['success', 'fail']:
    if result not in df_risk_filtered.columns:
        df_risk_filtered[result] = 0

# Merge with minutes played and normalize per 90 minutes
df_risk_filtered = pd.merge(df_risk_filtered, mp, on=['player_name'])
for result in ['success', 'fail']:
    df_risk_filtered[result] = df_risk_filtered[result] / df_risk_filtered['minutes_played'] * 90
df_risk_filtered.drop(columns=['minutes_played'], inplace=True)

# Main content area
st.header(f'VAEP stats for {selected_league_display} {selected_season_display}', divider=True)
st.markdown('''
#### Players by VAEP Rating
Feel free to select a range of minutes and pick action types and body parts to see how the players are performing.  
If you want to see the players of a specific team, select the team in the sidebar.  
Everything that follows is based on your filtered data.
''')

# Group and aggregate filtered stats
grouped_filtered_stats = filtered_stats.groupby('player_name').agg({
    'minutes_played': 'first',
    'team_name': 'first',
    'vaep_rating': 'sum',
    'offensive_rating': 'sum',
    'defensive_rating': 'sum',
    'vaep_value': 'sum',
    'offensive_value': 'sum',
    'defensive_value': 'sum'
}).reset_index()

grouped_filtered_stats = pd.merge(grouped_filtered_stats, df_risk_filtered, on=['player_name'])

# Sort by VAEP rating
sorted_filtered_stats = grouped_filtered_stats.sort_values(by='vaep_rating', ascending=False)

# Display columns in the DataFrame
columns_to_exclude = ["fail", "offside", "owngoal", "success"]
dataframe_table = sorted_filtered_stats.drop(columns=[col for col in columns_to_exclude if col in sorted_filtered_stats.columns])

# Display DataFrame and explanations
col1, col2 = st.columns([3, 1])
with col1:
    st.dataframe(
        dataframe_table,
        column_config={
            "player_name": "Player",
            "minutes_played": "Minutes",
            "team_name": "Team",
            "vaep_rating": "VAEP Rating",
            "offensive_rating": "Off. Rating",
            "defensive_rating": "Def. Rating",
            "vaep_value": "VAEP Value",
            "offensive_value": "Off. Value",
            "defensive_value": "Def. Value",
            "most_common_position": "Position"
        },
        hide_index=True,
    )
with col2:
    st.markdown('''
    - **VAEP Rating:** Offensive value per 90 minutes + Defensive value per 90 minutes.  
    - **Offensive Rating:** Offensive value per 90 minutes.  
    - **Defensive Rating:** Defensive value per 90 minutes.  
    - **VAEP Value:** Offensive value + Defensive value.  
    - **Offensive Value:** Calculated VAEP value for scoring model.  
    - **Defensive Value:** Calculated VAEP value for conceding model.  
    - **Position:** Most common starting position. Players who only played as a substitute are marked as 'Sub'.
    - **Team:** Team that was tracked for the most appearances.
    ''')

with st.expander('See explanation of positions'):
    st.markdown('''
    - **AMC (Attacking Midfielder Center)**: Central offensive midfielder focused on creating scoring opportunities.
    - **AML (Attacking Midfielder Left)**: Left-sided attacking midfielder, often a winger.
    - **AMR (Attacking Midfielder Right)**: Right-sided attacking midfielder.
    - **DC (Defender Center)**: Central defender responsible for defending the middle part of the defensive line.
    - **DL (Defender Left)**: Left fullback who defends the left flank.
    - **DMC (Defensive Midfielder Center)**: Defensive midfielder positioned ahead of the backline.
    - **DML (Defensive Midfielder Left)**: Left defensive midfielder covering the left side.
    - **DMR (Defensive Midfielder Right)**: Right defensive midfielder covering the right side.
    - **DR (Defender Right)**: Right fullback defending the right flank.
    - **FW (Forward)**: Primary attacker whose main objective is to score goals.
    - **FWL (Forward Left)**: Left-sided forward.
    - **FWR (Forward Right)**: Right-sided forward.
    - **GK (Goalkeeper)**: Player who guards the goal.
    - **MC (Midfielder Center)**: Central midfielder playing a key role in both defense and offense.
    - **ML (Midfielder Left)**: Left midfielder responsible for both defense and attack.
    - **MR (Midfielder Right)**: Right midfielder covering the right side.
    ''')

# Optional: Visualisierung der ausgewählten Zonen
with st.expander('See pitch zones'):
    if selected_zones:
        # Verkleinerte Figur erstellen
        fig, ax = plt.subplots(figsize=(6, 4))
        plots.createPitch(ax)  # Ihre Funktion zum Zeichnen des Spielfelds

        # Ausgewählte Zonen hervorheben
        for zone_name in selected_zones:
            zone = zones[zone_name]
            rect = plt.Rectangle(
                (zone['min_x'], zone['min_y']),
                zone['max_x'] - zone['min_x'],
                zone['max_y'] - zone['min_y'],
                linewidth=1,  # Linienbreite reduziert
                edgecolor='red',
                facecolor='none'
            )
            ax.add_patch(rect)
            ax.text(
                zone['min_x'] + (zone['max_x'] - zone['min_x']) / 2,
                zone['min_y'] + (zone['max_y'] - zone['min_y']) / 2,
                zone_name,
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=6,  # Schriftgröße reduziert
                color='red'
            )
        # Grafik anzeigen
        st.pyplot(fig)
    else:
        st.write("Keine Zone ausgewählt. Alle Events werden berücksichtigt.")
        # Verkleinerte Figur ohne hervorgehobene Zonen anzeigen
        fig, ax = plt.subplots(figsize=(6, 4))
        plots.createPitch(ax)
        st.pyplot(fig)

# Quantity-Quality Trade-Off Plot
st.markdown('''
#### Quantity - Quality Trade-Off
The VAEP rating per player per 90 minutes depends on the average rating per action and the number of actions per 90 minutes.  
Some players have high ratings because they execute a lot of actions per 90 minutes, while others have very high average ratings.

The horizontal line shows the average VAEP rating per player, the vertical line shows the average number of actions per 90 minutes.  
The higher the circle, the more valuable the player's average action.  
The further to the right the circle, the more actions per 90 minutes the player performs.
''')

# Calculate average actions per 90 minutes
action_counts = filtered_stats['player_name'].value_counts()
minutes_played = stats.groupby('player_name')['minutes_played'].first()
avg_actions_per_90 = (action_counts / minutes_played) * 90

# Calculate average VAEP rating per player
avg_vaep_rating = filtered_stats.groupby('player_name')['vaep_rating'].mean()
team_to_player = filtered_stats.groupby('player_name')['team_name'].first()

# Ensure all Series have the same index
common_index = avg_vaep_rating.index.intersection(avg_actions_per_90.index).intersection(team_to_player.index)

# Reindex the Series to the common index
avg_vaep_rating = avg_vaep_rating.loc[common_index]
avg_actions_per_90 = avg_actions_per_90.loc[common_index]
team_to_player = team_to_player.loc[common_index]

# Prepare scatter plot data
scatter_data = pd.DataFrame({
    'player_name': common_index,
    'avg_actions_per_90': avg_actions_per_90.values,
    'avg_vaep_rating': avg_vaep_rating.values,
    'team_name': team_to_player.values
})

# Selection for interactivity
selection = alt.selection_multi(fields=['team_name'], bind='legend')

# Calculate averages for lines
avg_x = scatter_data['avg_actions_per_90'].mean()
avg_y = scatter_data['avg_vaep_rating'].mean()

# Horizontal and vertical lines
horizontal_line = alt.Chart(pd.DataFrame({'y': [avg_y]})).mark_rule(strokeDash=[5, 5], color='grey').encode(y='y:Q')
vertical_line = alt.Chart(pd.DataFrame({'x': [avg_x]})).mark_rule(strokeDash=[5, 5], color='grey').encode(x='x:Q')

# Team colors
unique_teams = sorted(data['team_name'].unique())
team_colors = helpers.create_team_colors()
team_color_range = [team_colors[team] for team in unique_teams if team in team_colors]

# Scatter plot
points = alt.Chart(scatter_data).mark_circle(size=60).encode(
    x=alt.X('avg_actions_per_90:Q', title='Average Actions per 90 Minutes'),
    y=alt.Y('avg_vaep_rating:Q', title='Average VAEP Rating'),
    color=alt.Color('team_name:N', scale=alt.Scale(domain=unique_teams, range=team_color_range)),
    tooltip=[
        'player_name:N',
        'team_name:N',
        alt.Tooltip('avg_actions_per_90:Q', format='.2f'),
        alt.Tooltip('avg_vaep_rating:Q', format='.6f')
    ],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.1))
).add_selection(selection).interactive()

# Combine plot and lines
final_chart = (points + horizontal_line + vertical_line).properties(width=800, height=800).configure_axis(
    labelFontSize=15,
    titleFontSize=15
)

st.altair_chart(final_chart, use_container_width=True)

# Risk-Reward Trade-Off Plot
st.markdown('''
#### Risk - Reward Trade-Off
Here you can see the ratings for the player's successful actions and for the player's unsuccessful actions.  
This can help identify players who take more risk and those who play less risky.

The horizontal line shows the average VAEP rating per player for successful actions, the vertical line shows the average VAEP rating per player for unsuccessful actions.  
The higher the circle, the more reward the player's actions have.  
The further to the left the circle, the more risk the player's actions have.
''')

# Calculate averages for lines
avg_fail = sorted_filtered_stats['fail'].mean()
avg_success = sorted_filtered_stats['success'].mean()

# Horizontal and vertical lines
horizontal_line_rr = alt.Chart(pd.DataFrame({'y': [avg_success]})).mark_rule(strokeDash=[5, 5], color='grey').encode(y='y:Q')
vertical_line_rr = alt.Chart(pd.DataFrame({'x': [avg_fail]})).mark_rule(strokeDash=[5, 5], color='grey').encode(x='x:Q')

# Scatter plot
risk_reward_chart = alt.Chart(grouped_filtered_stats).mark_circle(size=60).encode(
    x=alt.X('fail:Q', title='Total VAEP rating with unsuccessful actions'),
    y=alt.Y('success:Q', title='Total VAEP rating with successful actions'),
    color=alt.Color('team_name:N', scale=alt.Scale(domain=unique_teams, range=team_color_range)),
    tooltip=[
        'player_name:N',
        'team_name:N',
        alt.Tooltip('success:Q', format='.3f'),
        alt.Tooltip('fail:Q', format='.3f'),
        alt.Tooltip('vaep_rating:Q', format='.3f')
    ],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.1))
).add_selection(selection).interactive()

# Combine plot and lines
final_rr_chart = (risk_reward_chart + horizontal_line_rr + vertical_line_rr).properties(width=800, height=800).configure_axis(
    labelFontSize=15,
    titleFontSize=15
)

st.altair_chart(final_rr_chart, use_container_width=True)

# Footer
st.markdown('---')
st.write('This Webapp was created by Christoph Debowiak - [chrisdebo @GitHub](https://github.com/chrisdebo)')