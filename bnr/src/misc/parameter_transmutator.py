from bnr.src.misc.parameters import set_random_value_for_input, is_vector_type
from bnr.src.misc.to_json import input_value_to_json

def transmute_params_random(nodes):
    """transmutes the parameters of all enabled node inputs

    Arguments:
        nodes -- The node group containing all nodes

    Returns:
        A tuple with a dictionary file with the new parameters and a list of normalized labels
    """

    params = {}
    normalized_lbls = []

    for n in nodes:
        params[n.name] = {}

        for i in n.inputs:
            if i.input_enabled and n.node_enabled:  # Only transmute parameters if enabled
                if is_vector_type(i):
                    for i_sub, en in enumerate(i.subinput_enabled):
                        if en:
                            normalized_lbls.extend(set_random_value_for_input(i, i_sub=i_sub))
                else:
                    normalized_lbls.extend(set_random_value_for_input(i))

            try:
                if (not i.is_linked):  # Save parameter unless it is linked (even if it wasn't transmuted)
                    params[n.name][i.identifier] = input_value_to_json(i)
            except (AttributeError, KeyError):
                # Some special node sockets do not have a value, skip them
                pass

    return params, normalized_lbls
