import bpy
from src.panels.base_panel import NODE_EDITOR_PT_Panel

class NODE_EDITOR_PT_SettingsPanel(NODE_EDITOR_PT_Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Render Properties"
    bl_idname = "NODE_EDITOR_PT_SettingsPanel"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        material = context.material
        nodes = material.node_tree.nodes if material else None 
        all_props = scene.props

        # Copy the soft max and soft min properties from all node inputs to editable properties
        #bpy.ops.socket.load_props()

        # Display the currently selected material
        layout.label(text="Selected Material: " + material.name if material else "None")

        # Display rendering button
        layout.operator("node.render")

        # Display modal button
        layout.operator("my_category.custom_confirm_dialog", text="Modal test")

        # Display all the properties that can be changed by the user to control the rendering
        props = ["x_res", "y_res", "render_amount", "use_standard_setup"]
        for p in props:
            row = layout.row()
            split = row.split()
            col1 = split.column()
            col1.alignment = "RIGHT"
            col2 = split.column()

            name = all_props.bl_rna.properties[p].name
            col1.label(text=name)
            col2.prop(all_props, p, text="")

      
