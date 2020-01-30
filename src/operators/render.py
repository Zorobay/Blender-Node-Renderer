import bpy
from bpy.types import Operator
from bpy import ops
import random
import sys
import json
import time
from src.operators.parameter_setup import node_params_default_vaulues_to_json
from mathutils import Vector


SCENE_NAME = "RENDER_SCENE_TMP"

def add_node(context, nodetype):
    bpy.ops.node.add_node(type=nodetype.__name__)  # WRONG! NEED TO CHANGE CONTEXT!
    node = context.active_node
    return node

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
                if (
                    not i.input_enable or i.is_linked
                ):  # Don't change the value of connected inputs
                    continue

                try:
                    # Get properties of the default value
                    def_val_prop = i.bl_rna.properties["default_value"]
                    u_min = i.user_props.user_min
                    u_max = i.user_props.user_max

                    if i.type == "RGBA":
                        i.default_value = [
                            random.randint(u_min, u_max),
                            random.randint(u_min, u_max),
                            random.randint(u_min, u_max),
                            1.0,
                        ]
                        params[n.name][i.name] = list(i.default_value)
                    elif i.bl_idname == "NodeSocketVectorXYZ":
                        i.default_value = [
                            random.uniform(u_min.x, u_max.x),
                            random.uniform(u_min.y, u_max.y),
                            random.uniform(u_min.z, u_max.z)
                        ]
                        params[n.name][i.name] = list(i.default_value)
                    elif def_val_prop.type == "FLOAT":
                        i.default_value = random.uniform(u_min, u_max)
                        params[n.name][i.name] = i.default_value
                    else:
                        print(i.type)

                except AttributeError as e:
                    pass
                except KeyError:
                    pass

        return params

    def execute(self, context):
        selected_scene = context.window.scene
        # Make a full copy of the current scene and only manipulate that one
        try:
            # Check if an old scene copy exists and delete it
            context.window.scene = bpy.data.scenes[SCENE_NAME]
            ops.object.select_all()
            ops.object.delete()
            bpy.ops.scene.delete()
        except KeyError as e:
            print(e)
            pass

        ops.scene.new(type="FULL_COPY")
        context.scene.name = SCENE_NAME

        objs = context.scene.objects
        material = context.material
        render = context.scene.render
        all_props = context.scene.props
        nodes = material.node_tree.nodes if material else []

        if all_props.use_standard_setup:
            # Delete unneeded objects
            obs_to_del = [o for o in objs if o.type in ("MESH", "LIGHT", "CAMERA")]
            ops.object.delete({"selected_objects": obs_to_del})

            # Add plane and apply material
            ops.mesh.primitive_plane_add(
                size=1, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0)
            )
            plane = context.selected_objects[0]
            plane.data.materials.append(material)

            # Setup HDRI
            world_node_tree = context.scene.world.node_tree
            print(context.active_node)
            world_node_tree.nodes.clear()
            world_output_node = add_node(context, bpy.types.ShaderNodeOutputWorld)
            background_node = add_node(context, bpy.types.ShaderNodeBackground)
            # world_node_tree.links.new(background_node.outputs["Background"], world_output_node.inputs["Surface"])
            # world_node_tree.nodes["Background"].inputs["Strength"].default_value = 0.44

            #ops.object.light_add(type="SUN", location=(0, 0, 3))  # Not needed for eevee
            #sun = context.selected_objects[0]
            #sun.data.energy = 1

            # Setup camera placement
            ops.object.camera_add(rotation=(0,0,0), location=(0,0,1.4))
            context.selected_objects[0].name = "Rendering Camera"
            context.scene.camera = context.object


        # Setup renderer
        render.resolution_x = all_props.x_res
        render.resolution_y = all_props.y_res
        render.engine = "CYCLES"
        context.scene.cycles.samples = 120

        # Setup render constants
        FILEPATH = render.filepath
        FILEPATH = FILEPATH[0 : FILEPATH.rfind("\\") + 1]
        FILE_EXTENSION = render.file_extension
        N = all_props.render_amount

        param_data = {}
        r = 0
        MAX_VAL = 10

        # ops.my_category.custom_confirm_dialog()  # Invoke other operator
        sys.stdout.write("===== STARTING RENDERING JOB ({}) =====\n".format(N))

        start_time = time.time()
        while r < N:
            passed_time = time.time()-start_time
            avg_sample_time = passed_time / (r+1)
            # Print progress information
            msg = "Rendering image {} of {}".format(r + 1, N)
            sys.stdout.write("{} [Elapsed: {:.1f}s][Remaining: {:.1f}s]\n".format(msg, passed_time, avg_sample_time * (N-r-1)))
            sys.stdout.flush()

            param_data[r] = self.permute_params(nodes)
            render.filepath = "{}{}{}".format(FILEPATH, r, FILE_EXTENSION)
            ops.render.render(write_still=True)
            r += 1

        # Write param data to file
        with open(FILEPATH + "param_data.json", "w") as f:
            json.dump(param_data, f)

        sys.stdout.write("DONE!\n")
        total_time = time.time() - start_time
        sys.stdout.write("Total Time: {:.1f}s [Avg per render: {:.2f}]".format(total_time, total_time / (N)))

        return {"FINISHED"}
