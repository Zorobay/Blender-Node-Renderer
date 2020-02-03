import bpy


def set_input_min_max(input_node, input):
    id = input.identifier
    output = input_node.outputs[id]
    min_val = output.min_value
    max_val = output.max_value

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

            # Save input node
            group_input_node = n.node_tree.nodes["Group Input"] if n.type == "GROUP" else None

            # Don't display nodes we can't control (no inputs or where all inputs are linked)
            status = len(n.inputs) == 0 or len([i.name for i in n.inputs if not i.is_linked]) == 0
            n.node_show = not status
            n.node_enable = not status

            for i in n.inputs:
                if group_input_node:
                    set_input_min_max(group_input_node, i)

                status = i.is_linked or i.bl_idname in ("NodeSocketVector", "NodeSocketShader")
                i.input_enable = not status
                i.input_show = not status

                try:
                    def_val = i.bl_rna.properties["default_value"]

                except KeyError:
                    pass

        context.scene.internal_props.nodes_loaded = True
        return {"FINISHED"}
        
        
