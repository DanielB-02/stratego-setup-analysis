from datetime import datetime
from grok_api import transcribe_setup
from check_for_opponent import check_for_opponent


def user_input():
    print("Date played:")
    date_played = datetime.strptime(input(), "%Y/%m/%d")

    print("Opponent name:")
    opponent_name_input = input()

    opponent_tuple = check_for_opponent(opponent_name_input)
    opponent_found_status = opponent_tuple[0]
    opponent_details = opponent_tuple[1]

    if opponent_found_status:
        opponent_id = opponent_details[0]
        opponent_name = opponent_details[1]
    else:
        raise Exception("Username not found.")

    print(f"opponent_found_status: {opponent_found_status}")
    print(f"opponent_details: {opponent_details}")
    print(f"opponent_id: {opponent_id}")
    print(f"opponent_name: {opponent_name}")

    print("Result (win/draw/loss):")
    result = input()

    print("Moves:")
    moves = int(input())

    print("Noobkiller (0/1):")
    noob_killer = int(input())

    print("Path to setup:")
    path = str(input())

    transcribed_setup = transcribe_setup(path)

    user_input_dict = create_dictionary(date_played, opponent_id, opponent_name, result, moves, noob_killer, transcribed_setup)

    return user_input_dict


def create_dictionary(date_played, opponent_id, opponent_name, result, moves, noob_killer, transcribed_setup):
    dictionary = {
        "date_played": date_played,
        "opponent_id": opponent_id,
        "opponent_name": opponent_name,
        "result": result,
        "moves": moves,
        "noob_killer": noob_killer,
        "setup": transcribed_setup
    }

    return dictionary

