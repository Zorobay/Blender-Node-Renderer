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
    "name" : "SimpleTestAddon",
    "author" : "Sebastian Hegardt",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Object",
    "category" : "Node" # Used for filtering in the addons panel
}

import bpy
from bpy.props import PointerProperty
from src.test_op import TestOP
from src.panels.test_panel import LayoutDemoPanel
from src.panels.nodes_panel import NODE_EDITOR_PT_NodesPanel
from src.properties.properties import PG_MyProperties
from src.operators.render  import NODE_OP_Render

classes = (
    PG_MyProperties,
    NODE_OP_Render,
    LayoutDemoPanel,
    NODE_EDITOR_PT_NodesPanel,
    TestOP
)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    # Register the properties on the scene object so it is accessible everywhere
    bpy.types.Scene.props = PointerProperty(type=PG_MyProperties)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.props
