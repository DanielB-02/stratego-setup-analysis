from src.database.sqlite_database import get_pieces_at_position, get_pieces_at_position_for_opponent
from collections import Counter

print("Give the row number:")
row_number = int(input())

print("Give the column number:")
column_number = int(input())

piece_positions = get_pieces_at_position(row_number, column_number)
print(piece_positions)

piece_positions_for_opponent = get_pieces_at_position_for_opponent("Sekertzis1973", 1, 1)
print("Piece positions for opponent:", piece_positions_for_opponent)

total_positions = len(piece_positions)


if total_positions > 0:
    # Directly extract pieces using a generator expression
    list_of_pieces = (tup[0] for tup in piece_positions)

    # Use Counter for efficient counting of pieces
    piece_counts = Counter(list_of_pieces)

    # Calculate and print percentages
    for piece, count in piece_counts.items():
        percentage = (count / total_positions) * 100
        print(f"Percentage of '{piece}': {percentage:.2f}%")
else:
    print("No positions available to calculate percentage")

