import bpy

class NODE_EDITOR_PT_NodesPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Render Nodes"
    bl_idname = "NODE_EDITOR_PT_NodesPanel"
    bl_space_type = "NODE_EDITOR"  # Location of panel
    bl_region_type = "UI"
    bl_category = "Render"  # Name of tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        material = context.material
        nodes = material.node_tree.nodes if material else None 

        for n in nodes:
            split = layout.split()
            c1 = split.column()
            c2 = split.column()
            c1.label(text=n.name)

            for i in n.inputs:
                c2.label(text=i.name)
        pass
