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
