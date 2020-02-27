# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Node Renderer",
    "author": "Sebastian Hegardt",
    "description": "An Addon for Blender that can automatically vary a set of node parameters based on user defined criteria and render each variation.",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "Node Editor Toolbar under Render",
    "category": "Node",  # Used for filtering in the addons panel
}

import bpy
from bpy.props import PointerProperty, BoolProperty, BoolVectorProperty

from bnr.src.operators.load_nodes import NODE_EDITOR_OP_LoadNodes
from bnr.src.operators.parameter_setup import (
    NODE_EDITOR_OP_SaveParameterSetup,
    NODE_EDITOR_OP_LoadParameterSetup,
    NODE_EDITOR_OP_LoadDefaultParameters
)
from bnr.src.operators.render import NODE_OP_Render
from bnr.src.panels.nodes_panel import NODE_EDITOR_PT_NodesPanel
from bnr.src.panels.settings_panel import NODE_EDITOR_PT_SettingsPanel
from bnr.src.properties.properties import (
    PG_PublicProps,
    PG_InternalProps,
    PG_ParameterEliminationProperties
)
from bnr.src.properties.socket_props import (
    FLOAT_SOCKET_PG_UserProperties,
    FLOAT_FACTOR_SOCKET_PG_UserProperties,
    FLOAT_VECTOR_SOCKET_PG_UserProperties,
    COLOR_SOCKET_PG_UserProperties,
)

from bnr.src.operators.eliminate_parameters import NODE_OP_EliminateParameters

panels = (
    NODE_EDITOR_PT_SettingsPanel,
    NODE_EDITOR_PT_NodesPanel,
)

operators = (
    NODE_OP_Render,
    NODE_EDITOR_OP_LoadNodes,
    NODE_EDITOR_OP_SaveParameterSetup,
    NODE_EDITOR_OP_LoadParameterSetup,
    NODE_EDITOR_OP_LoadDefaultParameters,
    NODE_OP_EliminateParameters,
)

properties = (
    PG_PublicProps,
    PG_InternalProps,
    PG_ParameterEliminationProperties,
    FLOAT_SOCKET_PG_UserProperties,
    FLOAT_FACTOR_SOCKET_PG_UserProperties,
    FLOAT_VECTOR_SOCKET_PG_UserProperties,
    COLOR_SOCKET_PG_UserProperties,
)

VEC_TYPES = (bpy.types.NodeSocketVectorXYZ, bpy.types.NodeSocketVector, bpy.types.NodeSocketVectorAcceleration,
             bpy.types.NodeSocketVectorDirection, bpy.types.NodeSocketVectorTranslation, bpy.types.NodeSocketVectorEuler)

def register():
    for c in (*properties, *operators, *panels):
        bpy.utils.register_class(c)

    # Register the properties on the scene object so it is accessible everywhere
    bpy.types.Scene.props = PointerProperty(type=PG_PublicProps)

    # Register our internal props on the Scene object
    bpy.types.Scene.internal_props = PointerProperty(type=PG_InternalProps)

    # Register internal properties for parameter elimination
    bpy.types.Scene.pe_props = PointerProperty(type=PG_ParameterEliminationProperties)

    # Register boolean property on the node type
    bpy.types.Node.node_enabled = BoolProperty(default=False)
    bpy.types.Node.node_show = BoolProperty(default=False)

    # Register boolean property on the NodeSocket type
    bpy.types.NodeSocketStandard.input_enabled = BoolProperty(default=False)
    bpy.types.NodeSocketStandard.input_show = BoolProperty(default=False)

    bpy.types.NodeSocketFloat.user_props = PointerProperty(type=FLOAT_SOCKET_PG_UserProperties)
    bpy.types.NodeSocketFloatFactor.user_props = PointerProperty(type=FLOAT_FACTOR_SOCKET_PG_UserProperties)
    bpy.types.NodeSocketColor.user_props = PointerProperty(type=COLOR_SOCKET_PG_UserProperties)

    # Override input_enabled for vector types (as we keep x,y and z as separate inputs)
    bpy.types.NodeSocketColor.subinput_enabled = BoolVectorProperty(default=(False, False, False))

    # Register user props on vector types
    for t in VEC_TYPES:
        default_min = FLOAT_VECTOR_SOCKET_PG_UserProperties.bl_rna.properties["user_min"]
        default_max = FLOAT_VECTOR_SOCKET_PG_UserProperties.bl_rna.properties["user_max"]
        subtype = t.bl_rna.properties["default_value"].subtype
        subtype = subtype if len(subtype) > 0 else "NONE"

        VectorPropertyType = type(
            "FLOAT_VECTOR_SOCKET_PG_UserProperties",
            (bpy.types.PropertyGroup,),
            {
                "user_min": bpy.props.FloatVectorProperty(
                    name=default_min.name,
                    default=default_min.default_array,
                    description=default_min.description,
                    subtype=subtype),
                "user_max": bpy.props.FloatVectorProperty(
                    name=default_max.name,
                    default=default_max.default_array,
                    description=default_max.description,
                    subtype=subtype)
            })
        bpy.utils.register_class(VectorPropertyType)
        t.user_props = PointerProperty(type=VectorPropertyType)
        t.subinput_enabled = BoolVectorProperty(default=(False, False, False))


def unregister():
    for c in (*properties, *operators, *panels):
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.props
    del bpy.types.Scene.internal_props
    del bpy.types.Node.node_enabled
    del bpy.types.Node.node_show
    del bpy.types.NodeSocketStandard.input_enabled
    del bpy.types.NodeSocketStandard.input_show
    del bpy.types.NodeSocketFloat.user_props

    for t in (*VEC_TYPES, bpy.types.NodeSocketColor):
        del t.user_props
        del t.subinput_enabled
