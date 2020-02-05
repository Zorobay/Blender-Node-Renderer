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

def input_value_to_json(inp):
    """
    Extracts the default value of an input socket and returns it in a JSON comatible format.
    """
    if inp.bl_rna.properties["default_value"].array_length > 1:
        val = list(inp.default_value)
        if inp.bl_idname == "NodeSocketVectorEuler":
            val.append(inp.default_value.order)

        return val
    else:
        return inp.default_value
