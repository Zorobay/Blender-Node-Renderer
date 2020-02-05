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
    "name": "Node Permutator Renderer",
    "author": "Sebastian Hegardt",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "Node Editor Toolbar under Render",
    "category": "Node",  # Used for filtering in the addons panel
}

import bpy
from bpy.props import PointerProperty, BoolProperty
from bpy.types import PropertyGroup
from npr.src.panels.settings_panel import NODE_EDITOR_PT_SettingsPanel
from npr.src.panels.nodes_panel import NODE_EDITOR_PT_NodesPanel
from npr.src.properties.properties import (
    PG_PublicProps,
    PG_InternalProps,
)
from npr.src.properties.socket_props import (
    FLOAT_SOCKET_PG_UserProperties,
    FLOAT_FACTOR_SOCKET_PG_UserProperties,
    FLOAT_VECTOR_SOCKET_PG_UserProperties,
)

from npr.src.operators.render import NODE_OP_Render
from npr.src.operators.modal import SimplePropConfirmOperator
from npr.src.operators.load_nodes import NODE_EDITOR_OP_LoadNodes
from npr.src.operators.parameter_setup import (
    NODE_EDITOR_OP_SaveParameterSetup,
    NODE_EDITOR_OP_LoadParameterSetup,
    NODE_EDITOR_OP_LoadDefaultParameters
)

panels = (
    NODE_EDITOR_PT_SettingsPanel,
    NODE_EDITOR_PT_NodesPanel,
)

operators = (
    SimplePropConfirmOperator,
    NODE_OP_Render,
    NODE_EDITOR_OP_LoadNodes,
    NODE_EDITOR_OP_SaveParameterSetup,
    NODE_EDITOR_OP_LoadParameterSetup,
    NODE_EDITOR_OP_LoadDefaultParameters
)

properties = (
    PG_PublicProps,
    PG_InternalProps,
    FLOAT_SOCKET_PG_UserProperties,
    FLOAT_FACTOR_SOCKET_PG_UserProperties,
    FLOAT_VECTOR_SOCKET_PG_UserProperties,
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

    # Register boolean property on the node type
    bpy.types.Node.node_enable = BoolProperty(default=False)
    bpy.types.Node.node_show = BoolProperty(default=False)

    # Register boolean property on the NodeSocket type
    bpy.types.NodeSocket.input_enable = BoolProperty(default=False)
    bpy.types.NodeSocket.input_show = BoolProperty(default=False)

    bpy.types.NodeSocketFloat.user_props = PointerProperty(type=FLOAT_SOCKET_PG_UserProperties)
    bpy.types.NodeSocketFloatFactor.user_props = PointerProperty(type=FLOAT_FACTOR_SOCKET_PG_UserProperties)

    # Register user props on vector types
    for t in VEC_TYPES:
        t.user_props = PointerProperty(type=FLOAT_VECTOR_SOCKET_PG_UserProperties)

    
def unregister():
    for c in (*properties, *operators, *panels):
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.props
    del bpy.types.Scene.internal_props
    del bpy.types.Node.node_enable
    del bpy.types.Node.node_show
    del bpy.types.NodeSocket.input_enable
    del bpy.types.NodeSocket.input_show
    del bpy.types.NodeSocketFloat.user_props

    for t in VEC_TYPES:
        del t.user_props
