import bpy
from bpy.props import CollectionProperty, BoolProperty
from npr.src.panels.base_panel import NODE_EDITOR_PT_Panel

class NODE_EDITOR_PT_NodesPanel(NODE_EDITOR_PT_Panel):
    bl_idname = "NODE_EDITOR_PT_NodesPanel"
    bl_label = "Render Nodes"

    # @classmethod
    # def poll(cls, context):
    #     return context.scene.internal_props.nodes_loaded
        

    def draw(self, context):
        if not context.scene.internal_props.nodes_loaded:
            self.layout.label(text="Load the nodes to see options...")
            return

        layout = self.layout
        material = context.material
        nodes = list(material.node_tree.nodes) if material else []
        selected_node = context.active_node

        # Put selected node first
        if selected_node:
            try:
                nodes.insert(0, nodes.pop(nodes.index(selected_node)))
            except ValueError:
                print("Unable to find node {} in list of nodes for material {}".format(selected_node, material))

        for n in nodes:
            if not n.node_show:
                continue

            layout.prop(n, "node_enabled", text=n.name)
            box = layout.box()
            split = box.split(factor=0.45, align=True)
            c1 = split.column()
            c_min_max = split.column()
            split2 = c_min_max.split(factor=0.5, align=True)
            c2 = split2.column()
            c3 = split2.column()

            box.enabled = n.node_enabled

            for i in n.inputs:
                if not i.input_show:
                    continue

                c1.prop(i, "input_enabled", text="{}({})".format(i.identifier, i.name))

                try:
                    def_val_prop = i.bl_rna.properties["default_value"]
                    if i.bl_idname in ("NodeSocketColor"):
                        c2.label(text="ALL")
                        c3.label(text="ALL")
                    elif i.bl_idname.startswith("NodeSocketVector"):
                        c2.prop(i.user_props, "user_min", text="")
                        c3.prop(i.user_props, "user_max", text="")
                        c1.separator(factor=6.3)
                    else:
                        c2.prop(i.user_props, "user_min", text="")
                        c3.prop(i.user_props, "user_max", text="")                       
   
                except KeyError:
                    pass
