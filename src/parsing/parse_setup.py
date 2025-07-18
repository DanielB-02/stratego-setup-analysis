import json
import ast


def string_to_json(string):
    import re
    
    # Find JSON content between first { and last }
    json_match = re.search(r'\{.*\}', string, re.DOTALL)
    if not json_match:
        raise ValueError("No JSON object found in response")
    
    json_string = json_match.group(0)
    setup = json.loads(json_string)

    for key in setup:
        setup[key] = ast.literal_eval(setup[key])

    return setup




