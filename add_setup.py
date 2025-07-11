from datetime import datetime
from grok_api import transcribe_setup


def user_input():
    print("Date played:")
    date_played = datetime.strptime(input(), "%Y/%m/%d")

    print("Opponent name:")
    opponent_name = input()

    print("Result (win/draw/loss):")
    result = input()

    print("Moves:")
    moves = int(input())

    print("Flipped setup (0/1):")
    flipped_setup = int(input())

    print("Noobkiller (0/1):")
    noob_killer = int(input())

    print("Path to setup:")
    path = str(input())

    transcribed_setup = transcribe_setup(path)

    user_input_dict = create_dictionary(date_played, opponent_name, result, moves, flipped_setup, noob_killer, transcribed_setup)

    print(user_input_dict)
    return user_input_dict


def create_dictionary(date_played, opponent_name, result, moves, flipped_setup, noob_killer, transcribed_setup):
    dictionary = {
        "date_played": date_played,
        "opponent_name": opponent_name,
        "result": result,
        "moves": moves,
        "flipped_setup": flipped_setup,
        "noob_killer": noob_killer,
        "setup": transcribed_setup
    }

    return dictionary


user_input()

