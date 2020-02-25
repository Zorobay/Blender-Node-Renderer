import random
import bpy
from mathutils import Color
from bnr.src.misc import misc
from collections import abc


def get_input_init_status(i: bpy.types.NodeSocket, n: bpy.types.Node = None):
    """Returns the enable/show status of an input socket upon loading.
    
        Arguments:
            n (Node) - If set, will return false if the Node is not enabled. Set to None (Default) to ignore the status of the node (when using for 'input_show').
    """
    status = (not i.enabled) or i.is_linked or i.bl_idname in ("NodeSocketVector", "NodeSocketShader")
    if n:
         status = status or not n.node_enabled
    
    return not status

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

def set_input_enabled(input, enabled, and_show=False, ind=-1):
    if input.type in ("RGBA", "VECTOR"):
        if ind > 0:
            input.subinput_enabled[ind] = enabled
        else:
            input.subinput_enabled = enabled if isinstance(enabled, abc.Sequence) else [enabled]*3
        if and_show:
            input.input_show = enabled
    else:
        input.input_enabled = enabled
        if and_show:
            input.input_show = enabled

def get_input_enabled(input, ind=-1):
    if input.type in ("RGBA", "VECTOR"):
        if ind > 0:
            return input.subinput_enabled[ind]
        else:
            return any(input.subinput_enabled)
    
    return input.input_enabled


def set_random_value_for_input(input: bpy.types.NodeSocket):
    """
    Sets a new random value for an input based on its type.

    Arguments:
        input - A NodeSocket with property group 'user_props'
        
    Returns:
        The normalized label corresponding to the randomized value (or values if vector type) as a list
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
    elif input.type == "VALUE":
        val = random.uniform(umin, umax)
        input.default_value = val
    elif input.type == "INT":
        val = random.randint(umin, umax)
        input.default_value = val
    else:
        raise TypeError("Input of type {} not supported!".format(input.type))

    normalized_lbl = []
    umin = misc.list_(umin)
    umax = misc.list_(umax)
    val = misc.list_(val)
    for x in range(len(val)):
        normalized_lbl.append(misc.normalize(val[x], umin[x], umax[x]))

    return normalized_lbl