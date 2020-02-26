from bpy.props import StringProperty, IntProperty, FloatProperty
from bpy.types import Operator,NodeSocket
from bpy import ops
from bnr.src.misc.to_json import node_params_to_json
from bnr.src.misc.parameters import get_input_enabled, set_input_enabled, is_vector_type
from bnr.src.misc.parameter_transmutator import transmute_params_random

import numpy as np
from PIL import Image
from pathlib import Path
from sklearn.decomposition import PCA

def flatten_image(img_array: np.ndarray):
    """Returns an image array as a flattened row array."""
    return img_array.reshape([1, np.prod(img_array.shape)])

def norm(pc1, pc2, exp_var_rat):
    return sum(abs(pc1-pc2) * exp_var_rat)

def open_image(image_path: str):
    img = np.array(Image.open(image_path)).astype(np.float32) / 255
    if img.shape[2] == 4:
        img = img[:,:,:3]

    return img

class NODE_OP_EliminateParameters(Operator):
    bl_idname = "node.eliminate_parameters"
    bl_label = "Eliminate Parameters"
    bl_options = {"REGISTER"}

    def execute(self, context):
        """Attempts to find parameters that have less than threshold impact on the final renders, and disables them.
        """
        nodes = context.material.node_tree.nodes
        render = context.scene.render
        props = context.scene.pe_props
        parameter_save = node_params_to_json(nodes)
        eliminated = []

        for n in nodes:
            if not n.node_enabled:
                continue

            for i in n.inputs:
                if not get_input_enabled(i):
                    continue
                
                if is_vector_type(i):  # We treat elements of vectory types as separate parameters
                    for i_sub in range(3):
                        props.i_sub = i_sub
                        decision = self._get_decision_for_input(i, nodes, props, render, i_sub=i_sub)
                        if not decision:
                            set_input_enabled(i, False, ind=i_sub)
                            msg = "DISABLED input {} index {} (Node: {}).".format(i.name, i_sub, n.name)
                            print(msg)
                            eliminated.append(msg)
                        else:
                            print("Keeping input {} index {} (Node: {}).".format(i.name, i_sub, n.name))

                else:
                    props.i_sub = -1
                    decision = self._get_decision_for_input(i, nodes, props, render)
                    if not decision:
                        set_input_enabled(i, False)
                        msg = "DISABLED input {} (Node: {}).".format(i.name, n.name)
                        print(msg)
                        eliminated.append(msg)
                    else:
                        print("Keeping input {} (Node: {}).".format(i.name, n.name))

        print("==== Parameter elimination summary ====")
        print("Total parameters eliminated: {}".format(len(eliminated)))
        for e in eliminated:
            print(e)

        # TODO load back the default values...

        return {"FINISHED"}

    def _get_decision_for_input(self, input, nodes, props, render, i_sub=-1):
        if i_sub >= 0:
            umin = input.user_props.user_min[i_sub]
            umax = input.user_props.user_max[i_sub]
        else:
            umin = input.user_props.user_min
            umax = input.user_props.user_max

        possible_values = np.linspace(umin, umax, num=props.N_renders, endpoint=True)

        # Loop L times (as it might have more impact for some parameter randomizations than others)
        for l in range(props.L_loops):
            #image_paths = ops.node.render_over_values(input, possible_values, i_sub=i_sub)
            transmute_params_random(nodes)
            image_paths = self.render_over_values(input, possible_values, props, render, i_sub=i_sub)
            
            base_img = open_image(image_paths[0])
            base_img = flatten_image(base_img)
            image_matrix = base_img

            for p in image_paths[1:]:  # Create image matrix for PCA 
                img = open_image(p)
                img = flatten_image(img)
                image_matrix = np.concatenate((image_matrix, img), axis=0)

            pca = PCA(n_components=props.C_components)
            principal_comps = pca.fit_transform(image_matrix)
            exp_var_rat = pca.explained_variance_ratio_
            if sum(exp_var_rat) < 0.89:
                print("Warning! The total explained variance ratio is below 0.9 ({})!".format(sum(exp_var_rat)))

            base_pcs = principal_comps[0,:]
            max_norm = 0
            for ind, pcs in enumerate(principal_comps[1:]):
                norm_ = norm(base_pcs, pcs, exp_var_rat)
                max_norm = max(max_norm, norm_)
                if norm_ >= props.norm_thresh:
                    print("(loop {}) max norm of {} did reach threshold of {} in image {}".format(l, max_norm, props.norm_thresh, ind+1))
                    return True
            
            print("(loop {}) max norm of {} did not reach threshold of {}".format(l, max_norm, props.norm_thresh))

        return False  # If not enough entropy was reached in any loop, this input can be disabled


    def render_over_values(self, input: NodeSocket, possible_values: list, props, render, i_sub=-1):
        """
        Randomizes all parameters, then renders an image for each value in 'possible_values' for input 'input'.
        
        Returns: 
            A list of image paths to renders
        """
        image_paths = []
        render_tmp_output = Path(props.render_tmp_output)

        # Render N images, iterating through possible parameter values
        for ren in range(props.N_renders):
            if i_sub >= 0:
                input.default_value[i_sub] = float(possible_values[ren])
            else:
                input.default_value = possible_values[ren]

            path = str(render_tmp_output / "{}.png".format(ren))
            image_paths.append(path)
            render.filepath = path
            ops.render.render(write_still=True)

        return image_paths