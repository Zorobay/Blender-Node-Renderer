import bpy


class NODE_EDITOR_PT_Panel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_space_type = "NODE_EDITOR"  # Location of panel
    bl_region_type = "UI"
    bl_category = "Render"  # Name of tab
