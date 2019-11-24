bl_info = {
    "name": "Automatic Node Renderer",
    "author": "Sebastian Hegardt",
    "description": "Addon to generate renders by automatically changing node variable values.",
    "blender": (2, 80, 0),
    "location": "Node Editor Toolbar under Misc",
    "category": "Node",
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Node Renderer"
    bl_idname = "NODE_EDITOR_PT_Renderer2"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        material = context.material
        nodes = material.node_tree.nodes

        # Create a simple row.
        layout.label(text="Current Material: " + material.name)

        my_int: IntProperty(
            name="My Integer",
            default=29,
            min=-1,
            max=204
        )
        for n in nodes:
            split = layout.split()
            col1 = split.column()
            col1.label(text=n.name)
            col2 = split.column()
            for i in n.inputs:
                def_val = i.default_value
                min_val = i.min_value
                col2.label(text="{}[{}],".format(i.name, i.default_value))
        # row.prop(scene, "frame_start")
        # row.prop(scene, "frame_end")
        #
        # # Create an row where the buttons are aligned to each other.
        # layout.label(text=" Aligned Row:")
        #
        # row = layout.row(align=True)
        # row.prop(scene, "frame_start")
        # row.prop(scene, "frame_end")
        #
        # # Create two columns, by using a split layout.
        # split = layout.split()
        #
        # # First column
        # col = split.column()
        # col.label(text="Column One:")
        # col.prop(scene, "frame_end")
        # col.prop(scene, "frame_start")
        #
        # # Second column, aligned
        # col = split.column(align=True)
        # col.label(text="Column Two:")
        # col.prop(scene, "frame_start")
        # col.prop(scene, "frame_end")
        #
        # # Big render button
        # layout.label(text="Big Button:")
        # row = layout.row()
        # row.scale_y = 3.0
        # row.operator("render.render")
        #
        # # Different sizes in a row
        # layout.label(text="Different button sizes:")
        # row = layout.row(align=True)
        # row.operator("render.render")
        #
        # sub = row.row()
        # sub.scale_x = 2.0
        # sub.operator("render.render")
        #
        # row.operator("render.render")


classes = (
    LayoutDemoPanel,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.register_class(c)


if __name__ == "__main__":
    #get the current material in draw(context) from context.material

    register()
