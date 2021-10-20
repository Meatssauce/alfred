from itertools import cycle
from math import ceil
from typing import Iterable, Tuple, Generic, Any, Sequence

import pygame
# import io
# from PIL import Image
#
#
# def iter_frames(img: Image):
#     i = 0
#     while True:
#         try:
#             img.seek(i)
#         except EOFError:
#             return
#         else:
#             frame = img.copy()
#             # needed?
#             if i == 0:
#                 palette = frame.getpalette()
#             else:
#                 frame.putpalette(palette)
#             yield frame
#         i += 1
#
#
# def img_to_surf(img: Image):
#     with io.BytesIO() as output:
#         img.save(output, format="png")
#         output.seek(0)
#         return pygame.image.load(output).convert_alpha()


class MultiFrameSprite(pygame.sprite.Sprite):
    def __init__(self, fps: int, frames: Iterable[pygame.Surface], loop: bool = False):
        if fps <= 0:
            raise ValueError('Frame rate must be a positive integer.')

        super(MultiFrameSprite, self).__init__()
        self.fps = fps
        self.frame_duration_millisec = 1000 // fps  # inter-frame delay in milliseconds
        self.prev_frame_at = 0

        self.pipe = []

        # Load all the specified animation frames
        self.frames = cycle(frames) if loop else frames
        try:
            # Start the animation at the first frame
            self.image = self.original_image = next(self.frames)
        except StopIteration:
            raise ValueError('Frames cannot be empty.')
        # Set centroid to the center of the screen
        self.rect = self.image.get_rect()

    def update(self):
        # If enough time has passed since previous frame, advance to next frame
        if (time_now := pygame.time.get_ticks()) > self.prev_frame_at + self.frame_duration_millisec:
            self.prev_frame_at = time_now

            # Preserve the centroid in case new frame has different size or coordinates
            center = self.rect.center

            try:
                # Advance to next frame
                self.image = self.original_image = next(self.frames)
            except StopIteration:
                # Animation over
                pass
            else:
                # Animate
                self.animate()

                # Get new rectangle and restore centroid coordinates
                self.rect = self.image.get_rect(center=center)

    def animate(self):
        for frame in self.pipe:
            for func in frame:
                func(self)

    def add_animation(self, sequence: Sequence[Sequence]):
        for existing, new in zip(self.pipe, sequence):
            existing += new

        if len(sequence) > len(self.pipe):
            self.pipe += sequence[len(self.pipe):]

    def zoom(self, scale: float, seconds: float):
        if seconds <= 0:
            raise ValueError('Duration must be a positive real number.')

        pipe = []
        num_frames = int(ceil(seconds * self.fps))
        scale_increment = (scale - 1) / num_frames
        for i in range(1, num_frames + 1):
            intermediary = 1 + scale_increment * i

            def _zoom(self):
                self.image = pygame.transform.smoothscale(self.original_image,
                                                          [intermediary * j for j in self.image.get_size()])

            pipe.append([_zoom])
        self.add_animation(pipe)


class AISprite(MultiFrameSprite):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = self.image.get_size()
        self.should_zoom_in = self.should_zoom_out = False
    #
    # def update(self):
    #     # If enough time has passed since previous frame, advance to next frame
    #     if (time_now := pygame.time.get_ticks()) > self.prev_frame_at + self.frame_duration_millisec:
    #         self.prev_frame_at = time_now
    #
    #         # Preserve the centroid in case new frame has different size or coordinates
    #         center = self.rect.center
    #
    #         try:
    #             # Advance to next frame
    #             self.image = next(self.frames)
    #         except StopIteration:
    #             # Animation over
    #             pass
    #         else:
    #             # Edit the image
    #             if self.should_zoom_in:
    #                 self.image = pygame.transform.smoothscale(self.image, [0.7 * i for i in self.image.get_size()])
    #             if self.should_zoom_out:
    #                 self.image = pygame.transform.smoothscale(self.image, [1.3 * i for i in self.image.get_size()])
    #
    #             # Get new rectangle and restore centroid coordinates
    #             self.rect = self.image.get_rect(center=center)

    def speed_up(self):
        self.frame_duration_millisec = int(1000 / (self.fps * 3))

    def speed_normal(self):
        self.frame_duration_millisec = 1000 // self.fps

    def speed_down(self):
        self.frame_duration_millisec = int(1000 / (self.fps * 0.4))

    def zoom_in(self):
        self.should_zoom_in = True

    def zoom_reset(self):
        self.should_zoom_out = self.should_zoom_in = False

    def zoom_out(self):
        self.should_zoom_out = True

    # def show_listening_animation(self):
    #     self.listneing = True


