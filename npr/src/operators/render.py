import bpy
import copy
import json
import random
import sys
import time
import csv
from bpy import ops
from bpy.types import Operator
from mathutils import Color
from pathlib import Path
import statistics as st

import npr
from npr.src.misc.parameters import find_number_of_enabled_sockets, set_random_value_for_input
from npr.src.misc.to_json import input_value_to_json, node_params_min_max_to_json, node_params_to_json
from npr.src.misc.misc import normalize, list_
from npr.src.misc.time import seconds_to_complete_time
from npr.src.misc.parameter_transmutator import transmute_params_random

SCENE_NAME = "RENDER_SCENE_TMP"
HDRI_FILE = "sunflowers_2k.hdr"
HDRI_PATH = str(Path(npr.__file__).parent / "res" / HDRI_FILE)

from npr.src.parameter_eliminator.parameter_eliminator import ParameterEliminator


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
    links.new(
        node_world_output.inputs["Surface"], node_background.outputs["Background"]
    )
    links.new(node_background.inputs["Color"], node_texture_env.outputs["Color"])
    links.new(node_texture_env.inputs["Vector"], node_mapping.outputs["Vector"])
    links.new(node_mapping.inputs["Vector"], node_texture_coord.outputs["Generated"])

    # Set node values
    node_background.inputs["Strength"].default_value = 1.0
    world_node_tree.nodes["Environment Texture"].image = bpy.data.images.load(HDRI_PATH)


class NODE_OP_Render(Operator):
    bl_idname = "node.render"
    bl_label = "Render"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.material and context.scene.internal_props.nodes_loaded and context.scene.props.render_output_dir != ""

    def execute(self, context):
        all_props = context.scene.props

        # Make a full copy of the current scene and only manipulate that one
        if all_props.use_standard_setup:
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
        nodes = material.node_tree.nodes

        if all_props.use_standard_setup:
            # Delete unneeded objects
            obs_to_del = [o for o in objs if o.type in ("MESH", "LIGHT", "CAMERA")]
            ops.object.delete({"selected_objects": obs_to_del})

            # Add plane and apply material
            ops.mesh.primitive_plane_add(
                size=2, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0)
            )
            plane = context.selected_objects[0]
            plane.data.materials.append(material)

            # Setup HDRI
            setup_HDRI_for_world(context)

            # Setup camera placement
            ops.object.camera_add(rotation=(0, 0, 0), location=(0, 0, 2))
            context.selected_objects[0].name = "Rendering Camera"
            context.scene.camera = context.object

        # Setup renderer
        render.resolution_x = all_props.x_res
        render.resolution_y = all_props.y_res
        render.resolution_percentage = 100
        render.engine = "CYCLES"
        context.scene.cycles.device = "GPU"
        context.scene.cycles.feature_set = "SUPPORTED"
        context.scene.cycles.samples = 200

        # Initialize render variables
        FILEPATH = all_props.render_output_dir
        FILE_EXTENSION = render.file_extension
        N = all_props.render_amount
        param_data = {}
        data_labels = []
        r = 0

        # ==== Eliminate parameters automatically ====
        pe = ParameterEliminator(nodes, render)
        pe.eliminate_parameters(thresh=0.1)

        # Save parameter mins and maxes (so that we can normalize them later)
        FILENAME = "param_min_max.json"
        with open(FILEPATH + FILENAME, "w") as f:
            data = node_params_min_max_to_json(nodes)
            json.dump(data, f)

        sys.stdout.write("===== STARTING RENDERING JOB ({}) =====\n".format(N))

        start_time = time.time()
        # renderer = Renderer(nodes, N, NUM_PARAMS)

        while r < N:
            pd, rl = transmute_params_random(nodes)
            param_data[r] = pd
            data_labels.append(rl)

            render.filepath = "{}{}{}".format(FILEPATH, r, FILE_EXTENSION)
            ops.render.render(write_still=True)
            r += 1

            # Print progress information
            passed_time = time.time() - start_time
            avg_sample_time = "{}h {}m {:.2f}s".format(*seconds_to_complete_time((passed_time / r) * (N - r)))
            passed_time = "{}h {}m {:.2f}".format(*seconds_to_complete_time(passed_time))
            msg = "Rendered image {} of {}".format(r, N)
            sys.stdout.write(
                "{} [Elapsed: {}][Remaining: {}]\n".format(
                    msg, passed_time, avg_sample_time
                )
            )
            sys.stdout.flush()

        # Write param data to file
        FILENAME = "param_data.json"
        with open(FILEPATH + FILENAME, "w") as f:
            json.dump(param_data, f)
            sys.stdout.write(
                "Wrote parameter data to: {}\n".format(FILEPATH + FILENAME)
            )

        FILENAME = "normalized_data_labels.csv"
        with open(FILEPATH + FILENAME, "w", newline="") as f:
            w = csv.writer(f, delimiter=",")
            w.writerows(data_labels)
            sys.stdout.write("Wrote labels to: {}\n".format(FILEPATH + FILENAME))

        total_time = time.time() - start_time
        sys.stdout.write(
            "Total Time: {:.1f}s [Avg per render: {:.3f}s]".format(
                total_time, total_time / (N)
            )
        )

        return {"FINISHED"}
