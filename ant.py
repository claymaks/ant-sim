import os
import math
import random

os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION'] = '0'
import numpy as np
import pygame

from constants import *

LEFT = 0
CENTER = 1
RIGHT = 2

class Ant(object):
    def __init__(self, velocity=5, view_range=20, color=np.array([255,255,255,255]), position=np.array([600,350]), bounds=np.array([[0,0], [1200,700]])):
        self.velocity = velocity
        self.color = color
        self._position = position.astype(np.float64)
        self.heading = random.random() * 2*math.pi
        self.bounds = bounds
        self.view_range = view_range
        self.last_detection = -1

    def find_collision(self, wrapped_layer, coords, wrap_size=8):
        return np.mean(wrapped_layer[int(coords[0]):int(coords[0])+2 * wrap_size, int(coords[1]):int(coords[1])+2 * wrap_size])
        

    def cluster_seed(self, offset):
        return self.position + np.array([self.view_range * math.cos(self.heading + offset), -self.view_range * math.sin(self.heading + offset)])
        

    def get_nearest_path_or_continue(self, alpha_layer, split=0.8):
        # https://www.desmos.com/calculator/mriewazy0g

        # check three clusters
        l = self.find_collision(alpha_layer, self.cluster_seed(-split))
        c = self.find_collision(alpha_layer, self.cluster_seed(0))
        r = self.find_collision(alpha_layer, self.cluster_seed(split))
        
        _max = max([l,c,r])
        
        if _max == c and c > 0:
            if self.last_detection == RIGHT:
                self.heading += 0.1
            elif self.last_detection == LEFT:
                self.heading -= 0.1
            self.last_detection = CENTER
        elif _max == l and l > 0:
            self.heading -= 0.1
            self.last_detection = LEFT
        elif _max == r and r > 0:
            self.heading += 0.1
            self.last_detection = RIGHT
        else:
            self.last_detection = -1

        self.heading %= 2*math.pi
            

    def update(self, alpha_layer):
        self.get_nearest_path_or_continue(alpha_layer)
        self.heading += (2 * (random.random() - 0.5)) * 0.4
        
        self._position += np.array([self.velocity * math.cos(self.heading),
                                   -self.velocity * math.sin(self.heading)])

    @property
    def position(self):
        return self.bounds[0] + (self._position.astype(np.int64) % self.bounds[1])

    

class Ant_old(object):
    def __init__(self, velocity=5, view_range=50, color=np.array([255,255,255,255]), position=np.array([600,350]), bounds=np.array([[0,0], [1200,700]])):
        self.velocity = velocity
        self.color = color
        self._position = position.astype(np.float64)
        self.heading = random.random() * 2*math.pi
        self.bounds = bounds
        self.view_range = view_range
        self.last_detection = -1

    def find_collision(self, data_layer, heading):
        collisions = []
        pos = self.position
        x_0, y_0 = int(pos[0]), int(pos[1])

        # get distance at current angle
        x_i = x_0 + self.view_range * math.cos(heading)
        y_i = y_0 - self.view_range * math.sin(heading)

        # find endpoint
        for i in range(90):
            j = (i+10)/100
            
            x_t = self.bounds[0][0] + (int(x_0 * j + x_i * (1 - j)) % self.bounds[1][0])
            y_t = self.bounds[0][1] + (int(y_0 * j + y_i * (1 - j)) % self.bounds[1][1])

            if x_t == x_0 and y_t == y_0:
                continue
    
            alpha = data_layer.get_at((x_t,y_t))[3]
            
            if alpha > 10:
                return self.view_range * (i+10)/100
            
        return math.inf
        

    def get_nearest_path_or_continue(self, data_layer):

        # check three distances
        l = self.find_collision(data_layer, self.heading - 0.5)
        c = self.find_collision(data_layer, self.heading)
        r = self.find_collision(data_layer, self.heading + 0.5)

        _min = min([l,c,r])
        
        if _min == l and l != math.inf:
            self.heading -= 0.1
            self.last_detection = LEFT
        elif _min == r and r != math.inf:
            self.heading += 0.1
            self.last_detection = RIGHT
        elif _min == c and c != math.inf:
            if self.last_detection == RIGHT:
                self.heading += 0.1
            elif self.last_detection == LEFT:
                self.heading -= 0.1
            self.last_detection = CENTER
        else:
            self.last_detection = -1

        self.heading %= 2*math.pi
            

    def update(self, data_layer):
        self.get_nearest_path_or_continue(data_layer)
        
        self._position += np.array([self.velocity * math.cos(self.heading),
                                   -self.velocity * math.sin(self.heading)])

    @property
    def position(self):
        return self.bounds[0] + (self._position.astype(np.int64) % self.bounds[1])
    


