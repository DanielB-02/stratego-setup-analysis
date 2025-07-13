from add_setup import user_input
from datetime import datetime
import sqlite3
from sqlite_database import get_highest_setup_id_from_game_setups

conn = sqlite3.connect('sqlite_database.db')
c = conn.cursor()


# setup_details = {
#     'date_played': datetime(2025, 4, 24, 0, 0),
#     'opponent_id': 10,
#     'opponent_name': 'Sekertzis1973',
#     'result': 'win',
#     'moves': 777,
#     'noob_killer': 1,
#     'setup': {
#         '1': ['6', '2', '8', '6', '4', '2', '5', '2', '2', '5'],
#         '2': ['3', '5', '2', '9', '7', '5', '2', 'B', '4', '8'],
#         '3': ['B', '2', '7', '1', '6', '2', '7', '10', '6', '3'],
#         '4': ['B', '4', 'B', '3', 'B', '3', 'B', '4', '3', 'F']
#     }
# }


def setup_to_sql(setup_details):
    print(setup_details)
    highest_setup_id = get_highest_setup_id_from_game_setups()
    json_setup = setup_details["setup"]
    game_setup_to_sql(json_setup, highest_setup_id)

    game_record_to_sql(setup_details, highest_setup_id)


def game_setup_to_sql(json_setup, highest_setup_id):
    for row, values in json_setup.items():
        # print(f"{row} + {values}")
        for index, value in enumerate(values):
            # print(f"(1, {row}, {index+1}, {str(value)}),")
            c.execute(
                "INSERT INTO GameSetups (setup_id, row, col, piece) VALUES (?, ?, ?, ?)",
                (highest_setup_id + 1, int(row), index + 1, str(value))
            )
    conn.commit()


def game_record_to_sql(setup_details, highest_setup_id):
    c.execute(
        "INSERT INTO GameRecords (setup_id, date_played, opponent_id, opponent_name, result, moves, noob_killer) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (highest_setup_id + 1,
         setup_details["date_played"],
         setup_details["opponent_id"],
         setup_details["opponent_name"],
         setup_details["result"],
         setup_details["moves"],
         setup_details["noob_killer"]
         )
    )
    conn.commit()


# c.execute("""INSERT INTO GameSetups (setup_id, row, col, piece) VALUES
# (1, 1, 1, '6'), (1, 1, 2, '2'), (1, 1, 3, '8'), (1, 1, 4, '2'), (1, 1, 5, '2'), (1, 1, 6, '4'), (1, 1, 7, '7'), (1, 1, 8, '5'), (1, 1, 9, '6'), (1, 1, 10, '2'),
# (1, 2, 1, '8'), (1, 2, 2, '3'), (1, 2, 3, '4'), (1, 2, 4, '5'), (1, 2, 5, '6'), (1, 2, 6, '2'), (1, 2, 7, '3'), (1, 2, 8, '9'), (1, 2, 9, '4'), (1, 2, 10, '7'),
# (1, 3, 1, '6'), (1, 3, 2, '2'), (1, 3, 3, '5'), (1, 3, 4, 'B'), (1, 3, 5, '10'), (1, 3, 6, '4'), (1, 3, 7, '8'), (1, 3, 8, '1'), (1, 3, 9, '2'), (1, 3, 10, 'B'),
# (1, 4, 1, 'B'), (1, 4, 2, '3'), (1, 4, 3, 'B'), (1, 4, 4, 'F'), (1, 4, 5, 'B'), (1, 4, 6, 'B'), (1, 4, 7, '3'), (1, 4, 8, '7'), (1, 4, 9, '2'), (1, 4, 10, '3')""")

setup_details = user_input()
# json_setup = setup_details["setup"]
setup_to_sql(setup_details)

conn.close()
