
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
    self.in_vars = in_vars
    self.out_vars = out_vars
    self.method = method
