from __future__ import division
from ale_python_interface import ALEInterface
import numpy as np


def init(game, display_screen=False, record_dir=None):
    if display_screen:
        import pygame
        pygame.init()
    ale = ALEInterface()
    ale.setBool('display_screen', display_screen)
    ale.setInt('random_seed', 123)
    if record_dir is not None:
        ale.setString("record_screen_dir", record_dir)
    ale.loadROM('{game}.bin'.format(game=game))
    ale.setFloat("repeat_action_probability", 0)

    return ale




class ALEGameVisualizer:
    def __init__(self, screen_size):
        import pygame
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode((screen_size * 2, screen_size * 8))
        self.mem = {}

    def show(self, prev_frames):
        import pygame

        def l(x):
            if x not in self.mem:
                self.mem[x] = (x, x, x)
            return self.mem[x]

        f_l = np.frompyfunc(l, 1, 3)
        rect = pygame.Surface((self.screen_size * 2, self.screen_size * 8))
        image = np.reshape(zip(*list(f_l(np.concatenate(prev_frames).flatten()))), (self.screen_size * 4, self.screen_size, 3))

        image = np.transpose(image, [1, 0, 2])
        pygame.surfarray.blit_array(rect, np.repeat(np.repeat(image, 2, axis=0), 2, axis=1))
        self.screen.blit(rect, (0, 0))

        pygame.display.flip()

    def next_game(self):
        pass


class ALEGame(object):

    def __init__(self, ale):
        self.ale = ale
        self.finished = True
        self.cum_reward = 0
        self.action_set = self.ale.getMinimalActionSet()
        self.n_channels = 1

        self.h = 210
        self.w = 160

        self.prev_frames = [np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),

                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),

                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),

                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8),
                            np.zeros((self.h, self.w), dtype=np.uint8), ]

    def reset_game(self):
        self.ale.reset_game()
        self.finished = False
        self.cum_reward = 0

    def n_actions(self):
        return len(self.action_set)

    def input(self, action):
        lives_before = self.ale.lives()
        action_reward = self.ale.act(self.action_set[action])
        self.cum_reward += action_reward

        if self.ale.game_over():
            self.finished = True

        self.prev_frames.append(np.dot(self.ale.getScreenRGB(), np.array([0.2126, 0.7152, 0.0722])).astype(np.int8))
        self.prev_frames = self.prev_frames[1:]

        return action_reward, lives_before != self.ale.lives()

    def get_state(self):
        return self.prev_frames
