from bnr.src.misc.misc import list_
from bnr.src.misc.parameters import get_input_enabled, is_vector_type

KEY_ENABLED = "enabled"
KEY_USER_PARAMS = "user_params"
KEY_DEFAULT_PARAMS = "default_params"
KEY_MAX = "user_max"
KEY_MIN = "user_min"
KEY_NAME = "name"
KEY_SUB_INDEX = "i_sub"

def input_value_to_json(inp):
    """
    Extracts the default value of an input socket and returns it in a JSON compatible format.
    """
    if inp.bl_rna.properties["default_value"].array_length > 1:
        val = list(inp.default_value)
        if inp.bl_idname == "NodeSocketVectorEuler":
            val.append(inp.default_value.order)

        return val
    else:
        return inp.default_value


def node_params_to_json(nodes) -> dict:
    """Extract user set min and max value of node parameters (inputs) and returns them in a dictionary.

    Arguments:
        nodes - a collection of a material's nodes

    Returns:
        dict -- a dictionary with parameter values
    """
    data = {}
    for n in nodes:
        if n.type == "FRAME":
            continue

        data[n.name] = {
            KEY_ENABLED: n.node_enabled,
            KEY_USER_PARAMS: {},
            KEY_DEFAULT_PARAMS: {},
        }

        for i in n.inputs:
            if i.is_linked:
                continue

            # Store default value
            try:
                data[n.name][KEY_DEFAULT_PARAMS][i.identifier] = input_value_to_json(i)
            except (AttributeError, KeyError):
                pass

            # Store user data
            try:
                props = i.user_props
                if is_vector_type(i):
                    u_min = list(props.user_min)
                    u_max = list(props.user_max)
                else:
                    u_min = props.user_min
                    u_max = props.user_max

                input_data = {
                    KEY_ENABLED: get_input_enabled(i),
                    KEY_MIN: u_min,
                    KEY_MAX: u_max,
                }
            except AttributeError:
                input_data = {
                    KEY_ENABLED: get_input_enabled(i),
                }

            data[n.name][KEY_USER_PARAMS][i.identifier] = {
                KEY_NAME: i.name,
                KEY_USER_PARAMS: input_data,
            }

    return data


def node_params_min_max_to_json(nodes) -> dict:
    """
    Returns a json document with information about the min and max values that the user has set for enabled parameters.
    Parameters with complex types (like vectors and colors) are added as separate parameters, and can be identified by their 'i_sub' field.
    """
    p = 0
    data = {}

    for n in nodes:
        if n.node_enabled:
            for i in n.inputs:
                umin = i.user_props.user_min
                umax = i.user_props.user_max
                i_data = {
                    "node_name": n.name,
                    "identifier": i.identifier,
                    "input_name": i.name,
                    "type": i.type
                }

                if is_vector_type(i):
                    for i_sub,(mi,ma) in enumerate(zip(umin, umax)):
                        if i.subinput_enabled[i_sub]:
                            data[p] = {
                                **i_data,
                                KEY_MIN: mi,
                                KEY_MAX: ma,
                                KEY_SUB_INDEX: i_sub
                            }
                            p+=1
                elif i.input_enabled:
                    data[p] = {
                        **i_data,
                        KEY_MIN: umin,
                        KEY_MAX: umax,
                        KEY_SUB_INDEX: 0
                    }
                    p+=1

    return data