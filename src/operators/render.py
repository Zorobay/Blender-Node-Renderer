from bpy.types import Operator
from bpy import ops
import random

class NODE_OP_Render(Operator):
    bl_idname = "node.render"
    bl_label = "Render"
    bl_options = {"REGISTER"}

    def permute_params(self, nodes):
        """Permutes the parameters of all node inputs
        
        Arguments:
            nodes -- The node group containing all nodes
        """

        for n in nodes:
            if n.name == "Material Output":
                continue

            for i in n.inputs:
                if i.is_linked:  # Don't change the value of connected inputs
                    continue

                try:
                    val = i.default_value

                    if i.type == "RGBA":
                        min = 0.0
                        max = 1.0
                        i.default_value = [random.randint(min,max), random.randint(min,max), random.randint(min,max), random.randint(min,max)]
                    elif i.type == "VALUE":
                        min = i.min_value if i.min_value else 0
                        max = i.min_value if i.max_value else 1
                except AttributeError:
                    pass

    def execute(self, context):
        objs = context.scene.objects
        selected_mat = context.material
        material = context.material
        render = context.scene.render
        all_props = context.scene.props
        nodes = material.node_tree.nodes if material else None

        # Delete unneeded objects
        obs_to_del = [o for o in objs if o.type in ("MESH", "LIGHT")]
        ops.object.delete({"selected_objects": obs_to_del})

        # Add plane and apply material
        ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
        plane = context.selected_objects[0]
        plane.data.materials.append(selected_mat)

        # Setup lighting
        ops.object.light_add(type="SUN", location=(0, 0, 3))  # Not needed for eevee
        sun = objs.get("Sun")
        sun.data.energy = 1

        # Setup camera placement
        cam = objs.get("Camera")
        cam.rotation_euler = (0, 0, 0)
        cam.location = (0, 0, 1.4)

        # Setup renderer
        render.resolution_x = all_props.x_res
        render.resolution_y = all_props.y_res
        render.engine = "BLENDER_EEVEE"

        # Setup render constants
        FILEPATH = render.filepath
        FILEPATH = FILEPATH[0:FILEPATH.rfind("\\")+1]
        FILE_EXTENSION = render.file_extension
        N = all_props.render_amount


        n = nodes.get("Group")
        inp = n.inputs.get("Wood scale")

        r = 0
        inp.default_value = 0
        MAX_VAL = 10
        while r < N:
            self.permute_params(nodes)
            render.filepath = "{}{}{}".format(FILEPATH, r, FILE_EXTENSION)
            ops.render.render(write_still=True)
            r += 1
            inp.default_value = (r / N) * MAX_VAL

        return {"FINISHED"}
