import streamlit as st
from utils.helpers import preload_data

# Setup the layout
# st.set_page_config(layout="wide")

# Header with logo and app name placeholder
st.sidebar.image('images/logo.jpg', use_column_width=True)
st.sidebar.header('', divider=True)

# Main content area
st.header('Willkommen auf datenflanke.de – Präzise Vorlagen für erfolgreiche Abschlüsse ⚽', divider=True)
st.markdown('''    
    #### 🔎 Tiefe Einblicke in die Spielerleistung
    Hier kannst Du die Bewertungen einzelner Spieler einsehen und ihre Leistungen in verschiedenen Wettbewerben und Saisons analysieren. Mithilfe eines fortschrittlichen Machine-Learning-Algorithmus, basierend auf Daten aus über 4000 Spielen, wurden mehr als 12 Millionen Aktionen bewertet. Aus diesen Berechnungen geht hervor, wie stark jede Aktion die Chance auf ein Tor oder ein Gegentor beeinflusst. Wo herkömmliche erweiterte Statistiken meist nur Torschüsse (expected Goals Modelle) miteinbeziehen, berücksichtigt unser Modell auch die Qualität jeder Aktion im Spiel (Pass, Dribbling, Einwurf ...), sowie die Position des Spielers und viele weitere Faktoren.

    #### 🥇 Präzise und Objektive Spielerbewertungen
    Wir kombinieren diese Daten mit über 40 weiteren Statistiken, um umfassende Spielerqualitäten zu ermitteln, die zuvor sorgfältig aus einem Team professioneller Scouts ermittelt wurden. Die Ergebnisse werden durch statistische Verfahren vergleichbar gemacht, sodass schnell sichtbar wird, wie Spieler relativ zu anderen abschneiden.
    
    #### 📊 Anpassbare Analysen
    Über die Spielersuche kannst Du spezifische Spielerqualitäten auswählen und gewichten, um die besten Spieler nach deinen Kriterien zu finden.
    
    #### 👨🏼‍🤝‍👨🏽 Wie schneiden die Spieler aus einem bestimmten Team ab?
    In der Teamanalyse kannst du alle Spieler eines Teams im Vergleich zum Rest der Liga analysieren.
''')
st.info("Klicke auf **Spielerbewertung**, **Spielersuche** oder **Teamanalyse** im Menü auf der linken Seite um loszulegen.")

# Footer
st.markdown('---')  # This creates a horizontal line
st.write('This Webapp was created by Christoph Debowiak - [chrisdebo @GitHub](https://github.com/chrisdebo)')

preload_data()