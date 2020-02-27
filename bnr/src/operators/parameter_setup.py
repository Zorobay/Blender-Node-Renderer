import json

import bpy
from bpy_extras.io_utils import ImportHelper

from bnr.src.misc.parameters import find_socket_by_id, set_input_enabled, get_input_init_status
from bnr.src.misc.nodes import get_node_init_status
from bnr.src.misc.to_json import input_value_to_json, node_params_to_json
from bnr.src.misc.to_json import (KEY_DEFAULT_PARAMS, KEY_ENABLED, KEY_MAX, KEY_MIN, KEY_NAME, KEY_USER_PARAMS)


def set_param_value_from_json(node, input_id, input_data):
    input = find_socket_by_id(node.inputs, input_id)
    if input.bl_idname == "NodeSocketVectorEuler":
        input.default_value = input_data[:3]
        input.default_value.order = input_data[3]
    else:
        input.default_value = input_data

def load_default_parameters(json_data:dict, nodes):
    for node_name, node_data in json_data.items():
        node = nodes.get(node_name)

        for input_id, input_data in node_data[KEY_DEFAULT_PARAMS].items():
            set_param_value_from_json(node, input_id, input_data)


class NODE_EDITOR_OP_LoadDefaultParameters(bpy.types.Operator):
    bl_idname = "node.load_default_parameters"
    bl_label = "Load Default Parameters"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Sets the parameters of the selected material to the loaded default values"
    )

    @classmethod
    def poll(cls, context):
        props = context.scene.internal_props
        return len(props.parameter_setup_filepath) > 0 and context.material

    def execute(self, context):
        nodes = context.material.node_tree.nodes
        props = context.scene.internal_props

        with open(props.parameter_setup_filepath, "r") as f:
            data = json.load(f)
            load_default_parameters(data, nodes)

        return {"FINISHED"}


class NODE_EDITOR_OP_LoadParameterSetup(bpy.types.Operator, ImportHelper):
    bl_idname = "node.load_parameter_setup"
    bl_label = "Load Parameter Setup"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Operator that allows the user to load a JSON file with previously save parameter setup for the users set min and max values for inputs of nodes, as well as the parameter values of the currently selected material"

    # The filepath selected by the file dialog will be automatically written to this property
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    # Filter files with only .json extension
    filter_glob: bpy.props.StringProperty(
        default="*.json", options={"HIDDEN"}, maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return context.material is not None and context.scene.internal_props.nodes_loaded

    def execute(self, context):
        nodes = context.material.node_tree.nodes
        props = context.scene.internal_props
        data = {}

        with open(self.filepath, "r") as f:
            data = json.load(f)
            props.parameter_setup_filepath = self.filepath

            for node_name, node_data in data.items():
                try:
                    node = nodes.get(node_name)
                    node.node_enabled = node_data[KEY_ENABLED]
                    node.node_show = get_node_init_status(node)

                    for input_id, input_data in node_data[KEY_DEFAULT_PARAMS].items():
                        set_param_value_from_json(node, input_id, input_data)

                    for input_id, input_data in node_data[KEY_USER_PARAMS].items():
                        input_data = input_data[KEY_USER_PARAMS]
                        input = find_socket_by_id(node.inputs, input_id)

                        set_input_enabled(input, input_data[KEY_ENABLED])
                        input.input_show = get_input_init_status(input)

                        i_min = input_data[KEY_MIN]
                        i_max = input_data[KEY_MAX]
                        try:
                            input.user_props.user_min = i_min
                            input.user_props.user_max = i_max
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
    filter_glob: bpy.props.StringProperty(
        default="*.json", options={"HIDDEN"}, maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return context.material is not None and context.scene.internal_props.nodes_loaded
        

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
