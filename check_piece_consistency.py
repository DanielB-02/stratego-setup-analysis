from collections import Counter

from sqlite_database import select_pieces_from_staging_setup

pieces = select_pieces_from_staging_setup(1)

# pieces = ['6', '2', '8', '6', '4', '2', '5', '2', '2', '5', '3', '5', '2', '9', '7', '5', '2', 'B', '4', '8', 'B', '2', '7', '1', '6', '2', '7', '10', '6', '3', 'B', '4', 'B', '3', 'B', '3', 'B', '4', '3', 'F']


def check_piece_cosistency(pieces):
    if len(pieces) != 40:
        raise Exception(f"Amount of pieces is incorrect. It's {len(pieces)} instead of 40.")

    piece_counts = Counter(pieces)
    # print(piece_counts)

    for piece, amount in piece_counts.items():
        if piece in correct_piece_configuration:
            if amount != correct_piece_configuration[piece]:
                raise Exception(
                    f"Incorrect count for piece {piece}. Found {amount}, expected {correct_piece_configuration[piece]}.")
        else:
            raise Exception(f"Invalid piece type: {piece}")


correct_piece_configuration = {
    '1': 1,
    '2': 8,
    '3': 5,
    '4': 4,
    '5': 4,
    '6': 4,
    '7': 3,
    '8': 2,
    '9': 1,
    '10': 1,
    'B': 6,
    'F': 1
}

# check_piece_cosistency(pieces)
