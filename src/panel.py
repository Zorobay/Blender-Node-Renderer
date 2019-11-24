import bpy


class Render_Panel(bpy.types.Panel):
    bl_idname = "Render_Panel"
    bl_label = "Render Panel"
    bl_category = "Addon"
    bl_space_type = "VIEW3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("view3d.myrender", text="Render n instances")
