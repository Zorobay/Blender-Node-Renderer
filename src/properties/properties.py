import bpy
from bpy.props import IntProperty

class PG_MyProperties(bpy.types.PropertyGroup):
    x_res : IntProperty(
        name="X Resolution",
        description="X resolution of renders",
        min=1,
        default=128
    )

    y_res: IntProperty(
        name="Y Resolution",
        description="Y resolution of renders",
        min=1,
        default=128
    )

    render_amount: IntProperty(
        name="Amount",
        description="Total amount of images to render",
        min=1,
        default=5
    )
