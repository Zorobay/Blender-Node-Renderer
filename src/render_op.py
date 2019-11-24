import bpy

class Render_Operator(bpy.types.Operator):
    bl_idname = "view3d.myrender"
    bl_label = "Render test!"
    bl_description = "Render me!"

    def execute(self, context):
        bpy.ops.snap_cursor_to_center()
        return ("Finished!")


