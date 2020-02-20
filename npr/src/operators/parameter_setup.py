import json

import bpy
from bpy_extras.io_utils import ImportHelper

from npr.src.misc.parameters import find_socket_by_id
from npr.src.misc.to_json import input_value_to_json, node_params_to_json
from npr.src.misc.to_json import (KEY_DEFAULT_PARAMS, KEY_ENABLED, KEY_MAX, KEY_MIN, KEY_NAME, KEY_USER_PARAMS)


global loaded_param_setup
loaded_param_setup = None


def set_param_value_from_json(node, input_id, input_data):
    inp = find_socket_by_id(node.inputs, input_id)
    if inp.bl_idname == "NodeSocketVectorEuler":
        inp.default_value = input_data[:3]
        inp.default_value.order = input_data[3]
    else:
        inp.default_value = input_data


class NODE_EDITOR_OP_LoadDefaultParameters(bpy.types.Operator):
    bl_idname = "node.load_default_parameters"
    bl_label = "Load Default Parameters"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Sets the parameters of the selected material to the loaded default values"
    )

    @classmethod
    def poll(cls, context):
        return loaded_param_setup and context.material

    def execute(self, context):
        nodes = context.material.node_tree.nodes

        for node_name, node_data in loaded_param_setup.items():
            node = nodes.get(node_name)

            for input_id, input_data in node_data[KEY_DEFAULT_PARAMS].items():
                set_param_value_from_json(node, input_id, input_data)

        return {"FINISHED"}


class NODE_EDITOR_OP_LoadParameterSetup(bpy.types.Operator, ImportHelper):
    bl_idname = "node.load_parameter_setup"
    bl_label = "Load Parameter Setup"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Operator that allows the user to load a JSON file with previously save parameter setup for the users set min and max values for inputs of nodes, as well as the parameter values of the currently selected material"

    # The filepath selected by the file dialog will be automatically written to this property
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    # Filter files with only .json extension
    filter_glob = bpy.props.StringProperty(
        default="*.json", options={"HIDDEN"}, maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return (
                context.material is not None and context.scene.internal_props.nodes_loaded
        )

    def execute(self, context):
        nodes = context.material.node_tree.nodes
        data = {}

        with open(self.filepath, "r") as f:
            data = json.load(f)
            global loaded_param_setup
            loaded_param_setup = data

            for node_name, node_data in data.items():
                try:
                    node = nodes.get(node_name)
                    node.node_enabled = node_data[KEY_ENABLED]

                    for input_id, input_data in node_data[KEY_DEFAULT_PARAMS].items():
                        set_param_value_from_json(node, input_id, input_data)

                    for input_id, input_data in node_data[KEY_USER_PARAMS].items():
                        input_data = input_data[KEY_USER_PARAMS]
                        inp = find_socket_by_id(node.inputs, input_id)
                        inp.input_enabled = input_data[KEY_ENABLED]
                        i_min = input_data[KEY_MIN]
                        i_max = input_data[KEY_MAX]
                        try:
                            inp.user_props.user_min = i_min
                            inp.user_props.user_max = i_max
                        except (AttributeError, KeyError):
                            pass
                        except ValueError as e:
                            print(
                                "Could not assign min and max value for node {}, input {}. \n Error: {}".format(
                                    node_name, input_id, e
                                )
                            )
                except (AttributeError, KeyError) as e:
                    print(e)  # Catch all errors and try to load as much as possible

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class NODE_EDITOR_OP_SaveParameterSetup(bpy.types.Operator, ImportHelper):
    bl_idname = "node.save_parameter_setup"
    bl_label = "Save Parameter Setup"
    bl_options = {"REGISTER"}
    bl_description = "Open a file dialog to save the users set min and max value for inputs of nodes, as well as current values of all parameters of the selected material, to a JSON file"

    # The filepath selected by the file dialog will be automatically written to this property
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    # Filter files with only .json extension
    filter_glob = bpy.props.StringProperty(
        default="*.json", options={"HIDDEN"}, maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return (
                context.material is not None and context.scene.internal_props.nodes_loaded
        )

    def execute(self, context):
        nodes = context.material.node_tree.nodes
        data = node_params_to_json(nodes)

        with open(self.filepath, "w") as f:
            json.dump(data, f)

        return {"FINISHED"}

    def invoke(self, context, event):
        name = context.material.name
        self.filepath = name + "_parameter_setup.json"  # Set default filename
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
