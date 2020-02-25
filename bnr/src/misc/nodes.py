
import bpy

def get_node_init_status(n: bpy.types.Node):
    """Returns the enable/show status of a Node upon loading."""
    status = len(n.inputs) == 0 or len([i.name for i in n.inputs if not i.is_linked]) == 0 or n.type == "OUTPUT_MATERIAL"
    return not status
