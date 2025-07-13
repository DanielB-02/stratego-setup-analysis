from sqlite_database import select_opponent_id_and_name


def check_for_opponent(opponent):
    opponent_id_and_name = select_opponent_id_and_name(opponent)
    print(opponent_id_and_name)

    opponent_found_status = False

    if opponent_id_and_name:
        opponent_found_status = True
        # print(opponent_found_status, opponent_id_and_name)
        return opponent_found_status, opponent_id_and_name
    else:
        # print(opponent_found_status)
        return opponent_found_status, ()
