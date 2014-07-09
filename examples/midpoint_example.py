import pygame, math, sys
sys.path.append("../src")
sys.path.append("../tests")

from skypyblue.core import ConstraintSystem
from skypyblue.models import *
from point import Point

from point import Point

cs = ConstraintSystem()
pm_var = Variable("pm", Point(600, 400), cs)
p1_var = Variable("p1", Point(250, 100), cs)
p2_var = Variable("p2", Point(200, 400), cs)
p3_var = Variable("p1", Point(100, 150), cs)
p4_var = Variable("p2", Point(100, 250), cs)


def all_points():
  return [p1_var, pm_var, p2_var, p3_var, p4_var]

def main_line():
  return [p1_var, pm_var, p2_var]

def direction_line():
  return [p3_var, p4_var]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)



LAST_MOUSE_POS = None
CURRENT_POINT = None

def length(p1, p2):
  dx = p1[0] - p2[0]
  dy = p1[1] - p2[1]
  return math.sqrt(dx * dx + dy * dy)


def main():
  pygame.init()
  surface = pygame.display.set_mode((800, 600))
  pygame.display.set_caption("Constraint-based-Programming: Midpoint Example")
  pygame.mouse.set_visible(1)
  pygame.key.set_repeat(1, 30)
  clock = pygame.time.Clock()
  # Die Schleife, und damit unser Spiel, laeuft solange running == True.
  running = 1
  c = 0
  while running:
    c = (c + 1) % 50
    # Framerate auf 30 Frames pro Sekunde beschraenken.
    # Pygame wartet, falls das Programm schneller laeuft.
    clock.tick(30)

    # surface mit Schwarz (RGB = 0, 0, 0) fuellen.
    surface.fill(BLACK)
    for event in pygame.event.get():
      # Spiel beenden, wenn wir ein QUIT-Event finden.
      if event.type == pygame.QUIT: running = False
      quit_on_escape(event)
      handle_mouse_event(event)
    pygame.display.flip()
    if c != 0:
      draw_lines(surface)

def quit_on_escape(event):
  if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
    # Wenn Escape gedrueckt wird, posten wir ein QUIT-Event in Pygames Event-Warteschlange.
    pygame.event.post(pygame.event.Event(pygame.QUIT))

def handle_mouse_event(event):
  global LAST_MOUSE_POS, CURRENT_POINT
  mouse_pos = pygame.mouse.get_pos()
  if event.type == pygame.MOUSEMOTION:
    if CURRENT_POINT:
      delta = diff2d(mouse_pos, LAST_MOUSE_POS or mouse_pos)
      CURRENT_POINT.set_value(Point(CURRENT_POINT.get_value().X+delta[0],CURRENT_POINT.get_value().Y+delta[1]))
    LAST_MOUSE_POS = mouse_pos
  elif event.type == pygame.MOUSEBUTTONDOWN:
    CURRENT_POINT = get_nearest_pt(mouse_pos)
  elif event.type == pygame.MOUSEBUTTONUP:
    CURRENT_POINT = None

def diff2d(p1, p2):
  return p1[0] - p2[0], p1[1] - p2[1]

def get_nearest_pt(mouse_pos):
  diffs = [(length(mouse_pos, pt.get_value().to_array()), pt) for pt in all_points()]
  min_diff = min(diffs, key = lambda x: x[0])
  if min_diff[0] < 10: return min_diff[1]
  return None

def draw_line(pts, surface):
  pygame.draw.aalines(surface, WHITE, False, pts)
  for pt in pts:
    pygame.draw.circle(surface, WHITE, pt, 5)
  pygame.display.update()

def draw_lines(surface):
  draw_line([p.get_value().to_array() for p in main_line()], surface)
  draw_line([p.get_value().to_array() for p in direction_line()], surface)

def create_constraints():
  mpmp3p4 = Method([pm_var, p3_var, p4_var], [p1_var, p2_var],
    lambda pm, p3, p4: (
      Point(
        pm.X - (p4.X - p3.X),
        pm.Y - (p4.Y - p3.Y)
      ),
      Point(
        pm.X + (p4.X - p3.X),
        pm.Y + (p4.Y - p3.Y)
      )
    )
  )
  mp1pmp3 = Method([p1_var, pm_var, p3_var], [p2_var, p4_var],
    lambda p1, pm, p3: (
      Point(
        2 * pm.X - p1.X,
        2 * pm.Y - p1.Y
      ),
      Point(
        p3.X + (pm.X - p1.X),
        p3.Y + (pm.Y - p1.Y)
      )
    )
  )
  mpmp2p4 = Method([pm_var, p2_var, p4_var], [p1_var, p3_var],
    lambda pm, p2, p4: (
      Point(
        2 * pm.X - p2.X,
        2 * pm.Y - p2.Y
      ),
      Point(
        p4.X + (pm.X - p2.X),
        p4.Y + (pm.Y - p2.Y)
      )
    )
  )


  constraint = Constraint(
    lambda p1, p2, p3, p4, pm: pm.is_midpoint(p1, p2) and
                         p1.distance(pm) == p3.distance(p4),
    Strength.STRONG,
    [p1_var, p2_var, p3_var, p4_var, pm_var],
    [mpmp3p4, mp1pmp3, mpmp2p4])

  cs.add_constraint(constraint)

  p3_var.stay()
  p4_var.stay()


if __name__ == '__main__':
  create_constraints()
  main()
