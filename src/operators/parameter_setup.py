import bpy
import json

from bpy_extras.io_utils import ImportHelper

KEY_ENABLED = "enabled"
KEY_PARAMS = "parameters"
KEY_MAX = "user_max"
KEY_MIN = "user_min"
KEY_NAME = "name"

def find_input_by_id(inputs, id: str):
    """Finds an input among a collection of inputs based on its unique identifier, and not its name.
    
    returns:
        The NodeSocket object with the specifier identifier. Returns None if not found.
    """

    for i in inputs:
        if i.identifier == id:
            return i

    return None
    

def node_params_default_vaulues_to_json(nodes) -> dict:
    data = {}
    for n in nodes:
        data[n.name] = {}

        for i in n.inputs:

            if i.is_linked:
                continue

            try:
                data[n.name][i.identifier] = i.default_value
            except KeyError:
                pass


def node_params_to_json(nodes) -> dict:
    """Extract user set min and max value of node parameters (inputs) and returns them in a dictionary.
    
    Arguments:
        nodes - a collection of a material's nodes
    
    Returns:
        dict -- a dictionary with parameter values
    """
    data = {}
    for n in nodes:
        data[n.name] = {KEY_ENABLED: n.node_enable, KEY_PARAMS: {}}

        for i in n.inputs:
            try:
                props = i.user_props
                if i.type == "VECTOR":
                    u_min = list(props.user_min)
                    u_max = list(props.user_max)
                else:
                    u_min = props.user_min
                    u_max = props.user_max
                    
                input_data = {
                    KEY_ENABLED: i.input_enable,
                    KEY_MIN: u_min,
                    KEY_MAX: u_max
                }
            except AttributeError:
                input_data = {
                    KEY_ENABLED: i.input_enable,
                }

            data[n.name][KEY_PARAMS][i.identifier] = {KEY_NAME: i.name, KEY_PARAMS: input_data}

    return data


class NODE_EDITOR_OP_LoadParameterSetup(bpy.types.Operator, ImportHelper):
    """Operator that allows the user to load a JSON file with previously save parameter setup for
     the users set min and max values for inputs of nodes.

    """

    bl_idname = "node.load_parameter_setup"
    bl_label = "Load Parameter Setup"
    bl_options = {"REGISTER"}

    # The filepath selected by the file dialog will be automatically written to this property
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    # Filter files with only .json extension
    filter_glob = bpy.props.StringProperty(
        default="*.json", options={"HIDDEN"}, maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def execute(self, context):
        nodes = context.material.node_tree.nodes
        data = {}

        with open(self.filepath, "r") as f:
            data = json.load(f)

            for node_name, node_data in data.items():
                try:
                    node = nodes.get(node_name)
                    node.node_enable = node_data[KEY_ENABLED]

                    for input_id, input_data in node_data[KEY_PARAMS].items():
                        input_data = input_data[KEY_PARAMS]
                        input = find_input_by_id(node.inputs, input_id)
                        input.input_enable = input_data[KEY_ENABLED]
                        i_min = input_data[KEY_MIN]
                        i_max = input_data[KEY_MAX]
                        try:
                            input.user_props.user_min = i_min
                            input.user_props.user_max = i_max
                        except (AttributeError, KeyError):
                            pass
                        except ValueError as e:
                            print("Could not assign min and max value for node {}, input {}. \n Error: {}".format(node_name, input_id, e))
                except (AttributeError, KeyError) as e:
                    print("Node:{}, Input:{}  -  {}".format(node_name, input_id, e))  # Catch all errors and try to load as much as possible


        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class NODE_EDITOR_OP_SaveParameterSetup(bpy.types.Operator, ImportHelper):
    """Operator that allows the user to open a file dialog and 
    save the users set min and max value for inputs of nodes to a JSON file.
    
    """

    bl_idname = "node.save_parameter_setup"
    bl_label = "Save Parameter Setup"
    bl_options = {"REGISTER"}

    # The filepath selected by the file dialog will be automatically written to this property
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    # Filter files with only .json extension
    filter_glob = bpy.props.StringProperty(
        default="*.json", options={"HIDDEN"}, maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return context.material is not None

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
