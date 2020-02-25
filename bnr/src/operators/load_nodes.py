import bpy

from bnr.src.operators.parameter_setup import find_socket_by_id
from bnr.src.misc.parameters import set_input_enabled, get_input_enabled, get_input_init_status
from bnr.src.misc.nodes import get_node_init_status


class NODE_EDITOR_OP_LoadNodes(bpy.types.Operator):
    bl_idname = "nodes.load_nodes"
    bl_label = "Load Nodes"
    bl_description = "Load nodes from selected material."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.material

    def execute(self, context):
        material = context.material
        nodes = material.node_tree.nodes

        for n in nodes:
            # Don't display nodes we can't control (no inputs or where all inputs are linked)
            status = get_node_init_status(n)
            n.node_show = status
            n.node_enabled = status

            for i in n.inputs:
                status = get_input_init_status(i,n)
                set_input_enabled(i, status, and_show=True)
                
                if i.type == "VALUE":
                    i.user_props.user_min = min(i.default_value, i.user_props.user_min)
                    i.user_props.user_max = max(i.default_value, i.user_props.user_max)

                if n.type == "GROUP":
                    interface = find_socket_by_id(n.node_tree.inputs, i.identifier)
                    try:
                        def_val = i.bl_rna.properties["default_value"]
                        max_val = interface.max_value if interface.max_value <= def_val.soft_max else def_val.soft_max
                        min_val = interface.min_value if interface.min_value >= def_val.soft_min else def_val.soft_min
                        if def_val.array_length == 3:
                            i.user_props.user_max = (max_val, max_val, max_val)
                            i.user_props.user_min = (min_val, min_val, min_val)
                        else:
                            i.user_props.user_min = min_val
                            i.user_props.user_max = max_val
                    except KeyError:
                        pass

        context.scene.internal_props.nodes_loaded = True
        return {"FINISHED"}
