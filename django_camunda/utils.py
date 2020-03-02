from typing import Any, Dict, List, Union

import inflection


def underscoreize(data: Union[List, Dict, str, None]) -> Union[List, Dict, str, None]:
    if isinstance(data, list):
        return [underscoreize(item) for item in data]

    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = inflection.underscore(key)
            # variables are dynamic names, can't make assumptions!
            if key == "variables":
                new_data[new_key] = value
            else:
                new_data[new_key] = underscoreize(value)
        return new_data

    return data


def serialize_variables(
    variables: Dict[str, Any]
) -> Dict[str, Dict[str, Union[str, float, int, None]]]:
    """
    Given a mapping of key: value, serialize into the Camunda Variables spec.

    Reference: https://docs.camunda.org/manual/7.12/reference/rest/overview/variables/

    This function looks at the variable types and serializes it accordingly. The result
    is a mapping of variableName: variableSpec. All Camunda default variable types
    are implemented.
    """
    raise NotImplementedError
