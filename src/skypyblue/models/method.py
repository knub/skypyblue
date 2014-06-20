class Method:
  def __init__(self, in_vars, out_vars, method):
    """
    in_vars:\tlist of (or single object) skypyblue.models.variables.Variable that are handled as input
    out_vars:\tlist of (or single object) skypyblue.models.variables.Variable that are handled as output
    method:\tlamba that fullfils the contraint. the result of the lambda will be assigned to the output variables

    Usage:
      method1 = Method([v1, v2], v3,
        lambda v1, v2: v1+v2)

      method2 = Method([v1, v2], [v3, v4],
        lambda v1, v2: v1+v2, v1-v2)
    """
    self.inputs = in_vars if isinstance(in_vars, list) else [in_vars]
    self.outputs = out_vars if isinstance(out_vars, list) else [out_vars]
    self.method = method
    self.mark = None

  def has_invalid_vars(self):
    for var in self.inputs:
      if not var.valid:
        return True
    return False

  def __str__(self):
    return "<Method %s => %s>" %(self.inputs, self.outputs)

  def __repr__(self):
    return str(self)

  def execute(self):
    out = self.method(*[var.get_value() for var in self.inputs])
    if len(self.outputs) == 1:
      self.outputs[0].set_value(out, triggerChange = False);
    else:
      for i in range(len(self.outputs)):
        self.outputs[i].set_value(out[i], triggerChange = False)
