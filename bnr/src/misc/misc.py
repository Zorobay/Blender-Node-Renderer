def normalize(val, umin, umax):
    """Normalizes the value to range [-1,1]"""
    try:
        return ((val - umin) / (umax - umin)) * 2 - 1
    except ZeroDivisionError:
        return 1


def list_(value):
    """Converts the input value to a list or puts the input value in a list."""
    try:
        return list(value)
    except TypeError:
        return [value]


def color_clamp(val):
    """Controls the value val so that it is in the range [0,1] and if the value is larger than 1, the overflow will be added to zero. 
    If the value is less than zero, the overflow will be subtracted from 1. In this way, we can produce well centered HSV values, even if the mean
    is around 0 or 1.
    
    Example:
        1.5 will be converted to 0.5
        2.3 will be converted to 0.3
        -1 will be converted to 0
        -0.3 will be converted to 0.7
        0.5 will be converted to 0.5    
    """
    return val % 1
