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

import npr
from npr.src.misc.sockets import input_value_to_json, find_number_of_enabled_sockets, node_params_min_max_to_json, normalize, list_
from npr.src.misc.time import seconds_to_complete_time

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
    links.new(
        node_world_output.inputs["Surface"], node_background.outputs["Background"]
    )
    links.new(node_background.inputs["Color"], node_texture_env.outputs["Color"])
    links.new(node_texture_env.inputs["Vector"], node_mapping.outputs["Vector"])
    links.new(node_mapping.inputs["Vector"], node_texture_coord.outputs["Generated"])

    # Set node values
    node_background.inputs["Strength"].default_value = 1.0
    world_node_tree.nodes["Environment Texture"].image = bpy.data.images.load(HDRI_PATH)


def permute_params_consecutive(nodes, r, N, P):
    """This permutation strategy permutes all parameters consecutively until exhausted, therefore, for any image, only one parameter will have changed.
    A parameter will not start permutating until the previous is done permutating.

    Arguments:
        nodes --
        r -- The current sample number
        N -- The total number of samples
        P -- The total number of parameters
    """

    samples_per_param = int(N / P)
    i_node = 0
    i_input = 0


def permute_params_random(nodes):
    """Permutes the parameters of all node inputs

    Arguments:
        nodes -- The node group containing all nodes

    Returns:
        A dictionary file with the new parameters.
    """

    params = {}
    normalized_lbl = []

    for n in nodes:
        params[n.name] = {}

        for i in n.inputs:
            try:
                # Get properties of the default value
                def_val_prop = i.bl_rna.properties["default_value"]

                if i.input_enabled and n.node_enabled:  # Only permute parameters if enabled
                    umin = i.user_props.user_min
                    umax = i.user_props.user_max

                    if i.type == "RGBA":
                        val = [
                            random.randint(umin, umax),
                            random.randint(umin, umax),
                            random.randint(umin, umax),
                            1.0,
                        ]
                        i.default_value = val


                    elif i.bl_idname.startswith("NodeSocketVector"):
                        val = [
                            random.uniform(umin.x, umax.x),
                            random.uniform(umin.y, umax.y),
                            random.uniform(umin.z, umax.z),
                        ]
                        i.default_value = val
                    elif def_val_prop.type == "FLOAT":
                        val = random.uniform(umin, umax)
                        i.default_value = val
                        val = [val]
                    else:
                        print(i.type)

                    umin = list_(umin)
                    umax = list_(umax)
                    for x in range(len(val)):
                        normalized_lbl.append(normalize(val[x], umin[x], umax[x]))

                if (
                        not i.is_linked
                ):  # Save parameter unless it is linked (even if it wasn't permuted)
                    params[n.name][i.identifier] = input_value_to_json(i)

            except AttributeError as e:
                pass
            except KeyError:
                pass

    return params, normalized_lbl


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
        FILEPATH = FILEPATH[0: FILEPATH.rfind("\\") + 1]
        FILE_EXTENSION = render.file_extension
        N = all_props.render_amount
        NUM_PARAMS = find_number_of_enabled_sockets(nodes)
        PERMUTATION_STRATEGY = context.scene.props.permutation_strategy
        param_data = {}
        data_labels = []
        r = 0

        # Save parameter mins and maxes (so that we can normalize them later)
        FILENAME = "param_min_max.json"
        with open(FILEPATH + FILENAME, "w") as f:
            data = node_params_min_max_to_json(nodes)
            json.dump(data, f)

        sys.stdout.write("===== STARTING RENDERING JOB ({}) =====\n".format(N))

        start_time = time.time()
        # renderer = Renderer(nodes, N, NUM_PARAMS)

        while r < N:
            pd, rl = permute_params_random(nodes)
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


class Renderer:
    def __init__(self, nodes, N, P):
        """
        Arguments:
            N -- The total number of samples
            P -- The total number of parameters
        """
        self.nodes = nodes
        self.N = N
        self.P = P
        self.SPP = int(self.N / self.P)  # Total number of samples per parameter
        self.EXCESS = max(
            0, self.N - (self.SPP * self.P)
        )  # The number of parameters that can be allowed to render 1 more sample (for consecutive)
        self.excess_r = 0  # The number of parameters that have been rendered 'excessively' (SPP + 1)
        self.current_param_r = 0
        self._current_param_max_r = self.SPP + (
            1 if self.EXCESS > 0 else 0)  # This is used to calculate the number of steps we can increase the parameter value
        self.current_param_i = 0  # Index of the current parameter
        self.current_node_i = 0  # Index of the current node
        self.ENABLED_NODES = [n for n in self.nodes if n.node_enabled]
        self.current_node = self.ENABLED_NODES[0]
        self._enabled_params = self._get_enabled_params()
        self.current_param = self._enabled_params[0]
        self.current_default_value = copy.copy(self.current_param.default_value)

    def _get_enabled_params(self):
        return [i for i in self.current_node.inputs if i.input_enabled]

    def _set_next_node_and_param(self):
        self.current_param_i += 1

        if self.current_param_i >= len(self._enabled_params):
            self.current_node_i += 1
            if self.current_node_i >= len(self.ENABLED_NODES):
                return
            self.current_param_i = 0
            self.current_node = self.ENABLED_NODES[self.current_node_i]
            self._enabled_params = self._get_enabled_params()

        self.current_param = self._enabled_params[self.current_param_i]
        self.current_default_value = copy.copy(self.current_param.default_value)

    def _get_color_range(self, center, radius):
        """Returns a possible color value range, shifted from center by radius."""
        _max = center + radius
        _min = center - radius
        if _max > 1.0:
            diff = 1.0 - _max
            _max = -diff
            _min + diff
        elif _min < 0.0:
            _max -= _min
            _min = 0.0

        return (_min, _max)

    def _get_next_default_value(self, umin, umax, r, rmax, input_type):
        rmax -= 1  # Need to divide by one less to cover all values from min to max
        if input_type in ("RGBA", "VECTOR"):
            val = [n + r * ((x - n) / rmax) for (x, n) in zip(umin, umax)]
            if input_type == "RGBA":
                val.append(1.0)
        elif input_type == "INT":
            val = round(umin + r * ((umax - umin) / rmax))
        else:
            val = umin + r * ((umax - umin) / rmax)

        return val

    def permute_params_consecutive(self, r):
        """This permutation strategy permutes all parameters consecutively until exhausted, therefore, for any image, only one parameter will have changed.
        A parameter will not start permutating until the previous is done permutating.

        Arguments:
            nodes --
            r -- The current sample number
        """
        def_val = self.current_param.bl_rna.properties["default_value"]
        input_type = self.current_param.type

        if input_type == "RGBA":
            c = Color(self.current_param.default_value[:3])
            var = 0.1
            (umin, umax) = [self._get_color_range(c, var) for c in c.hsv]
        else:
            umin = self.current_param.user_props.user_min
            umax = self.current_param.user_props.user_max

        self.current_param.default_value = self._get_next_default_value(umin, umax, r, self._current_param_max_r, input_type)

        # Check if we're done with this input
        self.current_param_r += 1
        if self.current_param_r > self._current_param_max_r:
            if self._current_param_max_r > self.SPP:
                self.excess_r += 1
            else:
                self.current_param_r = 0
                # Reset this parameter to default
                self.current_param.default_value = self.current_default_value
                self._current_param_max_r = self.SPP + 1 if self.excess_r < self.EXCESS else self.SPP

                self._set_next_node_and_param()

        params = {}
        # Save values for all parameters
        for n in self.nodes:
            params[n.name] = {}
            for i in n.inputs:
                if not i.is_linked:
                    try:
                        params[n.name][i.identifier] = input_value_to_json(i)
                    except KeyError:
                        pass
        return params
