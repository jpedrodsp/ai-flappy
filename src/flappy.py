import asyncio
import random
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (  # Player,
    AiPlayer,
    Background,
    Floor,
    GameOver,
    Pipes,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window


class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
            safedistance=100,
            readydistance=150,
            bestscore=0,
            bestpipespassed=0,
            generations=1,
        )

    async def start(self):
        while True:
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = AiPlayer(self.config)
            self.aiplayercount = 999
            self.aiplayers = []
            for i in range(self.aiplayercount):
                aiplayer = AiPlayer(self.config)
                self.aiplayers.append(aiplayer)
                aiplayer.x += random.randint(
                    0, 30
                )  # offset the x position of the aiplayers to avoid overlap
                aiplayer.y += random.randint(
                    0, 30
                )  # offset the y position of the aiplayers to avoid overlap
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)
            await self.splash()
            await self.play()
            await self.game_over()

    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""

        self.player.set_mode(PlayerMode.SHM)
        for aiplayer in self.aiplayers:
            aiplayer.set_mode(PlayerMode.SHM)
        print(f"generations: {self.config.generations}")
        print(f"safe distance: {self.config.safedistance}")
        print(f"ready distance: {self.config.readydistance}")
        print(f"best score: {self.config.bestscore}")

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    return

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            for aiplayer in self.aiplayers:
                aiplayer.tick()
            self.welcome_message.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    def should_ai_tap(self, aiplayer):
        ai_y = aiplayer.cy

        # find the nearest upper and lower pipes
        nearest_upper_pipe = None
        for pipe in self.pipes.upper:
            if pipe.x + pipe.w < aiplayer.x:
                continue
            if nearest_upper_pipe:
                if (
                    pipe.x + pipe.w
                    < nearest_upper_pipe.x + nearest_upper_pipe.w
                ):
                    nearest_upper_pipe = pipe
            else:
                nearest_upper_pipe = pipe
        nearest_lower_pipe = None
        for pipe in self.pipes.lower:
            if pipe.x + pipe.w < aiplayer.x:
                continue
            if nearest_lower_pipe:
                if (
                    pipe.x + pipe.w
                    < nearest_lower_pipe.x + nearest_lower_pipe.w
                ):
                    nearest_lower_pipe = pipe
            else:
                nearest_lower_pipe = pipe

        # standard variables
        safe_distance = aiplayer.safedistance
        ready_distance = aiplayer.readydistance
        screen_middle_y = self.config.window.viewport_height / 2

        # determine if the ai should tap
        # > floor
        floor_distance = self.floor.y - ai_y

        # > pipes
        if nearest_lower_pipe and nearest_upper_pipe:
            distance_between_pipe = nearest_upper_pipe.x - aiplayer.x
            upper_pipe_bottom = nearest_upper_pipe.y + nearest_upper_pipe.h
            bottom_pipe_top = nearest_lower_pipe.y
        middle_point = (
            (upper_pipe_bottom + bottom_pipe_top) / 2
            + aiplayer.h
            + safe_distance / 10
        )

        """
        ## execute

        ### dont touch the floor, mantain distance from the floor
            ### if the ai is too close to the floor
                # jump
        ### if there is an obstacle
            ### get the distance between the ai and the obstacle
            ### find the bottom part of the upper pipe
            ### find the top part of the lower pipe
            ### get the gap size between the upper and lower pipe
            ### aim bird to go to the middle of the gap: dont jump if the bird is already in the middle
            ### if the bird is not in the middle
                # jump
        ### else
            ### find the screen middle y point
            ### if the bird is not in the middle
                # jump
        """

        if floor_distance < safe_distance:
            # print("floor")
            # print(f"floor_distance: {floor_distance}, distance_between_pipe: {distance_between_pipe}")
            # print(f"upb_distance: {upb_distance}, bpt_distance: {bpt_distance}")
            # print(f"ai_y: {ai_y}, upper_pipe_bottom: {upper_pipe_bottom}, bottom_pipe_top: {bottom_pipe_top}")
            return True
        if distance_between_pipe < ready_distance:
            if ai_y > middle_point and distance_between_pipe < safe_distance:
                # print("too low, jump now")
                # print(f"floor_distance: {floor_distance}, distance_between_pipe: {distance_between_pipe}")
                # print(f"upb_distance: {upb_distance}, bpt_distance: {bpt_distance}")
                # print(f"ai_y: {ai_y}, upper_pipe_bottom: {upper_pipe_bottom}, bottom_pipe_top: {bottom_pipe_top}")
                return True
            if ai_y < middle_point and distance_between_pipe < safe_distance:
                # print("too high, dont jump")
                # print(f"floor_distance: {floor_distance}, distance_between_pipe: {distance_between_pipe}")
                # print(f"upb_distance: {upb_distance}, bpt_distance: {bpt_distance}")
                # print(f"ai_y: {ai_y}, upper_pipe_bottom: {upper_pipe_bottom}, bottom_pipe_top: {bottom_pipe_top}")
                return False
        if ai_y > screen_middle_y:
            # print("middle")
            # print(f"floor_distance: {floor_distance}, distance_between_pipe: {distance_between_pipe}")
            # print(f"upb_distance: {upb_distance}, bpt_distance: {bpt_distance}")
            # print(f"ai_y: {ai_y}, upper_pipe_bottom: {upper_pipe_bottom}, bottom_pipe_top: {bottom_pipe_top}")
            return True
        return False

    async def play(self):
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)
        for aiplayer in self.aiplayers:
            aiplayer.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                self.player.set_mode(PlayerMode.CRASH)
            for aiplayer in self.aiplayers:
                if aiplayer.collided(self.pipes, self.floor):
                    aiplayer.set_mode(PlayerMode.CRASH)
            all_ai_players_dead = False
            for aiplayer in self.aiplayers:
                if aiplayer.mode != PlayerMode.CRASH:
                    all_ai_players_dead = False
                    break
                all_ai_players_dead = True
            if all_ai_players_dead and self.player.mode == PlayerMode.CRASH:
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()
                    self.player.pipes_passed += 1
                for aiplayer in self.aiplayers:
                    if aiplayer.crossed(pipe):
                        self.score.add()
                        aiplayer.pipes_passed += 1

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()
            if type(self.player) == AiPlayer:
                if self.should_ai_tap(self.player):
                    self.player.flap()
            for aiplayer in self.aiplayers:
                if self.should_ai_tap(aiplayer):
                    aiplayer.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            for aiplayer in self.aiplayers:
                aiplayer.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self):
        """crashes the player down and shows gameover image"""

        self.pipes.stop()
        self.floor.stop()

        # Pass generation
        self.config.generations += 1

        # Get the best score
        if self.score.score > self.config.bestscore:
            self.config.bestscore = self.score.score
            print(f"new best score: {self.config.bestscore}")

        # Get the last crossing bird's safe distance and ready distance
        pipes_passed_max = 0
        new_safe_distance_array = []
        for aiplayer in self.aiplayers:
            if aiplayer.pipes_passed > pipes_passed_max:
                pipes_passed_max = aiplayer.pipes_passed
                self.config.safedistance = aiplayer.safedistance
                self.config.readydistance = aiplayer.readydistance
                print(
                    f"new safe distance: {self.config.safedistance}, new ready distance: {self.config.readydistance}"
                )
                new_safe_distance_array.append(aiplayer.safedistance)
        if self.player.pipes_passed > pipes_passed_max:
            pipes_passed_max = self.player.pipes_passed
            self.config.safedistance = self.player.safedistance
            self.config.readydistance = self.player.readydistance
            print(
                f"new safe distance: {self.config.safedistance}, new ready distance: {self.config.readydistance}"
            )
        if pipes_passed_max > self.config.bestpipespassed:
            self.config.bestpipespassed = pipes_passed_max
            print(f"new best pipes passed: {self.config.bestpipespassed}")

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            for aiplayer in self.aiplayers:
                aiplayer.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)
