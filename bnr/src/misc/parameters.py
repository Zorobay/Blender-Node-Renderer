import random
import bpy
import numpy as np
from mathutils import Color
from bnr.src.misc import misc
from collections import abc

def is_vector_type(input: bpy.types.NodeSocket):
    """Returns true if the input is of vector type (like ColorSocket or NodeSocketVectorXXX) else False."""
    return input.type in ("VECTOR", "RGBA")


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
    if is_vector_type(input):
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

def get_input_enabled(input, i_sub=-1):
    if is_vector_type(input):
        if i_sub > 0:
            return input.subinput_enabled[i_sub]
        else:
            return any(input.subinput_enabled)
    
    return input.input_enabled

def set_random_color(input: bpy.types.NodeSocket, umin: list, umax: list, i_sub=-1):
    """
    Calculates a random color based on the HSV ranges supplied in umin and umax. The value of the input will be set to this color. 
    If i_sub is supplied, only this index will be randomized, else all 3 channels will be randomized.
    
        Returns:
            A list with 1 or 3 new HSV values, based on whether i_sub was supplied or not.
    """
    assert i_sub < 3, "i_sub can not be greater than 2 as it corresponds to an index in a color vector (and alpha is not supported)!"

    c = Color(input.default_value[:3])  # Exclude the alpha channel
    if i_sub == 0:
        val = misc.color_clamp(random.normalvariate(umin.x, umax.x))
        c.h = val
    elif i_sub == 1:
        val = misc.color_clamp(random.normalvariate(umin.y, umax.y))
        c.s = val
    elif i_sub == 2:
        val = misc.color_clamp(random.normalvariate(umin.z, umax.z))
        c.v = val
    elif i_sub < 0:
        val = [misc.color_clamp(random.normalvariate(umin.x, umax.x)), misc.color_clamp(random.normalvariate(umin.y, umax.y)), misc.color_clamp(random.normalvariate(umin.z, umax.z))]
        c.hsv = val

    input.default_value = [*c[:], 1.0]
    return val

def set_random_vector(input: bpy.types.NodeSocket, umin:list, umax:list, i_sub=-1):
    """
    Calculates a list of random values based on the ranges supplied in umin and umax. The value of the input will be set to this list.
    If i_sub is supplied, only this index will be randomized, else all 3 values will be randomized.
    
        Returns:
            A list with 1 or 3 random values, based on whether i_sub was supplied or not.
    """
    assert i_sub < 3, "i_sub can not be greater than 2 as it corresponds to an index in a vector (and Blender only has 3D vectors)."

    if i_sub < 0:
        val = [random.uniform(umin.x, umax.x), random.uniform(umin.y, umax.y), random.uniform(umin.z, umax.z)]
        input.default_value = val
    else:
        val = random.uniform(umin[i_sub], umax[i_sub])
        input.default_value[i_sub] = val

    return val

def set_random_value_for_input(input: bpy.types.NodeSocket, i_sub = -1):
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

    if input.type == "RGBA":
        val = set_random_color(input, umin, umax, i_sub=i_sub)
    elif input.type == "VECTOR":
        val = set_random_vector(input, umin, umax, i_sub=i_sub)
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
    if i_sub >= 0:
        normalized_lbl.append(misc.normalize(val[0], umin[i_sub], umax[i_sub])) 
    else:
        for x in range(len(val)):
            normalized_lbl.append(misc.normalize(val[x], umin[x], umax[x]))

    return normalized_lbl

def linspace(input: bpy.types.NodeSocket, n:int, i_sub=-1) -> np.ndarray:
    """
    Generates a linspace between a sockets user set minimum and maximum of length n.
    The linspace will correspond to 95% of possible values of a normal distribution if the input is of type RGBA.
    """
    if i_sub >= 0:
        umin = input.user_props.user_min[i_sub]
        umax = input.user_props.user_max[i_sub]
    else:
        umin = input.user_props.user_min
        umax = input.user_props.user_max

    if input.type == "RGBA":
        mu = umin
        std = umax
        mi, ma = mu-2*std, mu + 2*std # Capture 95% of values sampled from normal dist
        return linspace_color(mi, ma, n)
    else:
        return np.linspace(umin, umax, num=n, endpoint=True)

def linspace_color(start, end, n: int):
    lin = np.linspace(start, end, num=n, endpoint=True)
    return [misc.color_clamp(x) for x in lin]
        
