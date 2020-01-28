from bpy.types import Operator
from bpy import ops
import random
import sys
import json

class NODE_OP_Render(Operator):
    bl_idname = "node.render"
    bl_label = "Render"
    bl_options = {"REGISTER"}

    def permute_params(self, nodes):
        """Permutes the parameters of all node inputs
        
        
        Arguments:
            nodes -- The node group containing all nodes

        Returns:
            A dictionary file with the new parameters.
        """

        params = {}
        for n in nodes:
            if not n.node_enable:
                continue
            params[n.name] = {}

            for i in n.inputs:
                if not i.input_enable or i.is_linked:  # Don't change the value of connected inputs
                    continue

                try:
                    # Get properties of the default value
                    def_val_prop = i.bl_rna.properties["default_value"]  # TODO only do once
                    s_min = def_val_prop.soft_min
                    s_max = def_val_prop.soft_max  

                    if i.type == "RGBA":
                        i.default_value = [random.randint(s_min,s_max), random.randint(s_min,s_max), random.randint(s_min,s_max), random.randint(s_min,s_max)]
                        params[n.name][i.name] = list(i.default_value)
                    elif def_val_prop.type == "FLOAT":
                        i.default_value = random.uniform(s_min, s_max)
                        params[n.name][i.name] = i.default_value
                    else:
                        print(i.type)

                except AttributeError:
                    pass

        return params

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

        param_data = {}
        r = 0
        MAX_VAL = 10 

        ops.my_category.custom_confirm_dialog()  # Invoke other operator
        sys.stdout.write("===== STARTING RENDERING JOB ({}) =====\n".format(N))

        while r < N:
            # Print progress information
            msg = "Rendering image {} of {}".format(r+1,N)
            sys.stdout.write(msg + chr(8)*len(msg))
            sys.stdout.flush()

            param_data[r] = self.permute_params(nodes)
            render.filepath = "{}{}{}".format(FILEPATH, r, FILE_EXTENSION)
            ops.render.render(write_still=True)
            r += 1

        # Write param data to file
        with open(FILEPATH + "param_data.json", "w") as f:
             json.dump(param_data, f)

        sys.stdout.write("DONE!")

        return {"FINISHED"}
