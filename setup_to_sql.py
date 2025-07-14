from add_setup import user_input
from datetime import datetime
import sqlite3
from sqlite_database import determine_new_setup_id_from_game_setups, select_everything_from_staging_setup, select_pieces_from_staging_setup, check_duplicate_setup, delete_from_temp_setup
from staging_consistency_checks import check_piece_consistency


conn = sqlite3.connect('sqlite_database.db')
c = conn.cursor()


setup_details = {
    'date_played': datetime(2025, 4, 24, 0, 0),
    'opponent_id': 10,
    'opponent_name': 'Sekertzis1973',
    'result': 'win',
    'moves': 777,
    'noob_killer': 1,
    'setup': {
        '1': ['6', '2', '6', '8', '4', '2', '5', '2', '2', '5'],
        '2': ['3', '5', '2', '9', '7', '5', '2', 'B', '4', '8'],
        '3': ['B', '2', '7', '1', '6', '2', '7', '10', '6', '3'],
        '4': ['B', '4', 'B', '3', 'B', '3', 'B', '4', '3', 'F']
    }
}

TEMP_SETUP_ID = 1


def setup_to_sql(setup_details):
    # print(setup_details)
    new_setup_id = determine_new_setup_id_from_game_setups()
    json_setup = setup_details["setup"]

    game_setup_to_sql_staging(json_setup, TEMP_SETUP_ID)

    check_consistency(TEMP_SETUP_ID)

    duplicate_setup_id = check_duplicate_setup()

    if duplicate_setup_id is None:
        game_setup_to_sql_real(json_setup, new_setup_id)
        game_record_to_sql(setup_details, new_setup_id)
    else:
        game_record_to_sql(setup_details, duplicate_setup_id)

    delete_from_temp_setup()


def game_setup_to_sql_staging(json_setup, new_setup_id):
    for row, values in json_setup.items():
        for index, value in enumerate(values):
            c.execute(
                "INSERT INTO TempSetup (setup_id, row, col, piece) VALUES (?, ?, ?, ?)",
                (TEMP_SETUP_ID, int(row), index + 1, str(value))
            )
    conn.commit()


def game_setup_to_sql_real(json_setup, new_setup_id):
    for row, values in json_setup.items():
        for index, value in enumerate(values):
            c.execute(
                "INSERT INTO GameSetups (setup_id, row, col, piece) VALUES (?, ?, ?, ?)",
                (new_setup_id, int(row), index + 1, str(value))
            )
    conn.commit()


def check_consistency(new_setup_id):
    pieces = select_pieces_from_staging_setup(new_setup_id)
    check_piece_consistency(pieces)


def game_record_to_sql(setup_details, new_setup_id):
    c.execute(
        "INSERT INTO GameRecords (setup_id, date_played, opponent_id, opponent_name, result, moves, noob_killer) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (new_setup_id,
         setup_details["date_played"],
         setup_details["opponent_id"],
         setup_details["opponent_name"],
         setup_details["result"],
         setup_details["moves"],
         setup_details["noob_killer"]
         )
    )
    conn.commit()


# setup_details = user_input()
# json_setup = setup_details["setup"]
setup_to_sql(setup_details)

conn.close()
