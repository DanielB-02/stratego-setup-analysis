from datetime import datetime
# from src.api.grok_api import transcribe_setup
from src.checks.check_for_opponent import check_for_opponent


def user_input():
    print("Date played:")
    date_played = datetime.strptime(input(), "%Y/%m/%d")

    print("Opponent name:")
    opponent_name_input = input()

    opponent_details = check_for_opponent(opponent_name_input)

    opponent_id = opponent_details[0]
    opponent_name = opponent_details[1]

    print("Result (win/draw/loss):")
    result = input()

    print("Moves:")
    moves = int(input())

    print("Noobkiller (0/1):")
    noob_killer = int(input())

    print("Path to setup:")
    path = str(input())

    # transcribed_setup = transcribe_setup(path)

    user_input_dict = create_dictionary(date_played, opponent_id, opponent_name, result, moves, noob_killer)

    return user_input_dict


def create_dictionary(date_played, opponent_id, opponent_name, result, moves, noob_killer):
    dictionary = {
        "date_played": date_played,
        "opponent_id": opponent_id,
        "opponent_name": opponent_name,
        "result": result,
        "moves": moves,
        "noob_killer": noob_killer,
        # "setup": transcribed_setup
    }

    return dictionary

