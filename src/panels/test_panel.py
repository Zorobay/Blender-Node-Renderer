import bpy

class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Render Properties"
    bl_idname = "NODE_EDITOR_PT_PropertiesPanel"
    bl_space_type = "NODE_EDITOR"  # Location of panel
    bl_region_type = "UI"
    bl_category = "Render"  # Name of tab

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        material = context.material
        nodes = material.node_tree.nodes if material else None 
        all_props = scene.props

        # Display the currently selected material
        layout.label(text="Selected Material: " + material.name if material else "None")

        # Display all the properties that can be changed by the user to control the rendering
        props = ["x_res", "y_res", "render_amount"]
        for p in props:
            row = layout.row()
            split = row.split()
            col1 = split.column()
            col2 = split.column()

            col2.prop(all_props, p)

        # Display rendering button
        layout.operator("node.render")
