import bpy

from npr.src.operators.parameter_setup import find_socket_by_id


def get_input_min_maxes(input_node):
    if not input_node:
        return {}

    data = {}
    for i in input_node.inputs:
        id = i.identifier
        def_val = i.bl_rna.properties["default_value"]
        data[id] = {
            "min": def_val.soft_min,
            "max": def_val.soft_max
        }

    return data


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
            status = len(n.inputs) == 0 or len([i.name for i in n.inputs if not i.is_linked]) == 0 or n.type == "OUTPUT_MATERIAL"
            n.node_show = not status
            n.node_enabled = not status

            for i in n.inputs:
                status = i.is_linked or i.bl_idname in ("NodeSocketVector", "NodeSocketShader") or n.type == "OUTPUT_MATERIAL"
                i.input_enabled = not status
                i.input_show = not status

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
