class Marker(object):

  def __init__(self):
    super(Marker, self).__init__()
    self.mark = 0

  def new_mark(self):
    self.mark += 1
    return self.mark
