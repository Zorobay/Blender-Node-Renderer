from bpy import ops
from bnr.src.misc.to_json import node_params_to_json
from bnr.src.misc.parameters import set_random_value_for_input
from bnr.src.misc.parameter_transmutator import transmute_params_random

import numpy as np
from PIL import Image
from pathlib import Path

class ParameterEliminator:

    def __init__(self, nodes, render_engine):
        self._nodes = nodes
        self._RE = render_engine

    def eliminate_parameters(self, thresh):
        """Attempts to find parameters that have less than threshold impact on the final renders, and disables them.
        """
        RENDER_TMP_OUTPUT = Path("/tmp/")
        parameter_save = node_params_to_json(self._nodes)
        N_renders = 5
        L_loops = 4

        for n in self._nodes:
            if not n.node_enabled:
                continue

            for i in n.inputs:
                if not i.input_enabled:
                    continue

                # Loop L times (as it might have more impact for other parameter randomizations)
                for loop in range(L_loops):
                    # Randomize all parameters
                    transmute_params_random(self._nodes)

                    image_paths = []
                    # Render N images, randomizing only parameter i
                    for ren in range(N_renders):
                        path = str(RENDER_TMP_OUTPUT / "{}.png".format(ren))
                        image_paths.append(path)
                        self._RE.filepath = path
                        ops.render.render(write_still=True)
                        set_random_value_for_input(i)

                    base_img = np.array(Image.open(image_paths[0]))
                    total_diff = 0
                    for p in image_paths[1:]:
                        img = np.array(Image.open(p))
                        abs_diff = abs(base_img-img)
                        abs_diff.dtype = np.int8  
                        sum_diff = np.sum(abs_diff)
                        total_diff += sum_diff

                