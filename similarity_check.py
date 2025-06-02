from sqlite_database import get_all_setup_positions


setup_positions = get_all_setup_positions()
newly_added_setup = {(1, 1): '4', (1, 2): 'B', (1, 3): '4', (1, 4): '10', (1, 5): '4', (1, 6): '6', (1, 7): '2', (1, 8): '8', (1, 9): '5', (1, 10): '3', (2, 1): '6', (2, 2): '2', (2, 3): '7', (2, 4): '2', (2, 5): '7', (2, 6): '2', (2, 7): '2', (2, 8): '1', (2, 9): '9', (2, 10): '6', (3, 1): '8', (3, 2): '2', (3, 3): '5', (3, 4): 'B', (3, 5): '3', (3, 6): 'B', (3, 7): '4', (3, 8): '7', (3, 9): '2', (3, 10): '2', (4, 1): '3', (4, 2): '3', (4, 3): 'B', (4, 4): 'F', (4, 5): 'B', (4, 6): 'B', (4, 7): '5', (4, 8): '5', (4, 9): '3', (4, 10): '6'}


def loop_setups(positions, new_setup):
    if not positions:
        return

    previous_id = positions[0][1]
    current_setup = []

    for position in positions:
        current_id = position[1]

        if current_id != previous_id:
            serialized_setup = serialize_setup(current_setup)
            check_for_90_percent_similarity(serialized_setup, new_setup)

            # print(f"Serialized setup with ID: {previous_id}")
            # print(serialized_setup)
            current_setup = []

        current_setup.append(position)
        previous_id = current_id

    # Serialize the last group
    if current_setup:
        serialized_setup = serialize_setup(current_setup)
        check_for_90_percent_similarity(serialized_setup, new_setup)

        # print(f"Serialized setup with ID: {previous_id}")
        # print(serialized_setup)


def check_for_90_percent_similarity(old_setup, new_setup):
    # if old_setup == new_setup:
    #     print(f"The newly added setup is the same as the following old setup: {old_setup}")

    similarity_counter = 0

    for key in new_setup:
        # old_setup[key] and new_setup[key] represent pieces at a specific position
        if key in old_setup and old_setup[key] == new_setup[key]:
            similarity_counter += 1

    print(similarity_counter)


def serialize_setup(setup_data):
    """Convert setup data to a dictionary of (row, col) -> piece."""
    return {(row, col): piece for _, _, row, col, piece in sorted(setup_data, key=lambda x: (x[2], x[3]))}


loop_setups(setup_positions, newly_added_setup)
