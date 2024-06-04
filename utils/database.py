from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.sql import text


def dataframe_from_sql(league: str, season: str, connection_string: str) -> pd.DataFrame:
    """
    Loads data from a SQL table into a DataFrame.

    Parameters:
    league (str): The league for which data is to be loaded.
    season (str): The season for which data is to be loaded.
    connection_string (str): The connection string to the SQL database.

    Returns:
    DataFrame: A DataFrame containing the loaded data.
    """
    engine = create_engine(connection_string, pool_pre_ping=True)

    # Verbindung zur Datenbank herstellen
    engine = create_engine(connection_string)

    # Table name
    table = f"{league}_{season}_stats_z"

    # Laden der Daten aus der SQL-Tabelle
    try:
        sql_query = f"""
        SELECT {table}.*, teams.team_name
        FROM {table}
        LEFT JOIN teams ON {table}.team_id = teams.team_id
        """
        dataframe = pd.DataFrame(engine.connect().execute(text(sql_query)))
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        dataframe = pd.DataFrame()
    return dataframe


