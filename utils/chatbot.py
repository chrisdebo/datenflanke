# Import the necessary libraries
from openai import OpenAI
import utils.passwords
import pandas as pd
import streamlit as st
client = OpenAI(api_key=utils.passwords.GPT_KEY)


# Define the function to describe the player's level
def describe_level(z_score: float) -> str:
    """
    Describes a player's performance level based on their z-score.

    Parameters:
    z_score (float): The player's z-score.

    Returns:
    str: A description of the player's performance level.
    """

    if z_score >= 1.5:
        description = "outstanding"
    elif z_score >= 1:
        description = "excellent"
    elif z_score >= 0.5:
        description = "good"
    elif z_score >= -0.5:
        description = "average"
    elif z_score >= -1:
        description = "below average"
    else:
        description = "poor"

    return description


def get_player_evaluation(player_name: str, attributes: list, data: pd.DataFrame) -> str:
    """
    Generates an evaluation of a player based on their attributes and data.

    Parameters:
    player_name (str): The name of the player.
    attributes (list): A list of attributes to be used for evaluating the player.
    data (pd.DataFrame): The DataFrame containing the player data.

    Returns:
    str: A description of the player based on their attributes and data.
    """
    try:
        player_data = data[data['player_name'] == player_name].iloc[0]
        position = player_data['position']
    except IndexError:
        return f"No data found for player {player_name}"

    description = f"Player: {player_name}\n"

    player_description = ""
    for attribute in attributes:
        z_score = player_data.get(attribute, None)
        if z_score is None:
            return f"Attribute {attribute} not found for player {player_name}"
        level = describe_level(z_score)
        player_description += f"When it comes to {attribute}, {player_name} is {level}.\n"

    messages = [
        {"role": "system", "content": f"You are a German-based football scout. \
            You provide succinct and to the point summaries of football players \
            based on data. You talk in footballing terms about data. \
            You use the information given to you from the data and answers \
            to earlier user/assistant pairs to give summaries of players. \
            Your current job is to assess players in the {position} position."},
        {"role": "user", "content": "Do you refer to the game you are an \
         expert in as soccer or football?"},
        {"role": "assistant", "content": "I refer to the game as football. \
         When I say football, I don't mean American football, I mean what \
         Americans call soccer. But I always talk about football, as people \
         do in the United Kingdom and all the other parts of Europe."}]

    start_prompt ="Below is a description of some of the player's skills':\n\n"
    end_prompt = f"\n Use the data provided and summarise the player (using at most four sentences) and speculate on the role the player might take in a team based on these attributes: {', '.join(attributes)}"
    # end_prompt = end_prompt + "\n Your answer should be in german. Take care of using football language in german as well. "
    #end_prompt = "\n Use the data provided to summarise the player in two sentences."
    #end_prompt = "\n Explain how the player's involvement in the match is calculated."
    #end_prompt = "\n Does the player get involved in the game and if not, should we be worried?"

    # Read in the descriptions up to date to be more detailed and get better answers
    try:
        current_df = pd.read_excel('Descriptions.xlsx')

        for number_provided,query in current_df.iterrows():
            previous_description = query['user']
            the_prompt=start_prompt + previous_description + end_prompt
            user={"role": "user", "content": the_prompt}
            messages = messages + [user]
            assistant={"role": "assistant", "content": query['assitant']}
            messages = messages + [assistant]

    except:
        current_df = pd.DataFrame()
        print("No descriptions file")


    #Now ask about current player

    the_prompt=start_prompt + player_description + end_prompt
    user={"role": "user", "content": the_prompt}
    messages = messages + [user]

    # st.text(messages)

    response = client.chat.completions.create(
        model="gpt-4o",  # You can use other models as well
        messages=messages
    )

    return response.choices[0].message.content



def describe_level_german(z_score: float) -> str:
    """
    Describes a player's performance level based on their z-score.

    Parameters:
    z_score (float): The player's z-score.

    Returns:
    str: A description of the player's performance level.
    """

    if z_score >= 1.5:
        description = "überragend"
    elif z_score >= 1:
        description = "ausgezeichnet"
    elif z_score >= 0.5:
        description = "gut"
    elif z_score >= -0.5:
        description = "durchscnitlich"
    elif z_score >= -1:
        description = "unterdurchschnittlich"
    else:
        description = "schlecht"

    return description


def get_player_evaluation_german(player_name: str, attributes: list, data: pd.DataFrame) -> str:
    """
    Generates an evaluation of a player based on their attributes and data.

    Parameters:
    player_name (str): The name of the player.
    attributes (list): A list of attributes to be used for evaluating the player.
    data (pd.DataFrame): The DataFrame containing the player data.

    Returns:
    str: A description of the player based on their attributes and data.
    """
    try:
        player_data = data[data['player_name'] == player_name].iloc[0]
        position = player_data['position']
    except IndexError:
        return f"No data found for player {player_name}"

    description = f"Player: {player_name}\n"

    player_description = ""
    for attribute in attributes:
        z_score = player_data.get(attribute, None)
        if z_score is None:
            return f"Attribute {attribute} not found for player {player_name}"
        level = describe_level_german(z_score)
        player_description += f"Wenn es um die Fähigkeit {attribute} geht, dann ist {player_name} {level}.\n"

    messages = [
        {"role": "system", "content": f"Du bist ein Fußballscout aus Deutschland \
            Du lieferst prägnante und auf den Punkt gebrachte Zusammenfassungen von Fußballspielern \
            basierend auf Daten. Du sprichst und benutzt für den Fußball typische Sprache. \
            Du nutzt die Informationen aus den dir gegebenen Daten und Antworten \
            aus früheren 'user/assistant' Paaren, um Zusammenfassungen über die Spieler zu erstellen. \
            Deine aktuelle Aufgabe besteht darin einen bestimmten Spieler auf der Position {position} zu beschreiben."},
        {"role": "user", "content": "Was meinst du genau mit Fußball?"},
        {"role": "assistant", "content": "Ich meine die Sportart Fußball, welche in Europa und in Deutschland die beliebteste und bekannteste Sportart ist.  \
         "}]

    start_prompt ="Hier findest du eine Beschreibung einiger Fähigkeiten des Spielers:\n\n"
    end_prompt = f"\n Nutze die zur Verfügung stehenden Daten und mache eine Zusammenfassung über den Spieler (nicht mehr als drei Sätze) und spekuliere über die Rolle, welche dieser Spieler in einem Team haben könnte aufgrund dieser Fähigkeiten: {', '.join(attributes)}"
    # end_prompt = end_prompt + "\n Your answer should be in german. Take care of using football language in german as well. "
    #end_prompt = "\n Use the data provided to summarise the player in two sentences."
    #end_prompt = "\n Explain how the player's involvement in the match is calculated."
    #end_prompt = "\n Does the player get involved in the game and if not, should we be worried?"

    # Read in the descriptions up to date to be more detailed and get better answers
    try:
        current_df = pd.read_excel('Descriptions.xlsx')

        for number_provided,query in current_df.iterrows():
            previous_description = query['user']
            the_prompt=start_prompt + previous_description + end_prompt
            user={"role": "user", "content": the_prompt}
            messages = messages + [user]
            assistant={"role": "assistant", "content": query['assitant']}
            messages = messages + [assistant]

    except:
        current_df = pd.DataFrame()
        print("No descriptions file")


    #Now ask about current player

    the_prompt=start_prompt + player_description + end_prompt
    user={"role": "user", "content": the_prompt}
    messages = messages + [user]

    # st.text(messages)

    response = client.chat.completions.create(
        model="gpt-4o",  # You can use other models as well
        messages=messages,
        seed=42,
        temperature=0.5
    )

    return response.choices[0].message.content


