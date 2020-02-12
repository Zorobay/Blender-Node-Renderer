def find_socket_by_id(sockets, id: str):
    """Finds a socket among a collection of sockets (inputs/outputs) based on its unique identifier, and not its name.
    
    returns:
        The NodeSocket object with the specifier identifier. Returns None if not found.
    """

    for s in sockets:
        if s.identifier == id:
            return s

    return None


def socket_index_by_id(sockets, id):
    for i,s in sockets:
        if s.identifier == id:
            return 0

    return -1

def input_value_to_json(inp, append_euler=True):
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

def list_(value):
    try:
        return list(value)
    except TypeError:
        return [value]

def node_params_min_max_to_json(nodes) -> dict:
    """ 
    Returns a json document with information about the min and max values that the user has set for enabled parameters.
    Parameters with complex types (like vectors and colors) are added as separate parameters, and can be identified by their 'sub_index' parameter.
    """
    p = 0
    data = {}
    
    for n in nodes:
        if n.node_enabled:
            for i in n.inputs:
                if i.input_enabled:
                    i_data = {
                        "node_name": n.name,
                        "identifier": i.identifier,
                        "input_name": i.name,
                        "type": i.type
                        }
                    
                    umin = list_(i.user_props.user_min)
                    umax = list_(i.user_props.user_max)

                    assert len(umax)==len(umin)

                    for j in range(len(umin)):
                        data[p] = {
                            **i_data,
                            "user_min": umin[j],
                            "user_max": umax[j],
                            "sub_idex": j
                        }
                        p+=1

    return data
                        
                    


def find_number_of_enabled_sockets(nodes):
    num = 0
    for n in nodes:
        if n.node_enabled:
            for i in n.inputs:
                if i.input_enabled:
                    num = num + 1
    
    return num