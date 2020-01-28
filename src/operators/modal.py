import bpy


class SimplePropConfirmOperator(bpy.types.Operator):
    """Really?"""
    bl_idname = "my_category.custom_confirm_dialog"
    bl_label = "===== Rendering Progress ====="
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print("RUNNING MODAL!")
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
            return {'PASS_THROUGH'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text="Rendering x of x")
