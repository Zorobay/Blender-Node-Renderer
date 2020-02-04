import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, FloatVectorProperty
from bpy.types import PropertyGroup


class PG_PublicProps(PropertyGroup):
    x_res: IntProperty(
        name="X Resolution", description="X resolution of renders", min=1, default=128,
        subtype="PIXEL"
    )

    y_res: IntProperty(
        name="Y Resolution", description="Y resolution of renders", min=1, default=128,
        subtype="PIXEL"
    )

    render_amount: IntProperty(
        name="Amount", description="Total amount of images to render", min=1, default=5
    )

    use_standard_setup: BoolProperty(
        name="Use Standard Setup", description="If true, creates a standard light/camera scene setup and renders from a plane.", default=False
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

    nodes_loaded: BoolProperty(
        name="Nodes Loaded",
        description="Signifies if the user have ordered the nodes to be loaded, and they we're successfully loaded",
        default=False
    )
