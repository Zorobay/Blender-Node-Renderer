import bpy
import json

from bpy_extras.io_utils import ImportHelper
from npr.src.misc.sockets import find_socket_by_id, input_value_to_json

KEY_ENABLED = "enabled"
KEY_USER_PARAMS = "user_params"
KEY_DEFAULT_PARAMS = "default_params"
KEY_MAX = "user_max"
KEY_MIN = "user_min"
KEY_NAME = "name"

global loaded_param_setup
loaded_param_setup = None


def node_params_to_json(nodes) -> dict:
    """Extract user set min and max value of node parameters (inputs) and returns them in a dictionary.
    
    Arguments:
        nodes - a collection of a material's nodes
    
    Returns:
        dict -- a dictionary with parameter values
    """
    data = {}
    for n in nodes:
        if n.type == "FRAME":
            continue

        data[n.name] = {
            KEY_ENABLED: n.node_enabled,
            KEY_USER_PARAMS: {},
            KEY_DEFAULT_PARAMS: {},
        }

        for i in n.inputs:
            if i.is_linked:
                continue

            # Store default value
            try:
                data[n.name][KEY_DEFAULT_PARAMS][i.identifier] = input_value_to_json(i)
            except (AttributeError, KeyError):
                pass

            # Store user data
            try:
                props = i.user_props
                if i.type == "VECTOR":
                    u_min = list(props.user_min)
                    u_max = list(props.user_max)
                else:
                    u_min = props.user_min
                    u_max = props.user_max

                input_data = {
                    KEY_ENABLED: i.input_enabled,
                    KEY_MIN: u_min,
                    KEY_MAX: u_max,
                }
            except AttributeError:
                input_data = {
                    KEY_ENABLED: i.input_enabled,
                }

            data[n.name][KEY_USER_PARAMS][i.identifier] = {
                KEY_NAME: i.name,
                KEY_USER_PARAMS: input_data,
            }

    return data


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
