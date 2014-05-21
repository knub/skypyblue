import pygame, math

p1 = [250, 100]
p2 = [600, 400]
p3 = [200, 400]

all_points = [p1,p2,p3]

WHITE = (255,255,255)
BLACK = (0,0,0)

LAST_MOUSE_POS = None
CURRENT_POINT = None

def main():
  pygame.init()
  surface = pygame.display.set_mode((800, 600))
  pygame.display.set_caption("Pygame-Tutorial: Grundlagen")
  pygame.mouse.set_visible(1)
  pygame.key.set_repeat(1, 30)
  clock = pygame.time.Clock()
  # Die Schleife, und damit unser Spiel, laeuft solange running == True.
  running = 1
  while running:
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
      CURRENT_POINT[0] += delta[0]
      CURRENT_POINT[1] += delta[1]
    LAST_MOUSE_POS = mouse_pos
  elif event.type == pygame.MOUSEBUTTONDOWN: 
    CURRENT_POINT = get_nearest_pt(mouse_pos)
  elif event.type == pygame.MOUSEBUTTONUP: 
    CURRENT_POINT = None

def diff2d(p1, p2):
  return p1[0]-p2[0], p1[1]-p2[1]    

def get_nearest_pt(mouse_pos):
  def diff(p1, p2): 
    dx = p1[0]-p2[0]
    dy = p1[1]-p2[1]
    return math.sqrt(dx*dx+dy*dy)
  diffs = [(diff(mouse_pos, pt), pt) for pt in all_points]
  min_diff = min(diffs, key = lambda x: x[0])
  if min_diff[0] < 10: return min_diff[1]
  return None


def draw_lines(surface):
  pygame.draw.aalines(surface, WHITE, False, all_points)
  for pt in all_points:
    pygame.draw.circle(surface, WHITE, pt, 5)
  pygame.display.update()

if __name__ == '__main__':
  # Unsere Main-Funktion aufrufen.
  main()