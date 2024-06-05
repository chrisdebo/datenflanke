# Datenflanke Streamlit

## Über das Projekt

Datenflanke Streamlit ist ein Python-basiertes Projekt, das sich auf die Analyse und Visualisierung von Fußballdaten konzentriert. Es nutzt die Streamlit-Bibliothek, um interaktive Webanwendungen zu erstellen, die es Benutzern ermöglichen, Daten auf intuitive und benutzerfreundliche Weise zu erkunden.
Dieses Repository wird so als DockerContainer auf einem eigenen Server geladen und bereitgestellt (datenflanke.de)

## Hauptfunktionen

- **Spielerbewertung**: Generiert eine Bewertung eines Spielers basierend auf seinen Attributen und Daten. 
- **Spielerplot**: Erstellt einen Plot für einen bestimmten Spieler, der seine Attribute mit anderen Spielern auf der gleichen Position vergleicht.
- **Teamspieleranzeige**: Zeigt alle Spieler eines Teams auf einer bestimmten Position und vergleicht diese Spieler mit dem Rest der Liga.
- **Spieler Suche**: Ermöglicht die Suche nach Spielern basierend auf Liga, Saison, Position und gespielten Minuten zu suchen. Dabei können eigene Kriterien ausgewählt und gewichtet werden.
- **Chatbot Funktion**: Mittels OpenAI Schnittstelle wird mit den selben Daten, aus denen der Plot generiert wird, ein prompt erstellt, dass eine Spielerbewertung auf deutsch und englisch ausgibt.
