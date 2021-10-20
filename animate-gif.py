import io

import pygame
from PIL import Image
from collections.abc import Iterable
from itertools import cycle

# Window size
from pygame import KEYDOWN, K_UP, K_SPACE, K_ESCAPE, KEYUP, K_DOWN, K_KP_PLUS, K_KP_MINUS
from sprite import AISprite

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1200
WINDOW_SURFACE = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE

DARK_BLUE = (3, 5, 54)


# class MultiFrameSprite(pygame.sprite.Sprite):
#     def __init__(self, fps: int, frames: Iterable[pygame.Surface], loop: bool = False):
#         if fps <= 0:
#             raise ValueError('Frame rate must be a positive integer.')
#
#         super(MultiFrameSprite, self).__init__()
#         self.fps = fps
#
#         # Load all the specified animation frames
#         self.frames = cycle(frames) if loop else frames
#         try:
#             # Start the animation at the first frame
#             self.image = next(self.frames)
#         except StopIteration:
#             raise ValueError('Frames cannot be empty.')
#         # Set centroid to the center of the screen
#         self.rect = self.image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
#
#         # Frame handling
#         self.frame_duration_millisec = 1000 // fps  # inter-frame delay in milliseconds
#         self.prev_frame_at = 0
#
#     def update(self):
#         # If enough time has passed since previous frame, advance to next frame
#         if (time_now := pygame.time.get_ticks()) > self.prev_frame_at + self.frame_duration_millisec:
#             self.prev_frame_at = time_now
#
#             # Preserve the centroid in case the frames are differing sizes
#             center = self.rect.center
#
#             try:
#                 # Advance to next frame
#                 self.image = next(self.frames)
#             except StopIteration:
#                 # Animation over
#                 pass
#             else:
#                 # Get new rectangle and restore centroid coordinates
#                 self.rect = self.image.get_rect(center=center)
#
#     def speed_up(self):
#         self.frame_duration_millisec = int(1000 / (self.fps * 3))
#
#     def speed_normal(self):
#         self.frame_duration_millisec = 1000 // self.fps
#
#     def speed_down(self):
#         self.frame_duration_millisec = int(1000 / (self.fps * 0.4))


def iter_frames(img: Image):
    i = 0
    while True:
        try:
            img.seek(i)
        except EOFError:
            return
        else:
            frame = img.copy()
            # needed?
            if i == 0:
                palette = frame.getpalette()
            else:
                frame.putpalette(palette)
            yield frame
        i += 1


def img_to_surf(img: Image):
    with io.BytesIO() as output:
        img.save(output, format="png")
        output.seek(0)
        return pygame.image.load(output).convert_alpha()


fps = 60
background_colour = (25, 12, 64)

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
all_groups = pygame.sprite.Group()

frames = iter_frames(Image.open('ai-ui/circular-4-squared.gif'))
ai = AISprite(fps=30, frames=(img_to_surf(img) for img in frames), loop=True)
ai.add(all_groups)
ai.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        # For development only. Animation commands should replaced with more abstract state commands for deployment
        if event.type == KEYDOWN:
            if event.key == K_UP:
                ai.speed_up()
            if event.key == K_DOWN:
                ai.speed_down()
            if event.key == K_KP_PLUS:
                ai.zoom_in()
                # ai.zoom(scale=0.7, seconds=0.5)
            if event.key == K_KP_MINUS:
                ai.zoom_out()

        if event.type == KEYUP:
            if event.key == K_UP:
                ai.speed_normal()
            if event.key == K_DOWN:
                ai.speed_normal()
            if event.key == K_KP_PLUS:
                ai.zoom_reset()
            if event.key == K_KP_MINUS:
                ai.zoom_reset()

    screen.fill(background_colour)
    all_groups.draw(screen)

    all_groups.update()
    pygame.display.update()

    clock.tick(60)
pygame.exit()
