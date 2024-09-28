import altair as alt
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Arc
import matplotsoccer

import utils.helpers


def create_player_plot(data: pd.DataFrame, attributes: list[str], player_name: str, position: str, league: str, season: str, quality: str) -> alt.Chart:
    """
    Creates a plot for a specific player, comparing their attributes to other players in the same position.

    Parameters:
    data (pd.DataFrame): The dataset containing player information.
    attributes (List[str]): A list of attributes to be used for evaluating the player.
    player_name (str): The name of the player.
    position (str): The position of the player.
    league (str): The league in which the player plays.
    season (str): The season for which the data is being analyzed.
    quality (str): The quality metric used for player evaluation.

    Returns:
    alt.Chart: An Altair chart object representing the player plot.
    """
    x_labels = utils.helpers.create_x_labels()
    y_labels = utils.helpers.create_y_labels()

    # Daten für den ausgewählten Spieler filtern
    player_data = data[(data['player_name'] == player_name) & (data['position'] == position)]

    # Daten für alle Spieler auf der gleichen Position filtern
    position_data = data[data['position'] == position]

    # Erstelle einen DataFrame für das Plotten
    plot_data_list = []
    for idx, attribute in enumerate(attributes):
        temp_data = pd.DataFrame({
            'Player': position_data['player_name'],
            'Value': position_data[attribute].values.flatten(),  # Sicherstellen, dass die Daten 1-dimensional sind
            'Attribute': attribute,
            'Y': y_labels[attribute]  # Y-Wert als benutzerdefiniertes Label zuweisen
        })
        temp_data['Rank'] = temp_data['Value'].rank(ascending=False, method='min')
        temp_data['Total'] = len(temp_data)
        temp_data['Rank_Display'] = temp_data.apply(lambda row: f"{int(row['Rank'])}/{int(row['Total'])}", axis=1)
        plot_data_list.append(temp_data)
    plot_data = pd.concat(plot_data_list)

    # Erstelle den Altair-Plot
    base = alt.Chart(plot_data).mark_circle(size=60, opacity=0.5).encode(
        x=alt.X('Value:Q', scale=alt.Scale(domain=(-3, 4)),
                axis=alt.Axis(title=f"{player_name} im Vergleich zu Spielern mit der Position {position} - {quality}",
                              titleY=75, titleAlign='center', values=list(x_labels.keys()),
                              labelExpr="datum.value == -1.5 ? 'schlecht' : datum.value == -0.75 ? 'unterdurchschnittlich' : datum.value == 0 ? 'durchschnittlich' : datum.value == 0.75 ? 'gut' : datum.value == 1.25 ? 'sehr gut' : datum.value == 1.75 ? 'überragend' : ''")),
        y=alt.Y('Y:N', axis=alt.Axis(
            title=f'{player_data["player_name"].values[0]} - {player_data["team_name"].values[0]} in {player_data["minutes_played"].values[0]} gespielten Minuten. {league} - Saison {season} ',
            titleAngle=0, titleX=100, titleY=-50, labelAngle=0, labelAlign='right', labelLimit=175)),
        # Y-Achse mit Attributnamen und Beschriftung
        tooltip=['Player', 'Rank_Display']
    ).properties(
        width=700,
        height=85 * len(attributes)
    )

    # Hervorhebung des ausgewählten Spielers
    highlight_data_list = []
    for idx, attribute in enumerate(attributes):
        temp_data = pd.DataFrame({
            'Player': [player_name],
            'Value': [player_data[attribute].values.flatten()[0]],
            'Attribute': [attribute],
            'Y': [y_labels[attribute]]
        })
        temp_data['Rank'] = \
            plot_data[(plot_data['Attribute'] == attribute) & (plot_data['Player'] == player_name)]['Rank'].values[0]
        temp_data['Total'] = \
            plot_data[(plot_data['Attribute'] == attribute) & (plot_data['Player'] == player_name)]['Total'].values[0]
        temp_data['Rank_Display'] = f"{int(temp_data['Rank'][0])}/{int(temp_data['Total'][0])}"
        highlight_data_list.append(temp_data)
    highlight_data = pd.concat(highlight_data_list)

    highlight = alt.Chart(highlight_data).mark_circle(size=200, color='red').encode(
        x='Value:Q',
        y=alt.Y('Y:N', axis=alt.Axis(labels=True)),
        tooltip=['Player', 'Rank_Display']
    )

    # Kombiniere den Basis-Chart und Highlight-Chart
    chart = alt.layer(base, highlight).properties(
        #background='#f0f0f0'  # Hintergrundfarbe setzen
    ).resolve_scale(
        color='independent'
    )

    return chart


def create_top10_plot(data):
    # Filter data to get the top 10 players based on the quality
    top10_data = data.nlargest(10, 'quality')

    # Determine the minimum and maximum value for the x-axis
    min_minutes_played = max(0, top10_data['minutes_played'].min() - 150)
    max_minutes_played = top10_data['minutes_played'].max() + 50

    # Determine the minimum and maximum value for the y-axis
    min_y = top10_data['quality'].min() - 0.25
    max_y = top10_data['quality'].max() + 0.25

    # Create the scatter plot
    base = alt.Chart(top10_data).mark_circle(size=200).encode(
        x=alt.X('minutes_played:Q', scale=alt.Scale(domain=(min_minutes_played, max_minutes_played)),
                title='Gespielte Minuten'),
        y=alt.Y('quality:Q', scale=alt.Scale(domain=(min_y, max_y)),
                title='Score'),
        color=alt.Color('quality:Q', scale=alt.Scale(scheme='goldgreen'), title='Spieler Qualität'),
        #size=alt.value(100),  # Increase the size of the points
        tooltip=['player_name', 'minutes_played', 'quality', 'team_name']
    ).properties(
        title='Top 10 Spieler',
        width=800,
        height=400
    )

    # Add text labels
    text = base.mark_text(
        align='right',
        baseline='middle',
        dx=10,
        dy=10, # Adjust the position of the text relative to the points
        fontSize=12,
        angle=20# Adjust the font size
    ).encode(
        text='player_name'
    )

    # Combine the scatter plot and text labels
    chart = base + text

    return chart

def create_teams_plot(data, attributes, team, position, selected_league_display, selected_season_display, selected_quality_display):
    x_labels = utils.helpers.create_x_labels()
    y_labels = utils.helpers.create_y_labels()

    # Daten für alle Spieler auf der gleichen Position filtern
    position_data = data[data['position'] == position]

    # Daten für alle Spieler im ausgewählten Team filtern
    team_data = data[(data['team_name'] == team) & (data['position'] == position)]

    if position_data.empty or team_data.empty:
        return alt.Chart(pd.DataFrame({'x': [], 'y': []})).mark_point()

    # Erstelle einen DataFrame für das Plotten
    plot_data_list = []
    for idx, attribute in enumerate(attributes):
        temp_data = pd.DataFrame({
            'Player': position_data['player_name'],
            'Value': position_data[attribute].values.flatten(),  # Sicherstellen, dass die Daten 1-dimensional sind
            'Attribute': attribute,
            'Y': y_labels[attribute]  # Y-Wert als benutzerdefiniertes Label zuweisen
        })
        temp_data['Rank'] = temp_data['Value'].rank(ascending=False, method='min')
        temp_data['Total'] = len(temp_data)

        if not temp_data.empty:
            temp_data['Rank_Display'] = temp_data.apply(lambda row: f"{int(row['Rank'])}/{int(row['Total'])}", axis=1)

        plot_data_list.append(temp_data)
    plot_data = pd.concat(plot_data_list)

    # Erstelle den Altair-Plot
    base = alt.Chart(plot_data).mark_circle(size=60, opacity=0.5).encode(
        x=alt.X('Value:Q', scale=alt.Scale(domain=(-3, 4)),
                axis=alt.Axis(title=f"Spieler im Vergleich zu Spielern mit der Position {position} - {selected_quality_display}",
                              titleY=75, titleAlign='center', values=list(x_labels.keys()),
                              labelExpr="datum.value == -1.5 ? 'schlecht' : datum.value == -0.75 ? 'unterdurchschnittlich' : datum.value == 0 ? 'durchschnittlich' : datum.value == 0.75 ? 'gut' : datum.value == 1.25 ? 'sehr gut' : datum.value == 1.75 ? 'überragend' : ''")),
        y=alt.Y('Y:N', axis=alt.Axis(
            title=f'{team} - {selected_season_display}',
            titleAngle=0, titleX=100, titleY=-50, labelAngle=0, labelAlign='right', labelLimit=175)),
        # Y-Achse mit Attributnamen und Beschriftung
        tooltip=['Player', 'Rank_Display']
    ).properties(
        width=700,
        height=85 * len(attributes)
    )

    # Hervorhebung der Spieler im ausgewählten Team
    highlight_data_list = []
    for idx, attribute in enumerate(attributes):
        for player in team_data['player_name']:
            temp_data = pd.DataFrame({
                'Player': [player],
                'Value': [team_data[team_data['player_name'] == player][attribute].values.flatten()[0]],
                'Attribute': [attribute],
                'Y': [y_labels[attribute]]
            })
            temp_data['Rank'] = plot_data[(plot_data['Attribute'] == attribute) & (plot_data['Player'] == player)]['Rank'].values[0]
            temp_data['Total'] = plot_data[(plot_data['Attribute'] == attribute) & (plot_data['Player'] == player)]['Total'].values[0]
            temp_data['Rank_Display'] = f"{int(temp_data['Rank'][0])}/{int(temp_data['Total'][0])}"
            highlight_data_list.append(temp_data)
    highlight_data = pd.concat(highlight_data_list)

    highlight = alt.Chart(highlight_data).mark_circle(size=200, color='red').encode(
        x='Value:Q',
        y=alt.Y('Y:N', axis=alt.Axis(labels=True)),
        tooltip=['Player', 'Rank_Display']
    )

    # Kombiniere den Basis-Chart und Highlight-Chart
    chart = alt.layer(base, highlight).properties(
        #background='#f0f0f0'  # Hintergrundfarbe setzen
    ).resolve_scale(
        color='independent'
    )

    return chart

def plot_actions_around(selected_action, all_actions, games, num_actions_before, num_actions_after):
    # Bestimmen des Indexes der ausgewählten Aktion
    action_index = selected_action.name

    # Bestimmen der Indexgrenzen
    start_index = max(action_index - num_actions_before, 0)
    end_index = min(action_index + num_actions_after + 1, len(all_actions))

    # Extrahieren der relevanten Aktionen
    actions_to_plot = all_actions.iloc[start_index:end_index].copy()
    print("Aktionen zum Plotten:", actions_to_plot)

    # Zusätzliche Informationen hinzufügen
    def nice_time(row):
        minute = int((row.period_id - 1) * 45 + row.time_seconds // 60)
        second = int(row.time_seconds % 60)
        return f"{minute}m{second}s"

    actions_to_plot["nice_time"] = actions_to_plot.apply(nice_time, axis=1)
    labels = actions_to_plot[["nice_time", "actiontype_name", "player_name", "team_name", "vaep_value"]]

    # Spielinformationen für die ausgewählte Aktion holen
    game_id = selected_action.game_id
    g = games[games.game_id == game_id].iloc[0]
    minute = int((selected_action.period_id - 1) * 45 + selected_action.time_seconds // 60)
    game_info = f"{g.game_date} {g.home_team} {g.home_score}-{g.away_score} {g.away_team} {minute + 1}'"
    print(game_info)

    # Erstellen Sie das Figure- und Axes-Objekt
    fig, ax = plt.subplots(figsize=(6, 4))

    # Aktionen plotten
    matplotsoccer.actions(
        location=actions_to_plot[["start_x", "start_y", "end_x", "end_y"]],
        action_type=actions_to_plot.actiontype_name,
        team=actions_to_plot.team_name,
        result=actions_to_plot.result_name == "success",
        label=labels,
        labeltitle=["time", "actiontype", "player", "team", "vaep_value"],
        ax=ax,  # Verwenden Sie das erstellte Axes-Objekt
        zoom=False
    )

    # Zeigen Sie den Plot in Streamlit an
    st.pyplot(fig)
    return ax

def create_pitch():
    # Spielfeldmaße in Metern
    pitch_length = 105
    pitch_width = 68

    # Außenlinien
    outer_lines_df = pd.DataFrame({
        'x': [0, pitch_length, pitch_length, 0, 0],
        'y': [0, 0, pitch_width, pitch_width, 0],
        'order': [1, 2, 3, 4, 5]
    })

    outer_lines = alt.Chart(outer_lines_df).mark_line(color='black', strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        order='order'
    )

    # Mittellinie
    mid_line_df = pd.DataFrame({
        'x': [pitch_length / 2, pitch_length / 2],
        'y': [0, pitch_width],
        'order': [1, 2]
    })

    mid_line = alt.Chart(mid_line_df).mark_line(color='black', strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        order='order'
    )

    # Mittelkreis
    center_circle = alt.Chart(pd.DataFrame({
        'x': [pitch_length / 2],
        'y': [pitch_width / 2]
    })).mark_circle(color='black', fill=None, strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        size=alt.value(400)
    )

    # Strafraum links
    left_penalty_area_df = pd.DataFrame({
        'x': [16.5, 16.5, 0, 0, 16.5],
        'y': [pitch_width - 16.5, 16.5, 16.5, pitch_width - 16.5, pitch_width - 16.5],
        'order': [1, 2, 3, 4, 5]
    })

    left_penalty_area = alt.Chart(left_penalty_area_df).mark_line(color='black', strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        order='order'
    )

    # Strafraum rechts
    right_penalty_area_df = pd.DataFrame({
        'x': [pitch_length - 16.5, pitch_length - 16.5, pitch_length, pitch_length, pitch_length - 16.5],
        'y': [pitch_width - 16.5, 16.5, 16.5, pitch_width - 16.5, pitch_width - 16.5],
        'order': [1, 2, 3, 4, 5]
    })

    right_penalty_area = alt.Chart(right_penalty_area_df).mark_line(color='black', strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        order='order'
    )

    # Torraum links
    left_six_yard_box_df = pd.DataFrame({
        'x': [5.5, 5.5, 0, 0, 5.5],
        'y': [
            (pitch_width / 2) + 9.16,
            (pitch_width / 2) - 9.16,
            (pitch_width / 2) - 9.16,
            (pitch_width / 2) + 9.16,
            (pitch_width / 2) + 9.16
        ],
        'order': [1, 2, 3, 4, 5]
    })

    left_six_yard_box = alt.Chart(left_six_yard_box_df).mark_line(color='black', strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        order='order'
    )

    # Torraum rechts
    right_six_yard_box_df = pd.DataFrame({
        'x': [pitch_length - 5.5, pitch_length - 5.5, pitch_length, pitch_length, pitch_length - 5.5],
        'y': [
            (pitch_width / 2) + 9.16,
            (pitch_width / 2) - 9.16,
            (pitch_width / 2) - 9.16,
            (pitch_width / 2) + 9.16,
            (pitch_width / 2) + 9.16
        ],
        'order': [1, 2, 3, 4, 5]
    })

    right_six_yard_box = alt.Chart(right_six_yard_box_df).mark_line(color='black', strokeWidth=2).encode(
        x='x:Q',
        y='y:Q',
        order='order'
    )

    # Elfmeterpunkte
    left_penalty_spot = alt.Chart(pd.DataFrame({
        'x': [11],
        'y': [pitch_width / 2]
    })).mark_point(color='black', size=50).encode(
        x='x:Q',
        y='y:Q'
    )

    right_penalty_spot = alt.Chart(pd.DataFrame({
        'x': [pitch_length - 11],
        'y': [pitch_width / 2]
    })).mark_point(color='black', size=50).encode(
        x='x:Q',
        y='y:Q'
    )

    center_spot = alt.Chart(pd.DataFrame({
        'x': [pitch_length / 2],
        'y': [pitch_width / 2]
    })).mark_point(color='black', size=25000).encode(
        x='x:Q',
        y='y:Q'
    )

    # Strafraumhalbkreis links
    left_penalty_arc = alt.Chart().mark_arc(color='black', strokeWidth=2).encode(
        x=alt.value(11),
        y=alt.value(pitch_width / 2),
        theta=alt.value(-0.589),  # -33.75 Grad in Radiant
        theta2=alt.value(0.589),  # 33.75 Grad in Radiant
        radius=alt.value(9.15)
    )

    # Strafraumhalbkreis rechts
    right_penalty_arc = alt.Chart().mark_arc(color='black', strokeWidth=2).encode(
        x=alt.value(pitch_length - 11),
        y=alt.value(pitch_width / 2),
        theta=alt.value(2.553),  # 146.25 Grad in Radiant
        theta2=alt.value(3.730),  # 213.75 Grad in Radiant
        radius=alt.value(9.15)
    )

    # Zusammensetzen der Spielfeldteile
    pitch_elements = alt.layer(
        outer_lines,
        mid_line,
        center_spot,
        left_penalty_area,
        right_penalty_area,
        left_six_yard_box,
        right_six_yard_box,
        left_penalty_spot,
        right_penalty_spot,
        left_penalty_arc,
        right_penalty_arc
    ).properties(
        width=700,
        height=450
    )

    return pitch_elements

def createPitch(ax=None):
    # Wenn keine Achse übergeben wurde, erstellen wir eine neue
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))

    # Spielfeldmaße
    pitch_length = 105  # Länge in Metern
    pitch_width = 68    # Breite in Metern

    # Spielfeldlinien zeichnen
    # Außenlinien und Mittellinie
    ax.plot([0, 0], [0, pitch_width], color="black")  # Linke Seitenlinie
    ax.plot([0, pitch_length], [pitch_width, pitch_width], color="black")  # Obere Torlinie
    ax.plot([pitch_length, pitch_length], [pitch_width, 0], color="black")  # Rechte Seitenlinie
    ax.plot([pitch_length, 0], [0, 0], color="black")  # Untere Torlinie
    ax.plot([pitch_length/2, pitch_length/2], [0, pitch_width], color="black")  # Mittellinie

    # Strafräume
    # Linker Strafraum
    left_penalty_area = {'min_x': 0, 'max_x': 16.5, 'min_y': 13.84, 'max_y': 54.16}
    # Vertikale Linie
    ax.plot([left_penalty_area['max_x'], left_penalty_area['max_x']], [left_penalty_area['min_y'], left_penalty_area['max_y']], color="black")
    # Obere horizontale Linie
    ax.plot([left_penalty_area['min_x'], left_penalty_area['max_x']], [left_penalty_area['max_y'], left_penalty_area['max_y']], color="black")
    # Untere horizontale Linie
    ax.plot([left_penalty_area['max_x'], left_penalty_area['min_x']], [left_penalty_area['min_y'], left_penalty_area['min_y']], color="black")

    # Rechter Strafraum
    right_penalty_area = {'min_x': 88.5, 'max_x': 105, 'min_y': 13.84, 'max_y': 54.16}
    # Vertikale Linie
    ax.plot([right_penalty_area['min_x'], right_penalty_area['min_x']], [right_penalty_area['min_y'], right_penalty_area['max_y']], color="black")
    # Obere horizontale Linie
    ax.plot([right_penalty_area['min_x'], right_penalty_area['max_x']], [right_penalty_area['max_y'], right_penalty_area['max_y']], color="black")
    # Untere horizontale Linie
    ax.plot([right_penalty_area['max_x'], right_penalty_area['min_x']], [right_penalty_area['min_y'], right_penalty_area['min_y']], color="black")

    # Torraum (6-Meter-Raum)
    # Linker Torraum
    left_six_yard_box = {'min_x': 0, 'max_x': 5.5, 'min_y': (pitch_width/2) - 9.16/2, 'max_y': (pitch_width/2) + 9.16/2}
    # Vertikale Linie
    ax.plot([left_six_yard_box['max_x'], left_six_yard_box['max_x']], [left_six_yard_box['min_y'], left_six_yard_box['max_y']], color="black")
    # Obere horizontale Linie
    ax.plot([left_six_yard_box['min_x'], left_six_yard_box['max_x']], [left_six_yard_box['max_y'], left_six_yard_box['max_y']], color="black")
    # Untere horizontale Linie
    ax.plot([left_six_yard_box['max_x'], left_six_yard_box['min_x']], [left_six_yard_box['min_y'], left_six_yard_box['min_y']], color="black")

    # Rechter Torraum
    right_six_yard_box = {'min_x': pitch_length - 5.5, 'max_x': pitch_length, 'min_y': (pitch_width/2) - 9.16/2, 'max_y': (pitch_width/2) + 9.16/2}
    # Vertikale Linie
    ax.plot([right_six_yard_box['min_x'], right_six_yard_box['min_x']], [right_six_yard_box['min_y'], right_six_yard_box['max_y']], color="black")
    # Obere horizontale Linie
    ax.plot([right_six_yard_box['min_x'], right_six_yard_box['max_x']], [right_six_yard_box['max_y'], right_six_yard_box['max_y']], color="black")
    # Untere horizontale Linie
    ax.plot([right_six_yard_box['max_x'], right_six_yard_box['min_x']], [right_six_yard_box['min_y'], right_six_yard_box['min_y']], color="black")

    # Mittelkreis und Anstoßpunkte
    centre_circle = plt.Circle((pitch_length/2, pitch_width/2), 9.15, color="black", fill=False)
    centre_spot = plt.Circle((pitch_length/2, pitch_width/2), 0.4, color="black")
    left_penalty_spot = plt.Circle((11, pitch_width/2), 0.4, color="black")
    right_penalty_spot = plt.Circle((pitch_length - 11, pitch_width/2), 0.4, color="black")

    # Kreise hinzufügen
    ax.add_patch(centre_circle)
    ax.add_patch(centre_spot)
    ax.add_patch(left_penalty_spot)
    ax.add_patch(right_penalty_spot)

    # Strafraumhalbkreise
    left_arc = Arc((11, pitch_width/2), height=18.3, width=18.3, angle=0,
                   theta1=310, theta2=50, color="black")
    right_arc = Arc((pitch_length - 11, pitch_width/2), height=18.3, width=18.3, angle=0,
                    theta1=130, theta2=230, color="black")

    # Bögen hinzufügen
    ax.add_patch(left_arc)
    ax.add_patch(right_arc)

    # Achsenbegrenzungen und Aussehen einstellen
    ax.set_xlim(-5, pitch_length + 5)
    ax.set_ylim(-5, pitch_width + 5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Achse zurückgeben
    return ax

