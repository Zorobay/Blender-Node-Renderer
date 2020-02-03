import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, FloatVectorProperty
from bpy.types import PropertyGroup
from src.operators.load_socket_props import NODE_EDITOR_OP_SetNodeParamShow


class PG_PublicProps(PropertyGroup):
    x_res: IntProperty(
        name="X Resolution", description="X resolution of renders", min=1, default=128
    )

    y_res: IntProperty(
        name="Y Resolution", description="Y resolution of renders", min=1, default=128
    )

    render_amount: IntProperty(
        name="Amount", description="Total amount of images to render", min=1, default=5
    )

    use_standard_setup: BoolProperty(
        name="Use Standard Setup", description="If true, creates a standard light/camera scene setup and renders from a plane.", default=False
    )

    run_show_set: BoolProperty(
        default=False,
        update=NODE_EDITOR_OP_SetNodeParamShow
    )


class FLOAT_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        default=0,
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        default=1,
    )


class FLOAT_FACTOR_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        default=0,
        min=0,
        max=1,
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        default=1,
        min=0,
        max=1,
    )

class FLOAT_VECTOR_XYZ_SOCKET_PG_UserProperties(PropertyGroup):

    user_min: FloatVectorProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
        default=(0,0,0),
        subtype="XYZ"
    )

    user_max: FloatVectorProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
        default=(1,1,1),
        subtype="XYZ"
    )

class COLOR_SOCKET_PG_UserProperties(PropertyGroup):
    user_min: FloatProperty(
        name="User Min",
        description="The minimum value that this input parameter will take during render",
    )

    user_max: FloatProperty(
        name="User Max",
        description="The maximum value that this input parameter will take during render",
    )


class PG_InternalProps(PropertyGroup):
    current_render: IntProperty(
        name="Current Render",
        description="The id number of the image currently running",
        min=1,
        default=1,
    )

    running: BoolProperty(
        name="Running",
        description="Indicates if the script is currently running",
        default=False,
    )
