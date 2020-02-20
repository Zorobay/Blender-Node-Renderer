from bnr.src.misc.parameters import set_random_value_for_input
from bnr.src.misc.to_json import input_value_to_json

def transmute_params_random(nodes):
    """transmutes the parameters of all node inputs

    Arguments:
        nodes -- The node group containing all nodes

    Returns:
        A tuple with a dictionary file with the new parameters and a list of normalized labels
    """

    params = {}
    normalized_lbl = []

    for n in nodes:
        params[n.name] = {}

        for i in n.inputs:
            try:
                if i.input_enabled and n.node_enabled:  # Only transmute parameters if enabled
                    set_random_value_for_input(i, normalized_lbl=normalized_lbl)

                if (not i.is_linked):  # Save parameter unless it is linked (even if it wasn't transmuted)
                    params[n.name][i.identifier] = input_value_to_json(i)

            except AttributeError:
                pass
            except KeyError:
                pass

    return params, normalized_lbl
