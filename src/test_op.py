import bpy
from bpy.types import Operator

class TestOP(Operator):
    bl_idname = "object.move_x"  # A unique identifier
    bl_label = "Move an object X" # The display name of the operator
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        scene = context.scene
        for obj in scene.objects:
            obj.location.x -= 1.0

        return {"FINISHED"}

        