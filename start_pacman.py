from pygame.math import Vector2 as vec
import pygame
from pygame.locals import *
import os.path
import random
import math
import copy
import time
from pygame_widgets import Slider, TextBox, Button
import sys

def loadImage(name, useColorKey=False):
    fullname = os.path.join('Data',name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if useColorKey is True:
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey,RLEACCEL)
    return image

def loadSound(name):
    fullname = os.path.join('Data',name)
    sound = pygame.mixer.Sound(fullname)
    return sound

# screen settings
WIDTH, HEIGHT = 610, 670
FPS = 60
TOP_BOTTOM = 50
M_WIDTH, M_HEIGHT = WIDTH-TOP_BOTTOM, HEIGHT-TOP_BOTTOM

ROWS = 30
COLS = 28

# colour settings
BLACK = (0, 0, 0)
RED = (208, 22, 22)
GREY = (107, 107, 107)
WHITE = (255, 255, 255)
PLAYER_COLOUR = (190, 194, 15)

# font settings
START_TEXT_SIZE = 16
START_FONT = 'arial black'

pygame.init()
vec = pygame.math.Vector2
class Game:
    def __init__(self):
        """
        Pacman game initializer.
        """
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.running = True
        self.state = 'start'
        self.level = 'normal'
        self.cell_width = M_WIDTH//COLS
        self.cell_height = M_HEIGHT//ROWS
        self.number_movement = 6
        self.kill_ghost = []
        self.walls = []
        self.coins = []
        self.enemies = []
        self.e_pos = []
        self.cross = []
        self.rule_text =[]
        self.high_score_file = []
        self.p_pos = None
        self.load()
        self.player = Player(self, vec(self.p_pos))
        self.make_enemies()
        self.volume_sound = 0.5
        self.high_score = 0
        self.high_time = 0
        ######################### CREATE WIDGET #################################################################
        self.slider = Slider(self.screen, 100, 100, 400, 40, min=0, max=100, step=1)
        self.button_start = Button(
            self.screen, WIDTH//2-125, HEIGHT//2-200, 250, 100, text='PRESS TO START',
            fontSize=35, margin=20,
            textColour=(255, 0, 102),
            hoverColour=(204, 0, 153),
            inactiveColour=(255, 204, 0),
            pressedColour=(0, 255, 0), radius=20,
            onRelease=lambda:self.click_button_start())
        self.button_rule = Button(
            self.screen, WIDTH//2-150, HEIGHT//2-50, 300, 100, text='RULE AND ABOUT ME',
            fontSize=35, margin=20,
            textColour=(0, 204, 204),
            hoverColour=(204, 204, 0),
            inactiveColour=(255, 204, 0),
            pressedColour=(0, 255, 0), radius=20,
            onClick=lambda:self.click_button_rule())
        self.button_config = Button(
            self.screen, WIDTH//2-75, HEIGHT//2+100, 150, 100, text='SETTING',
            fontSize=35, margin=20,
            textColour=(0, 0, 102),
            hoverColour=(204, 0, 255),
            inactiveColour=(255, 204, 0),
            pressedColour=(0, 255, 0), radius=20,
            onClick=lambda:self.click_button_config())
        self.button_return = Button(
            self.screen, WIDTH-200, HEIGHT-50, 200, 50, text='RETURN TO START',
            fontSize=30, margin=10,
            textColour=(0, 0, 0),
            hoverColour=(204, 0, 255),
            inactiveColour=(255, 0, 0),
            pressedColour=(0, 255, 0), radius=20,
            onClick=lambda:self.click_button_return())
        self.button_return_game = Button(
            self.screen, WIDTH-150, HEIGHT-20, 150, 20, text='RETURN TO START',
            fontSize=20, margin=10,
            textColour=(0, 0, 0),
            hoverColour=(204, 0, 255),
            inactiveColour=(255, 0, 0),
            pressedColour=(0, 255, 0), radius=20,
            onClick=lambda:self.click_button_return())
        self.button_exit = Button(
            self.screen, 0, HEIGHT-40, 60, 40, text='EXIT',
            fontSize=30, margin=20,
            textColour=(0, 0, 0),
            hoverColour=(204, 0, 255),
            inactiveColour=(255, 0, 0),
            pressedColour=(0, 255, 0), radius=20,
            onClick=lambda:self.click_button_exit())
        self.button_set_level_0 = Button(
            self.screen, WIDTH//2 -225, HEIGHT//2, 180, 40, text='LEVEL NORMAL',
            fontSize=30, margin=20,
            textColour=(0, 0, 0),
            hoverColour=(204, 0, 255),
            inactiveColour=(0, 255, 0),
            pressedColour=(0, 255, 255), radius=20,
            onClick=lambda:self.click_button_set_level_0())
        self.button_set_level_1 = Button(
            self.screen, WIDTH//2 +25,HEIGHT//2, 200, 40, text='LEVEL RUN AWAY',
            fontSize=30, margin=20,
            textColour=(0, 0, 0),
            hoverColour=(204, 0, 255),
            inactiveColour=(153, 153, 102),
            pressedColour=(0, 255, 0), radius=20,
            onClick=lambda:self.click_button_set_level_1())
    ###################### FUNCTION TO BOTTON ###########################################
    def click_button_set_level_0(self):
        self.level = "normal"
    def click_button_set_level_1(self):
        self.level = "run away"
    def click_button_start(self):
        self.state = 'playing'
    def click_button_rule(self):
        self.state = 'rule'
    def click_button_config(self):
        self.state = 'config'
    def click_button_return(self):
        self.reset()
        self.state = 'start'
    def click_button_exit(self):
        self.running = False

    #######################################################################################

    def run(self):

        """
        Run pointed part of game.
        """
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_draw()
            elif self.state == 'rule':
                self.rule_events()
                self.rule_draw()
            elif self.state == 'config':
                self.config_events()
                self.config_draw()
            elif self.state == 'finish':
                self.finish_events()
                self.finish_draw()
            elif self.state == 'catch':
                self.catch_events()
                self.catch_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

############################ HELPER FUNCTIONS ##################################

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        """
        Creat text on screen.
        :param words: given text
        :param screen: screen, on which we want creat text
        :param pos: position text on screen
        :param size: size letter
        :param colour: letter colour
        :param font_name: font
        :param centered: centered
        """
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def load(self):
        """
        Load image and sound, created wall, coin, pacman and ghost.
        :return:
        """
        self.background = loadImage('background.png')
        self.background = pygame.transform.scale(self.background, (M_WIDTH, M_HEIGHT))
        # player image open
        self.image_Pacman_open = loadImage('Pacman.open.player_small.png',True)
        self.image_Pacman_open = pygame.transform.scale(self.image_Pacman_open, (self.cell_width, self.cell_height))
        self.image_Pacman = self.image_Pacman_open
        self.image_Pacman_open = self.image_Pacman_open.copy()
        self.image_Pacman_open_righ = self.image_Pacman_open
        self.image_Pacman_open_left = pygame.transform.flip(self.image_Pacman_open,True, False)
        self.image_Pacman_open_up= pygame.transform.rotate(self.image_Pacman_open, 90)
        self.image_Pacman_open_down = pygame.transform.rotate(self.image_Pacman_open, -90)
        #player image close
        self.image_Pacman_close = loadImage('Pacman.close.player.png',True)
        self.image_Pacman_close = pygame.transform.scale(self.image_Pacman_close, (self.cell_width, self.cell_height))
        self.image_Pacman_close = self.image_Pacman_close.copy()
        self.image_Pacman_close_righ = self.image_Pacman_close
        self.image_Pacman_close_left = pygame.transform.flip(self.image_Pacman_close,True, False)
        self.image_Pacman_close_up= pygame.transform.rotate(self.image_Pacman_close, 90)
        self.image_Pacman_close_down = pygame.transform.rotate(self.image_Pacman_close, -90)
        # Ghost image
        self.image_ghost = loadImage('duch.1.png', True)
        self.image_ghost = pygame.transform.scale(self.image_ghost, (20,20))
        # Food image
        self.image_food = loadImage('Jedzeni.png',True)
        self.image_food = pygame.transform.scale(self.image_food, (self.cell_width, self.cell_height))
        # Kill food image
        self.image_food_kill = loadImage('Jedzenie.super.png',True)
        self.image_food_kill = pygame.transform.scale(self.image_food_kill, (self.cell_width, self.cell_height))
        #sound eating food
        self.sound_eating = loadSound('pacman_chomp.wav')
        #sound dead player
        self.sound_dead_player = loadSound('pacman_death.wav')
        #soud dead ghost
        self.sound_dead_ghost = loadSound('pacman_eatghost.wav')
        #sound intermission
        self.sound_intermission = loadSound('pacman_intermission.wav')
        # Opening walls file
        # Creating walls list with co-ords of walls
        # stored as  a vector
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(xidx, yidx))
                    elif char == "C" or char == "S":
                        if self.level == 'normal':
                            self.coins.append(vec(xidx, yidx))
                    elif char == "P":
                        self.p_pos = [xidx, yidx]
                    elif char in ["2", "3", "4", "5"]:
                        self.e_pos.append([xidx, yidx])
                    elif char == "B":
                        pygame.draw.rect(self.background, BLACK, (xidx*self.cell_width, yidx*self.cell_height,
                                                                  self.cell_width, self.cell_height))
                    elif char == "S":
                        self.cross.append(vec(xidx, yidx))
                    elif char == "K":
                        if self.level == 'normal':
                            self.kill_ghost.append(vec(xidx,yidx))
            file.close()
        with open("rule.txt",mode="r",encoding="utf-8") as file:
            for line in file:
                self.rule_text.append(line)
            file.close()
        with open("high_score.txt",mode="r",encoding="utf-8") as file:
            for line in file:
                self.high_score_file.append(line)
            file.close()
        self.high_score = int(self.high_score_file[1])
        self.high_time = int(self.high_score_file[3])
    def make_enemies(self):
        """
        Created ghosts.
        """
        for idx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def reset(self):
        """
        When payer loose all live.
        """
        self.sound_dead_ghost.stop()
        self.sound_intermission.stop()
        if self.level == 'normal':
            self.player.lives = 3
        else:
            self.player.lives = 1
            self.current_time = 0
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0
        self.coins = []
        self.kill_ghost = []
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == 'C' or char == 'S':
                        if self.level == 'normal':
                            self.coins.append(vec(xidx, yidx))
                    elif char == "K":
                        if self.level == 'normal':
                            self.kill_ghost.append(vec(xidx, yidx))
        self.state = "playing"

    def killing_ghost(self,enemy):
        """
        Function to reset ghost and add score
        """
        self.player.current_score += 100
        self.sound_dead_ghost.play()
        self.sound_dead_ghost.set_volume(self.volume_sound)
        enemy.grid_pos = vec(enemy.starting_pos)
        enemy.pix_pos = enemy.get_pix_pos()
        enemy.direction *= 0

########################### INTRO FUNCTIONS ####################################

    def start_events(self):
        """
        Loading move the player with keyboard.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.state = 'playing'
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            self.button_start.listen(event)
            self.button_rule.listen(event)
            self.button_config.listen(event)
            self.button_exit.listen(event)

    def start_draw(self):
        """
        Creat windown "Start"
        """
        self.high_score = int(self.high_score_file[1])
        self.high_time = int(self.high_score_file[3])
        self.screen.fill(BLACK)
        self.button_start.draw()
        self.button_rule.draw()
        self.button_config.draw()
        self.button_exit.draw()
        self.draw_text("IF YOU DON'T LIKE MOUSE, PUSH SPACE BAR", self.screen, [WIDTH//2, HEIGHT-50],
                       START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [WIDTH//2, 55],
                       50, (44, 167, 198), START_FONT, centered=True)
        self.draw_text('HIGH SCORE: {}'.format(self.high_score), self.screen, [4, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        self.draw_text('HIGH TIME: {}'.format(self.high_time), self.screen, [WIDTH-160, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        pygame.display.update()

########################### PLAYING FUNCTIONS ##################################

    def playing_events(self):
        """
        Loading the move player with keyboard.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            self.button_return_game.listen(event)

    def playing_update(self):
        """
        Update player and ghosts movement on screen and live.
        """
        self.player.update()
        self.current_time += 1/6
        for enemy in self.enemies:
            enemy.update()
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                if self.player.super:
                    self.killing_ghost(enemy)
                else:
                    self.remove_life()
        if self.level == 'normal':
            if len(self.coins) == 0:
                self.state = 'finish'

    def playing_draw(self):
        """
        Updating on screen every move.
        """
        self.high_score = self.high_score_file[1]
        self.high_time = self.high_score_file[3]
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (TOP_BOTTOM//2, TOP_BOTTOM//2))
        self.draw_coins()
        self.draw_kill_coin()
        if self.level == 'normal':
            self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                           self.screen, [60, 0], 18, WHITE, START_FONT)
            self.draw_text('HIGH SCORE: {}'.format(self.high_score[:-1]), self.screen, [WIDTH//2+90, 0], 18, WHITE, START_FONT)
        else:
            self.draw_text('CURRENT TIME: {}'.format(int(self.current_time)),
                           self.screen, [60, 0], 18, WHITE, START_FONT)
            self.draw_text('HIGH TIME: {}'.format(self.high_time), self.screen, [WIDTH//2+90, 0], 18, WHITE, START_FONT)
        self.button_return_game.draw()
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()

    def remove_life(self):
        """
        Remove lives on screen and run to windown "game over".
        """
        self.sound_dead_player.play()
        self.sound_dead_player.set_volume(self.volume_sound)
        self.player.lives -= 1
        if self.player.lives == 0:
            if self.level == 'normal':
                self.state = "game over"
            else:
                self.state = 'catch'
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0

    def draw_coins(self):
        """
        Creat a coins.
        """
        for coin in self.coins:
            self.screen.blit(self.image_food, (int(coin.x*self.cell_width + self.cell_width//6)+ TOP_BOTTOM//2.25,
                                                        int(coin.y*self.cell_height + self.cell_height//6) + TOP_BOTTOM//2.5))

    def draw_kill_coin(self):
        for food_kill in self.kill_ghost:
            self.screen.blit(self.image_food_kill, (int(food_kill.x * self.cell_width + self.cell_width // 6) + TOP_BOTTOM // 2.25,
                              int(food_kill.y * self.cell_height + self.cell_height // 6) + TOP_BOTTOM // 2.5))

########################### GAME OVER FUNCTIONS ################################

    def game_over_events(self):
        for event in pygame.event.get():
            """
            Loading move the player with keyboard
            """
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            self.button_return.listen(event)
            self.button_exit.listen(event)

    def game_over_draw(self):
        """
        Creat windown "Game Over"
        """
        self.screen.fill(BLACK)
        again_text = "Press SPACE BAR to PLAY AGAIN"
        if self.player.current_score > int(self.high_score):
            self.high_score = self.player.current_score
            self.high_score_file[1] = str(self.player.current_score)
            self.high_score_file[1] = str(self.player.current_score) +'\n'
            plik = open("high_score.txt",'w')
            for element in self.high_score_file:
                plik.write(element)
            plik.close()
        self.draw_text('YOUR CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [WIDTH//2 , 250], 48,(153, 255, 102), 'arial',centered=True)
        self.draw_text('YOUR HIGH SCORE: {}'.format(self.high_score[:-1]), self.screen, [WIDTH//2, 400],48,(255, 191, 0), 'arial',centered=True)
        self.draw_text('YOUR HIGH SCORE: {}'.format(int(self.high_score)), self.screen, [WIDTH//2, 400],48,(255, 191, 0), 'arial',centered=True)

        self.draw_text("GAME OVER", self.screen, [WIDTH//2, 100], 52,
                       RED, "arial", centered=True)
        self.draw_text(again_text, self.screen, [WIDTH//2, 550],  36,
                       (190, 190, 190), "arial", centered=True)
        self.button_return.draw()
        self.button_exit.draw()
        pygame.display.update()

###################### RULE FUNCTION ###############################################################

    def rule_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = 'start'
            self.button_return.listen(event)
            self.button_exit.listen(event)

    def rule_draw(self):
        """
        Creat windown "About me and rule"
        """
        self.screen.fill((0, 102, 102))
        for numer,text in enumerate(self.rule_text):
            if text[:-1] == "ABOUT ME":
                self.draw_text(text[:-1], self.screen, [WIDTH // 2, 80], 52, (210, 121, 210), "arial black", centered=True)
            elif text[:-1] == "RULE":
                self.draw_text(text[:-1], self.screen, [WIDTH // 2, 50 + numer*30 ], 52, (210, 121, 210), "arial black", centered=True)
            elif numer == len(self.rule_text)-1:
                self.draw_text(text, self.screen, [WIDTH // 2, 80 + numer * 25], 20, (204, 153, 0), "Comic Sans MS",centered=True)
            elif numer < 5:
                self.draw_text(text[:-1], self.screen, [WIDTH // 2, 80 + numer * 25], 20, (204, 153, 0),"AvantGarde Md BT", centered=True)
            else:
                self.draw_text(text[:-1], self.screen, [WIDTH // 2, 80 + numer*25], 20, (204, 153, 0), "Comic Sans MS", centered=True)
        quit_text = "Press the ESCAPE to back to START"
        #self.draw_text("ABOUT", self.screen, [WIDTH // 2, 100], 52, RED, "arial", centered=True)
        self.draw_text(quit_text, self.screen, [WIDTH // 2, HEIGHT -100], 40, (190, 250, 190), "arial", centered=True)
        self.button_return.draw()
        self.button_exit.draw()
        pygame.display.update()

###################### CONFIGURE FUNCTION ###############################################################

    def config_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = 'start'
            self.slider.listen(event)
            self.volume_sound = self.slider.getValue()/100
            self.button_return.listen(event)
            self.button_exit.listen(event)
            self.button_set_level_1.listen(event)
            self.button_set_level_0.listen(event)

    def config_draw(self):
        """
        Creat windown "Config"
        """
        self.screen.fill((0, 102, 102))
        self.draw_text("Setting Volume", self.screen, [WIDTH // 2, 30], 36, (190, 190, 190), "arial", centered=True)
        self.draw_text("Level Game", self.screen, [WIDTH // 2, HEIGHT//2-50], 36, (190, 190, 190), "arial", centered=True)
        output = TextBox(self.screen, 270, 170, 60, 45,radius=20,borderThickness=2,borderColour=(255, 128, 0), fontSize=30)
        output.setText(str(self.slider.getValue())+"%")
        output_1 = TextBox(self.screen, WIDTH//2-65, HEIGHT//2 +65, 110, 40,radius=10,borderColour=(102, 153, 255),textColour=(0, 119, 179), fontSize=30)
        output_1.setText(self.level)
        self.slider.draw()
        output.draw()
        output_1.draw()
        self.button_return.draw()
        self.button_exit.draw()
        self.button_set_level_1.draw()
        self.button_set_level_0.draw()
        pygame.display.update()

########################### FINISH INTO #############################################

    def finish_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = 'start'
            self.button_return.listen(event)
            self.button_exit.listen(event)

    def finish_draw(self):
        """
        Creat windown "Finish"
        """
        self.screen.fill(BLACK)
        if self.player.current_score > int(self.high_score):
            self.high_score = self.player.current_score
            self.high_score_file[1] = str(self.player.current_score)
            self.high_score_file[1] = str(self.player.current_score) +'\n'
            plik = open("high_score.txt",'w')
            for element in self.high_score_file:
                plik.write(element)
            plik.close()
        self.draw_text('YOU LIVE YET', self.screen, [WIDTH//2 , 150], 65, (255, 204, 0), START_FONT,centered=True)
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [WIDTH//2, 300], 42, (153, 255, 102), 'arial',centered=True)
        self.draw_text('HIGH SCORE: {}'.format(self.high_score[:-1]), self.screen, [WIDTH // 2, 450], 42, (255, 204, 0), 'arial',centered=True)
        self.draw_text('HIGH SCORE: {}'.format(int(self.high_score)), self.screen, [WIDTH // 2, 450], 42, (255, 204, 0), 'arial',centered=True)
        self.button_return.draw()
        self.button_exit.draw()
        pygame.display.update()

################################### CATCH YOU FUNCTION #####################################333

    def catch_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = 'start'
            self.button_return.listen(event)
            self.button_exit.listen(event)

    def catch_draw(self):
        """
        Creat windown "CATCH"
        """
        self.screen.fill(BLACK)
        if self.current_time > float(self.high_time):
            self.high_score = self.player.current_score
            self.high_time = int(self.current_time)
            self.high_score_file[3] = str(self.high_time)
            plik = open("high_score.txt",'w')
            for element in self.high_score_file:
                plik.write(element)
            plik.close()
        self.draw_text('WASTED', self.screen, [WIDTH//2 , 150], 65, (255, 204, 0), START_FONT,centered=True)
        self.draw_text('CURRENT TIME: {}'.format(int(self.current_time)),
                       self.screen, [WIDTH//2, 300], 42, (153, 255, 102), 'arial',centered=True)
        self.draw_text('HIGH TIME: {}'.format(self.high_time), self.screen, [WIDTH // 2, 450], 42, (255, 204, 0), 'arial',centered=True)
        self.button_return.draw()
        self.button_exit.draw()
        pygame.display.update()

class Enemy:
    def __init__(self, game, pos, number):
        """Ghost initializer """
        self.game = game
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.game.cell_width//2.3)
        self.number = number
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = self.set_speed()
        self.x_dir = 0
        self.y_dir = 1
        self.old_pos = None

    def update(self):
        """
        Update ghost movement
        """
        if self.game.level == 'run away':
            self.personality = "speedy"

        else:
            if self.chceck_radious() < 10 and self.game.player.super == False:
                self.personality = "slow"
            elif self.chceck_radious() < 20 and self.game.player.super == True:
                self.personality = "scared"
            else:
                self.personality = "random"
        self.speed = self.set_speed()
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()
        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM +
                            self.game.cell_width//2)//self.game.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM +
                            self.game.cell_height//2)//self.game.cell_height+1

    def draw(self):
        """
        Creat ghost
        """
        self.game.screen.blit(self.game.image_ghost, (int(self.pix_pos.x - self.game.cell_width//2),
                                          int(self.pix_pos.y - self.game.cell_height//2)))

    def chceck_radious(self):
        """
        Calculating distance between ghost and player.
        :return: distance
        """
        distance = math.sqrt((self.grid_pos.x - self.game.player.grid_pos.x)**2 + (self.grid_pos.y - self.game.player.grid_pos.y)**2)
        return distance
    def set_speed(self):
        """
        Set speed ghost depending on the character.
        :return: speed
        """
        if self.personality in ["speedy"]:
            speed = 2
        else:
            speed = 1
        return speed
    def set_target(self):
        """
        Creat target dependig on the character.
        :return: position target.
        """
        if self.personality == "speedy" or self.personality == "slow":
            return self.game.player.grid_pos
        else:
            if self.game.player.grid_pos[0] > COLS//2 and self.game.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)
            elif self.game.player.grid_pos[0] > COLS//2 and self.game.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)
            elif self.game.player.grid_pos[0] < COLS//2 and self.game.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)
            else:
                return vec(COLS-2, ROWS-2)

    def time_to_move(self):
        """
        Chech ghost colidate with wall.
        """
        if int(self.pix_pos.x+TOP_BOTTOM//2) % self.game.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM//2) % self.game.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        """
        Define move ghost and creat a move.
        """
        if self.personality == "random":
            self.direction = self.get_random_direction()
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)
# follow player or escape from player
    def get_path_direction(self, target):
        """
        Function which look for path to pointed target
        :param target: player position or shelter position
        :return: vector of move
        """
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        """
        Look for the move which we must make to get to target
        :param target: player position or shelter position
        :return: move
        """
        path = self.find_path([int(self.grid_pos.x), int(self.grid_pos.y)],
                        [int(target[0]), int(target[1])])
        return path[1]

    def find_path(self, start, target):
        """
        Base function to find path
        :param start: position ghost
        :param target: player position or shelter position
        :return: list with movements
        """
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.game.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_random_direction(self):
        """
        This function is using to smooth random movment ghost. \n
        :return vector with radnom move
        """
        now_pos = vec(self.grid_pos)
        if self.grid_pos in self.game.cross:
            while True:
                number = random.randint(-2, 1)
                if number == -2:
                    self.x_dir, self.y_dir = 1, 0
                elif number == -1:
                    self.x_dir, self.y_dir = 0, 1
                elif number == 0:
                    self.x_dir, self.y_dir = -1, 0
                else:
                    self.x_dir, self.y_dir = 0, -1
                next_pos = vec(self.grid_pos.x + self.x_dir, self.grid_pos.y + self.y_dir)
                if next_pos not in self.game.walls :
                    if self.old_pos == None or next_pos != self.old_pos:
                        self.old_pos = now_pos
                        break
            return vec(self.x_dir, self.y_dir)
        elif self.time_to_move():
            while True:
                number = random.randint(-2, 1)
                if number == -2:
                    self.x_dir, self.y_dir = 1, 0
                elif number == -1:
                    self.x_dir, self.y_dir = 0, 1
                elif number == 0:
                    self.x_dir, self.y_dir = -1, 0
                else:
                    self.x_dir, self.y_dir = 0, -1
                next_pos = vec(self.grid_pos.x + self.x_dir, self.grid_pos.y + self.y_dir)
                if next_pos not in self.game.walls:
                    if self.old_pos == None or next_pos != self.old_pos:
                        self.old_pos = now_pos
                        break
            return vec(self.x_dir, self.y_dir)
        else:
            self.old_pos = now_pos
            return vec(self.x_dir, self.y_dir)

    def get_pix_pos(self):
        """
        Function calculate the postion with grid_pos to the pixel position.
        :return pixel vector
        """
        return vec((self.grid_pos.x*self.game.cell_width)+TOP_BOTTOM//2+self.game.cell_width//2,
                   (self.grid_pos.y*self.game.cell_height)+TOP_BOTTOM//2 +
                   self.game.cell_height//2)

    def set_personality(self):
        """
        Setting beginning character ghost
        :return: character ghost
        """
        if self.number == 0:
            return "random"
        elif self.number == 1:
            return "random"
        elif self.number == 2:
            return "random"
        else:
            return "random"

class Player:
    def __init__(self, game, pos):
        """
        Pacman Initializer.
        :param game: game class
        :param pos: starting position
        """
        self.game = game
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.old_pos = None
        self.super = False
        self.amount_move = 0
        self.amount_eated_coin = 0
        self.time_eat = time.time_ns()
        self.timer = 0
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2
        if self.game.level == 'normal':
            self.lives = 3
        else:
            self.lives = 1

    def update(self):
        """
        Update movement.
        """
        if self.able_to_move:
            old_pix = list(self.pix_pos)
            old_pix_1 = old_pix.copy()
            self.old_pos = vec(old_pix_1)
            self.pix_pos += self.direction*self.speed
            if self.old_pos != None:
                if self.pix_pos.x > self.old_pos.x:
                    if self.amount_move % 12 == 0:
                        self.game.image_Pacman = self.game.image_Pacman_open_righ
                    elif self.amount_move % 12 == 6:
                        self.game.image_Pacman = self.game.image_Pacman_close_righ
                if self.pix_pos.x < self.old_pos.x:
                    if self.amount_move % 12 == 0:
                        self.game.image_Pacman = self.game.image_Pacman_open_left
                    elif self.amount_move % 12 == 6:
                        self.game.image_Pacman = self.game.image_Pacman_close_left
                if self.pix_pos.y < self.old_pos.y:
                    if self.amount_move % 12 == 0:
                        self.game.image_Pacman = self.game.image_Pacman_open_up
                    elif self.amount_move % 12 == 6:
                        self.game.image_Pacman = self.game.image_Pacman_close_up
                if self.pix_pos.y > self.old_pos.y:
                    if self.amount_move % 12 == 0:
                        self.game.image_Pacman = self.game.image_Pacman_open_down
                    elif self.amount_move % 12 == 6:
                        self.game.image_Pacman = self.game.image_Pacman_close_down
                self.amount_move += 1

        if self.time_to_move():
            if self.stored_direction != None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()

        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM +
                            self.game.cell_width//2)//self.game.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM +
                            self.game.cell_height//2)//self.game.cell_height+1
        self.draw()
        if self.on_coin():
            self.eat_coin()
            if int(time.time_ns() - self.time_eat) > 17*(10**8):
                self.amount_eated_coin = 0
            if self.amount_eated_coin % 4 == 0:
                self.game.sound_eating.play()
                self.game.sound_eating.set_volume(self.game.volume_sound)
            self.amount_eated_coin += 1
            self.time_eat = time.time_ns()
        if self.on_super_food():
            self.eat_super_food()
            self.game.sound_intermission.stop()
            self.timer = 0
        if self.super:
            if self.timer > 500:
                self.game.sound_intermission.stop()
                self.super = False
                self.timer = 0
            else:
                if self.timer % 275 == 0:
                    self.game.sound_intermission.play()
                    self.game.sound_intermission.set_volume(self.game.volume_sound)
            self.timer += 1

    def draw(self):
        """
        Make pacman and lives.
        """
        self.game.screen.blit(self.game.image_Pacman, (int(self.pix_pos.x - self.game.cell_width//2),
                                          int(self.pix_pos.y - self.game.cell_height//2)))
        # Drawing player lives
        for x in range(self.lives):
            pygame.draw.circle(self.game.screen, PLAYER_COLOUR, (30 + 20*x, HEIGHT - 15), 7)


    def on_coin(self):
        """
        Check colidate coin with pacman.
        """
        if self.grid_pos in self.game.coins:
            if int(self.pix_pos.x+TOP_BOTTOM//2) % self.game.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM//2) % self.game.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def on_super_food(self):
        """
        Check colidate coin with pacman.
        """
        if self.grid_pos in self.game.kill_ghost:
            if int(self.pix_pos.x+TOP_BOTTOM//2) % self.game.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM//2) % self.game.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def eat_coin(self):
        """
        Remove coin with list and update current score.
        """
        self.game.coins.remove(self.grid_pos)

        self.current_score += 1


    def eat_super_food(self):
        self.game.kill_ghost.remove(self.grid_pos)
        self.super = True

    def move(self, direction):
        """
        Creat move pacman
        :param direction:

        """
        self.stored_direction = direction

    def get_pix_pos(self):
        """
        Function calculate the postion with grid_pos to the pixel position.
        :return pixel vector
        """
        return vec((self.grid_pos[0]*self.game.cell_width)+TOP_BOTTOM//2+self.game.cell_width//2,
                   (self.grid_pos[1]*self.game.cell_height) +
                   TOP_BOTTOM//2+self.game.cell_height//2)

    def time_to_move(self):
        """
        Chech correctness movement.
        """
        if int(self.pix_pos.x+TOP_BOTTOM//2) % self.game.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM//2) % self.game.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def can_move(self):
        """
        Chech collision pacman with wall.
        """
        for wall in self.game.walls:
            if vec(self.grid_pos+self.direction) == wall:
                return False
        return True

if __name__ == '__main__':
    game = Game()
    game.run()