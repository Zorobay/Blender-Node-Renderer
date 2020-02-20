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