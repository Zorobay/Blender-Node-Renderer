import bpy
from bpy.props import CollectionProperty, BoolProperty
from src.panels.base_panel import NODE_EDITOR_PT_Panel


class NODE_EDITOR_PT_NodesPanel(NODE_EDITOR_PT_Panel):
    bl_idname = "NODE_EDITOR_PT_NodesPanel"
    bl_label = "Render Nodes"

    def draw(self, context):
        layout = self.layout
        material = context.material
        nodes = list(material.node_tree.nodes) if material else []
        selected_node = context.active_node

        # Disply a 'Save Parameter Setup' button and a 'Load Parameter Setup" button
        split_op = layout.split()
        cop1 = split_op.column()
        cop2 = split_op.column()
        cop1.operator("node.save_parameter_setup", icon="FILE_TICK")
        cop2.operator("node.load_parameter_setup", icon="FILEBROWSER")

        # Put selected node first
        if selected_node:
            nodes.insert(0, nodes.pop(nodes.index(selected_node)))

        for n in nodes:
            # Don't display nodes we can't control (no inputs) or where all inputs are linked
            if len(n.inputs) == 0 or len([i.name for i in n.inputs if not i.is_linked]) == 0:  
                continue

            layout.prop(n, "node_enable", text=n.name)
            box = layout.box()
            split = box.split()
            c1 = split.column()
            c2 = split.column()
            c3 = split.column()

            box.enabled = n.node_enable

            for i in n.inputs:
                if i.is_linked:
                    continue

                c1.prop(i, "input_enable", text=i.name)

                try:
                    def_val_prop = i.bl_rna.properties["default_value"]
                    if i.bl_idname in ("NodeSocketFloat", "NodeSocketFloatFactor"):
                        c2.prop(i.user_props, "user_min", text="")
                        c3.prop(i.user_props, "user_max", text="")
                    elif i.bl_idname == "NodeSocketColor":
                        c2.label(text="ALL")
                        c3.label(text="ALL")
                        # c2.prop(i.bl_rna.properties, "default_value", text="")
                        pass
                    elif i.bl_idname == "NodeSocketVectorXYZ":
                        c2.prop(i.user_props, "user_min", text="")
                        c3.prop(i.user_props, "user_max", text="")
                        c1.separator(factor=6.3)
                    else:
                        # Insert empty space so that the column items are aligned properly
                        c2.separator_spacer()
                        c3.separator_spacer()
                        pass

                except KeyError:
                    pass
