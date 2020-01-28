import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty
from bpy.types import PropertyGroup

class PG_PublicProps(PropertyGroup):
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

class FLOAT_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value for this socket that the user has defined.",
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value for this socket that the user has defined.",
    )

class COLOR_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value for this socket that the user has defined.",
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value for this socket that the user has defined.",
    )


class PG_InternalProps(PropertyGroup):
    current_render: IntProperty(
        name="Current Render",
        description="The id number of the image currently running.",
        min=1,
        default=1,
    )

    running: BoolProperty(
        name="Running",
        description="Indicates if the script is currently running.",
        default=False
    )
