import altair as alt
import pandas as pd
import utils.helpers


def create_player_plot(data, attributes, player_name, position, league, season, quality):
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

