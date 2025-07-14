from src.database.sqlite_database import select_opponent_id_and_name


def check_for_opponent(opponent):
    opponent_id_and_name = select_opponent_id_and_name(opponent)

    if opponent_id_and_name:
        return opponent_id_and_name
    else:
        raise Exception("Username not found.")

