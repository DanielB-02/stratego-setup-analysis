import json
import ast


def string_to_json(string):
    json_string = string[8:-4]

    setup = json.loads(json_string)

    for key in setup:
        setup[key] = ast.literal_eval(setup[key])

    return setup




