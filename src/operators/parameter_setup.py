import bpy
import json

from bpy_extras.io_utils import ImportHelper

KEY_ENABLED = "enabled"
KEY_PARAMS = "parameters"
KEY_MAX = "user_max"
KEY_MIN = "user_min"

def node_params_default_vaulues_to_json(nodes) -> dict:
    data = {}
    for n in nodes:
        data[n.name] = {}

        for i in n.inputs:

            if i.is_linked:
                continue

            try:
                data[n.name][i.name] = i.default_value
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

            data[n.name][KEY_PARAMS][i.name] = input_data

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
                node = nodes.get(node_name)
                node.node_enable = node_data[KEY_ENABLED]

                for input_name, input_data in node_data[KEY_PARAMS].items():
                    input = node.inputs.get(input_name)
                    input.input_enable = input_data[KEY_ENABLED]

                    try:
                        input.user_props.user_min = input_data[KEY_MIN]
                        input.user_props.user_max = input_data[KEY_MAX]
                    except KeyError:
                        pass  # If data about user_min or user_max was not stored, don't bother.
                pass


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
