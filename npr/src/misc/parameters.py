import random
import bpy
from mathutils import Color
from npr.src.misc import misc

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
    for s in sockets:
        if s.identifier == id:
            return 0

    return -1

def find_number_of_enabled_sockets(nodes):
    num = 0
    for n in nodes:
        if n.node_enabled:
            for i in n.inputs:
                if i.input_enabled:
                    num = num + 1

    return num

def set_random_value_for_input(input: bpy.types.NodeSocket, normalized_lbl=None):
    """
    Sets a new random value for an input based on its type.

    Arguments:
        input - A NodeSocket with property group 'user_props'
        normalized_lbl (list) - If provided, the normalized label corresponding to the randomized value will be appended.
    """
    assert input.user_props, "Input of type {} does not have property 'user_props'!".format(input.type)
    umin = input.user_props.user_min
    umax = input.user_props.user_max

    # Get properties of the default value
    def_val_prop = input.bl_rna.properties["default_value"]

    if input.type == "RGBA":
        c = Color()
        c.hsv = misc.color_clamp(random.normalvariate(umin.x, umax.x)), misc.color_clamp(random.normalvariate(umin.y, umax.y)), misc.color_clamp(random.normalvariate(umin.z, umax.z))
        val = [*c.hsv]
        input.default_value = [*c.rgb, 1.0]
    elif input.type == "VECTOR":
        val = [
            random.uniform(umin.x, umax.x),
            random.uniform(umin.y, umax.y),
            random.uniform(umin.z, umax.z),
        ]
        input.default_value = val
    elif def_val_prop.type == "FLOAT":
        val = random.uniform(umin, umax)
        input.default_value = val
        val = [val]
    else:
        raise TypeError("Input of type {} not supported!".format(input.type))

    if normalized_lbl:
        umin = misc.list_(umin)
        umax = misc.list_(umax)
        for x in range(len(val)):
            normalized_lbl.append(misc.normalize(val[x], umin[x], umax[x]))
