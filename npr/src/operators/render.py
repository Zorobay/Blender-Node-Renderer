import bpy
import random
import sys
import json
import time
import npr

from bpy.types import Operator
from bpy import ops

from mathutils import Vector
from pathlib import Path


SCENE_NAME = "RENDER_SCENE_TMP"
HDRI_FILE = "sunflowers_2k.hdr"
HDRI_PATH = str(Path(npr.__file__).parent / "res" / HDRI_FILE)


def setup_HDRI_for_world(context):
    world_node_tree = context.scene.world.node_tree
    nodes = world_node_tree.nodes
    links = world_node_tree.links
    x_start = 0
    delta_x = -200

    world_node_tree.nodes.clear()
    context.scene.world.use_nodes = True

    # Create new nodes
    node_world_output = nodes.new(type="ShaderNodeOutputWorld")
    node_background = nodes.new(type="ShaderNodeBackground")
    node_texture_env = nodes.new(type="ShaderNodeTexEnvironment")
    node_mapping = nodes.new(type="ShaderNodeMapping")
    node_texture_coord = nodes.new(type="ShaderNodeTexCoord")

    # Move nodes
    node_world_output.location.x = x_start
    node_background.location.x = node_world_output.location.x + delta_x
    node_texture_env.location.x = node_background.location.x + delta_x
    node_mapping.location.x = node_texture_env.location.x + delta_x
    node_texture_coord.location.x = node_texture_coord.location.x + delta_x

    # Connect nodes
    links.new(node_world_output.inputs["Surface"], node_background.outputs["Background"])
    links.new(node_background.inputs["Color"], node_texture_env.outputs["Color"])
    links.new(node_texture_env.inputs["Vector"], node_mapping.outputs["Vector"])
    links.new(node_mapping.inputs["Vector"], node_texture_coord.outputs["Generated"])

    # Set node values
    node_background.inputs["Strength"].default_value = 1.0
    world_node_tree.nodes["Environment Texture"].image = bpy.data.images.load(HDRI_PATH)

def permute_params(nodes):
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
            if not i.input_enable:
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
                        random.uniform(u_min.z, u_max.z),
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


class NODE_OP_Render(Operator):
    bl_idname = "node.render"
    bl_label = "Render"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.material and context.scene.internal_props.nodes_loaded

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
            pass

        ops.scene.new(type="FULL_COPY")
        context.scene.name = SCENE_NAME

        objs = context.scene.objects
        material = context.material
        render = context.scene.render
        all_props = context.scene.props
        nodes = material.node_tree.nodes

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
            setup_HDRI_for_world(context)

            # Setup camera placement
            ops.object.camera_add(rotation=(0, 0, 0), location=(0, 0, 1.4))
            context.selected_objects[0].name = "Rendering Camera"
            context.scene.camera = context.object

        # Setup renderer
        render.resolution_x = all_props.x_res
        render.resolution_y = all_props.y_res
        render.engine = "CYCLES"
        context.scene.cycles.device = "GPU"
        context.scene.cycles.feature_set = "SUPPORTED"        
        context.scene.cycles.samples = 200

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
            param_data[r] = permute_params(nodes)
            render.filepath = "{}{}{}".format(FILEPATH, r, FILE_EXTENSION)
            ops.render.render(write_still=True)
            r += 1

            # Print progress information
            passed_time = time.time() - start_time
            avg_sample_time = passed_time / (r)
            msg = "Rendered image {} of {}".format(r, N)
            sys.stdout.write(
                "{} [Elapsed: {:.1f}s][Remaining: {:.1f}s]\n".format(
                    msg, passed_time, avg_sample_time * (N - r)
                )
            )
            sys.stdout.flush()


        # Write param data to file
        with open(FILEPATH + "param_data.json", "w") as f:
            json.dump(param_data, f)

        sys.stdout.write("DONE!\n")
        total_time = time.time() - start_time
        sys.stdout.write(
            "Total Time: {:.1f}s [Avg per render: {:.2f}]".format(
                total_time, total_time / (N)
            )
        )

        return {"FINISHED"}
