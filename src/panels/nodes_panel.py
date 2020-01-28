import bpy
from bpy.props import CollectionProperty, BoolProperty
from src.panels.base_panel import NODE_EDITOR_PT_Panel


class NODE_EDITOR_PT_NodesPanel(NODE_EDITOR_PT_Panel):
    bl_idname = "NODE_EDITOR_PT_NodesPanel"
    bl_label = "Render Nodes"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        material = context.material
        nodes = material.node_tree.nodes if material else []

        for n in nodes:
            row = layout.row()
            row.prop(n, "node_enable", text=n.name)
            box = layout.box()
            split = box.split()
            c2 = split.column()
            c3 = split.column()
            c4 = split.column()

            #c1.prop(n, "node_enable", text=n.name)
            box.enabled = n.node_enable

            for i in n.inputs:
                c2.prop(i, "input_enable", text=i.name)

            try:
                def_val_prop = i.bl_rna.properties["default_value"]
                if i.bl_idname == "NodeSocketFloat":
                    c3.prop(i.user_props, "user_min", text="")
                    c4.prop(i.user_props, "user_max", text="")
            except KeyError:
                pass
