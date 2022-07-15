import math
import time
import random
from functools import cached_property
from multiprocessing import Pool
import io

from PIL import Image, ImageFilter
import numpy as np
import pygame

from ant import Ant
from constants import *


class FPS(object):
    def __init__(self, _max: int = 60, init_val=70):
        self._start = time.time()
        self._end = time.time()
        self._average = [init_val]
        self._max = _max

    def get(self):
        return sum(self._average) / len(self._average)

    def poll(self):
        self._end = time.time()
        self._average.append(1 / (self._end - self._start))
        if len(self._average) > self._max: self._average.pop(0)
        self._start = time.time()
        return sum(self._average) / len(self._average)


class Environment_Cluster(object):
    def __init__(self, dimensions=(1200, 600), num_ants=200, clusters=10, velocity=2):
        """Initialize environment.

        Parameters
            :param dimensions ( (int, int), optional ): map dimensions

        """
        
        pygame.init()

        self.fps = FPS()
        self.font = pygame.font.Font('freesansbold.ttf', 16)
        
        pygame.display.set_caption(f"Follow the leader")
        self.W, self.H = dimensions

        self.map = pygame.display.set_mode(dimensions)
        
        self.map.fill(BLACK)
        
        self.data_layer = self.map.copy()
        s = pygame.surfarray.pixels_alpha(self.data_layer)
        s[:] = 0
        del s

        self.alpha_layer = self.data_layer.copy()
        

        self.ants = []
        for _ in range(clusters):
            x,y = random.randint(0, dimensions[0]), random.randint(0, dimensions[1])
            for a in range(int(num_ants/clusters)):
                self.ants.append(Ant(velocity, position=np.array([x,y]),
                                     bounds=np.array([[0,0], [self.W, self.H]])))
                self.map.set_at(self.ants[-1].position, self.ants[-1].color)
    
        
        pygame.display.update()

    def apply(self, ant):
        ant.update(self.alpha_layer)

    def update(self):
        # Reset background.
        self.map.fill(BLACK)

        # Fade trails.
        s = pygame.surfarray.pixels_alpha(self.data_layer)
        s[:] = (s * 0.99).astype(np.uint8)
        self.alpha_layer = s.copy()
        del s

        # Update ant positions.
        # with Pool(5) as p:
        map(self.apply, self.ants)
        for a in self.ants:
            self.apply(a)
            self.data_layer.set_at(a.position, a.color)

        self.map.blit(self.data_layer, (0,0))

        
        text = self.font.render(f"{str(round(self.fps.poll(), 1))} FPS", True, (0,0,0), (255,255,255))
        self.map.blit(text, (0,0))

    def add_mouse(self, coords):
        self.data_layer.set_at(coords, WHITE)


class Environment(object):
    def __init__(self, dimensions=(1200, 600), num_ants=750, velocity=2):
        """Initialize environment.

        Parameters
            :param dimensions ( (int, int), optional ): map dimensions

        """
        
        pygame.init()

        self.fps = FPS()
        self.font = pygame.font.Font('freesansbold.ttf', 16)
        
        pygame.display.set_caption(f"Follow the leader")
        self.W, self.H = dimensions

        self.map = pygame.display.set_mode(dimensions)
        
        self.map.fill(BLACK)
        
        self.data_layer = self.map.copy()
        s = pygame.surfarray.pixels_alpha(self.data_layer)
        s[:] = 0
        del s

        self.alpha_layer = self.data_layer.copy()
        

        self.ants = []
        for a in range(int(num_ants)):
            x,y = random.randint(0, dimensions[0]), random.randint(0, dimensions[1])
            self.ants.append(Ant(velocity, position=np.array([x,y]),
                            bounds=np.array([[0,0], [self.W, self.H]])))
            self.ants[-1].heading = 2 * math.pi + math.atan2(y - dimensions[1]/2, dimensions[0]/2 - x)
            self.map.set_at(self.ants[-1].position, self.ants[-1].color)
    
        
        # pygame.display.update()

    def apply(self, ant):
        ant.update(self.alpha_layer)

    def update(self):
        # Reset background.
        self.map.fill(BLACK)

        # Fade trails.
        s = pygame.surfarray.pixels_alpha(self.data_layer)
        s[:] = (s * 0.99).astype(np.uint8)
        self.alpha_layer = s.copy()
        del s

        self.alpha_layer = np.pad(self.alpha_layer, 8, mode='wrap')

        # Update ant positions.
        # with Pool(5) as p:
        #map(self.apply, self.ants)
        for a in self.ants:
            self.apply(a)
            self.data_layer.set_at(a.position, a.color)

        self.map.blit(self.data_layer, (0,0))

        raw = pygame.image.tostring(self.map, 'RGBA')
        blurred = Image.frombytes("RGBA", self.map.get_size(), raw).filter(ImageFilter.GaussianBlur(radius=1.5))
        self.map.blit(pygame.image.fromstring(blurred.tobytes(), self.map.get_size(), blurred.mode), (0,0))

        text = self.font.render(f"{str(round(self.fps.poll(), 1))} FPS", True, (0,0,0), (255,255,255))
        self.map.blit(text, (0,0))
    
