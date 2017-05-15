#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *
from random import randint
from collections import deque
from heapq import heappop, heappush

SCREEN = (300, 300)
BLOCK_SIZE = 20
COLS = SCREEN[0] / BLOCK_SIZE
ROWS = SCREEN[1] / BLOCK_SIZE
FREQUENCY = 30
FPS = 30
EXIT_TIME = 5000
WHITE = 0xffffff
RED = 0xff0000
GREEN = 0x00ff00
BLUE = 0x0000ff
YELLOW = 0xffff00
BLACK = 0x000000
DIR = (0, 1)
DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
OPP_DIR = {
    (0, 1): (0, -1),
    (0, -1): (0, 1),
    (1, 0): (-1, 0),
    (-1, 0): (1, 0),
}


class Block(object):

    def __init__(self, screen, pos=(0, 0), color=GREEN):
        self.screen = screen
        self.pos = pos
        self.rect_pos = (self.pos[0] * BLOCK_SIZE,
                         self.pos[1] * BLOCK_SIZE)
        self.val = self.pos[0] * ROWS + self.pos[1]
        self.color = color

    def display(self):
        pygame.draw.rect(self.screen, self.color, Rect(
            self.rect_pos, (BLOCK_SIZE, BLOCK_SIZE)))
        pygame.draw.rect(self.screen, BLACK, Rect(
            self.rect_pos, (BLOCK_SIZE, BLOCK_SIZE)), 1)

    def set_color(self, color):
        self.color = color


class Snake(object):

    def __init__(self, screen, size=2, dr=(1, 0)):
        self.screen = screen
        self.body = deque()
        self.size = size
        self.dr = dr
        for i in range(self.size):
            self.body.append(Block(self.screen, pos=(i, 0)))
        self.head = self.body[-1]
        self.head.set_color(RED)
        self.tail = self.body[0]
        self.tail.set_color(BLUE)

    def display(self):
        for block in self.body:
            block.display()

    def is_collision(self, food):
        return (self.head.val == food.val)

    def move(self, head):
        self.head.set_color(GREEN)
        self.head = head
        self.head.set_color(RED)
        self.body.append(self.head)
        tail = self.body.popleft()
        self.tail = self.body[0]
        self.tail.set_color(BLUE)
        return tail

    def update(self, tail, dr):
        self.tail.set_color(GREEN)
        self.tail = tail
        self.tail.set_color(BLUE)
        self.body.appendleft(self.tail)
        self.head.set_color(RED)
        self.dr = dr

    def shortest_path(self, food):
        obs = deque([block.val for block in self.body])
        pq = [(0, [self.head], self.dr, obs)]
        vis = [False for _ in range(ROWS * COLS)]
        vis[self.head.val] = True
        flg = False

        while pq:
            (pr, path, c_dr, obs) = heappop(pq)
            u = path[-1]

            if u.val == food.val:
                return (path, c_dr, obs)

            flg = False
            for d in DIRS:
                if d == OPP_DIR[c_dr]:
                    continue

                v = Block(screen, pos=(u.pos[0] + d[0], u.pos[1]
                                       + d[1]))

                if v.pos[0] < 0 or v.pos[0] >= COLS or v.pos[1] < 0 \
                        or v.pos[1] >= ROWS or vis[v.val] or v.val in obs:
                    continue

                new_path = list(path)
                new_path.append(v)

                h = manhattan(v, food) + manhattan(u, v)

                new_obs = deque(obs)
                new_obs.popleft()
                new_obs.append(v.val)

                heappush(pq, (h, new_path, d, new_obs))
                vis[v.val] = True
                flg = True

        if not flg:
            return False


def random_spawn(body=deque()):
    food = Block(screen, pos=(randint(0, COLS - 1),
                              randint(0, ROWS - 1)), color=YELLOW)
    obs = [block.val for block in body]
    while food.val in obs:
        food = Block(screen, pos=(randint(0, COLS - 1),
                                  randint(0, ROWS - 1)), color=YELLOW)
    return food


def manhattan(a, b):
    return abs(a.pos[0] - b.pos[0]) + abs(a.pos[1] - b.pos[1])


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode(SCREEN, 0, 32)
    pygame.display.set_caption('Snake !')
    clock = pygame.time.Clock()

    snake = Snake(screen)
    food = random_spawn()

    spath = snake.shortest_path(food)
    if not spath:
        print 'Game Over!'
        pygame.time.wait(EXIT_TIME)
        pygame.quit()
        sys.exit()

    (path, dr, obs) = spath

    i = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)

        if snake.is_collision(food):
            snake.update(tail, dr)

            food = random_spawn(snake.body)
            snake.display()
            food.display()
            pygame.display.update()

            spath = snake.shortest_path(food)
            if not spath:
                print 'Game Over!'
                pygame.time.wait(EXIT_TIME)
                pygame.quit()
                sys.exit()

            (path, dr, obs) = spath
            i = 0

        else:
            snake.display()
            food.display()
            pygame.display.update()

            tail = snake.move(path[i])
            i += 1

        pygame.time.delay(FREQUENCY)
        clock.tick(FPS)
