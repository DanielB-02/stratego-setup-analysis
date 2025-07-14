from collections import Counter


def check_piece_consistency(pieces):
    if len(pieces) != 40:
        raise Exception(f"Amount of pieces is incorrect. It's {len(pieces)} instead of 40.")

    piece_counts = Counter(pieces)

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
