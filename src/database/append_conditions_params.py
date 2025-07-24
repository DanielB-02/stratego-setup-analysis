def build_conditions_and_params(kwargs):
    conditions = []
    params = []

    def add_exact_match(field, column_name):
        value = kwargs.get(field)
        if value is not None:
            conditions.append(f"{column_name} = ?")
            params.append(value)

    def add_range_filter(min_key, max_key, column_name):
        min_val = kwargs.get(min_key)
        max_val = kwargs.get(max_key)
        if min_val is not None and max_val is not None:
            conditions.append(f"{column_name} BETWEEN ? AND ?")
            params.extend([min_val, max_val])

    # Exact match filters
    filter_mappings = {
        "opponent": "opponent_name",
        "result": "result",
        "noob_killer": "noob_killer",
    }
    for key, column in filter_mappings.items():
        add_exact_match(key, column)

    # Range filters
    add_range_filter("min_moves", "max_moves", "moves")
    add_range_filter("start_date", "end_date", "date_played")

    return conditions, params