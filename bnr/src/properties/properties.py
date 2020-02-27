import bpy

from pathlib import Path
from bpy.props import IntProperty, BoolProperty, EnumProperty, CollectionProperty, StringProperty, FloatProperty
from bpy.types import PropertyGroup


def set_abs_path(self, context):
    abs_path = bpy.path.abspath(self.render_output_dir)
    self["render_output_dir"] = abs_path


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
        name="Use Standard Setup", description="If true, creates a standard light/camera scene setup and renders from a plane.", default=True
    )

    render_output_dir: StringProperty(
        name="Render Output Dir",
        subtype="DIR_PATH",
        default="",
        update=set_abs_path
    )

    STRATEGIES = [("0", "Input Consecutive", "Inputs will be permuted consecutively. For any sample, only one input will be changed"),
                  ("1", "Input Simultaneously", "Blö")]

    permutation_strategy: EnumProperty(
        name="Permutation Strategy",
        description="The strategy to use when permuting parameters",
        default="0",
        items=STRATEGIES
    )

    eliminate_parameters: BoolProperty(
        name="Eliminate Parameters",
        description="Run a parameter elimination strategy to automatically disable parameters that do not contribute enough change in the look of the renders.",
        default=False)


class PG_ParameterEliminationProperties(PropertyGroup):
    render_tmp_output: StringProperty(default=str(Path("/tmp/")))
    L_loops: IntProperty(default=5)
    C_components: IntProperty(default=8)
    norm_thresh: FloatProperty(default=2.0)
    N_renders: IntProperty(default=8)
    i_sub: IntProperty()
    total_explained_var_thresh: FloatProperty(default=0.89)


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

    absolute_render_dir: PG_ParameterEliminationProperties

    parameter_setup_filepath: StringProperty()



