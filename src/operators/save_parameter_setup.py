import bpy
import json

from bpy_extras.io_utils import ImportHelper

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
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,
            )

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def execute(self, context):
        nodes = context.material.node_tree.nodes
        data = {}

        for n in nodes:
            data[n.name] = {"enabled": n.node_enable, "parameters": {}}

            for i in n.inputs:
                try:
                    props = i.user_props
                    input_data = {
                        "enabled": i.input_enable,
                        "min": props.user_min,
                        "max": props.user_max
                    }
                except AttributeError:
                    input_data = {
                        "enabled": i.input_enable,
                    }

                data[n.name]["parameters"][i.name] = input_data 

                

        with open(self.filepath, "w") as f:
            json.dump(data, f)

        return {"FINISHED"}

    def invoke(self, context, event):
        name = context.material.name
        self.filepath = name + "_parameter_setup.json"  # Set default filename
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
