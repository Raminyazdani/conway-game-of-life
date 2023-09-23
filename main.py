import os
import random
import threading
import time
import pygame
import numpy
import numpy as np
import ctypes

# At each step in time, the following transitions occur:
#
# Any live cell with fewer than two live neighbours dies, as if by underpopulation.
# Any live cell with two or three live neighbours lives on to the next generation.
# Any live cell with more than three live neighbours dies, as if by overpopulation.
# Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
# These rules, which compare the behaviour of the automaton to real life, can be condensed into the following:
#
# Any live cell with two or three live neighbours survives.
# Any dead cell with three live neighbours becomes a live cell.
# All others live cells die in the next generation. Similarly, all other dead cells stay dead.


class LifeNode(threading.Thread):
    all_nodes = {}
    lock = threading.Lock()
    get_next_move = threading.Event()
    put_next_move = threading.Event()
    wait_for_run_again = threading.Event()
    count = 1
    all_nodes_numpy = None

    def __init__(self, w, h, printer):
        super().__init__()

        self.condition = 0
        self.next_condition = 0
        self.x = w
        self.y = h
        LifeNode.all_nodes[(w, h)] = self
        self.neighbors = None
        self.finished = False
        self.waiting = False
        self.job = False
        self.id = LifeNode.count
        LifeNode.count += 1
        self.printer = printer

    def get_neighbors(self):
        temp = []
        for x in range(self.x - 1,
                       self.x + 2):
            for y in range(self.y - 1,
                           self.y + 2):
                res = LifeNode.all_nodes.get((x, y),
                                             None)
                if res is not None and res != self:
                    temp.append(res)

        self.neighbors = numpy.array(temp)

    def run(self) -> None:
        self.get_neighbors()
        self.waiting = True
        while True:
            if self.condition == 1:
                self.printer.pygame.draw.rect(self.printer.screen,
                                              self.printer.GREEN,
                                              [(self.printer.MARGIN + self.printer.WIDTH) * self.y + self.printer.MARGIN, (self.printer.MARGIN + self.printer.HEIGHT) * self.x + self.printer.MARGIN, self.printer.WIDTH, self.printer.HEIGHT])  # screen.blit(font.render(str(cell.id),  #                                   True,  #                                   (255, 0, 0)),  #                  [(MARGIN + WIDTH) * cell.y + MARGIN, (MARGIN + HEIGHT) * cell.x + MARGIN, WIDTH, HEIGHT])
            else:
                self.printer.pygame.draw.rect(self.printer.screen,
                                              self.printer.WHITE,
                                              [(self.printer.MARGIN + self.printer.WIDTH) * self.y + self.printer.MARGIN, (self.printer.MARGIN + self.printer.HEIGHT) * self.x + self.printer.MARGIN, self.printer.WIDTH, self.printer.HEIGHT])  # screen.blit(font.render(str(cell.id),  #                                   True,  #                                   (255, 0, 0)),  #                  [(MARGIN + WIDTH) * cell.y + MARGIN, (MARGIN + HEIGHT) * cell.x + MARGIN, WIDTH, HEIGHT])
            self.get_next_move.wait()
            self.next_phase()
            GameBox.temp_done += 1
            self.put_next_move.wait()
            self.next_run_started()
            GameBox.temp_done += 1
            self.wait_for_run_again.wait()
            GameBox.temp_done += 1

            time.sleep(0.001)

    def next_phase(self):
        self.waiting = False
        self.alive_nodes = 0
        self.dead_nodes = 0
        for n in self.neighbors:
            if n.condition == 0:
                self.dead_nodes += 1
            else:
                self.alive_nodes += 1
        if self.condition == 1:
            if self.alive_nodes < 2:
                self.next_condition = 0
            elif self.alive_nodes == 2 or self.alive_nodes == 3:
                self.next_condition = 1
            elif self.alive_nodes > 3:
                self.next_condition = 0
            else:
                self.next_condition = 0
        elif self.condition == 0:
            if self.alive_nodes == 3:
                self.next_condition = 1
            else:
                self.next_condition = 0


        else:
            self.next_condition = 0
        GameBox.temp_data[self.id] = {
            "condition": self.condition,
            "next_condition": self.next_condition,
            "alive_nodes": self.alive_nodes,
            "dead_nodes": self.dead_nodes
            }
        self.waiting = True

    def next_run_started(self):
        self.waiting = False
        self.condition = self.next_condition
        self.waiting = True

    def __str__(self):
        return str(self.condition)

    def __repr__(self):
        return self.__str__()

def print_box_str(box):
    result = ""
    for row in box:
        for node in row:
            temp = node.condition
            if temp == 0:
                result += " "
            else:
                result += "●"
        result += "\n"
    # clear the screen
    print("\033[H\033[J")
    os.system("cls")
    print(result)

def print_box(gird):
    pass

class Printer():

    def __init__(self, x, y):
        self.size = 8
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

        # This sets the WIDTH and HEIGHT of each grid location


        # This sets the margin between each cell
        self.MARGIN = 1

        # Create a 2 dimensional array. A two dimensional
        # array is simply a list of lists.
        # Initialize pygame
        self.pygame = pygame
        self.pygame.init()
        self.size_h=self.size
        self.size_w=self.size
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        scrn_height = screensize[1]
        scrn_width = screensize[0]
        while True:
            self.WIDTH = self.size_w
            self.HEIGHT = self.size_h
            temp_x = (x * (self.HEIGHT + self.MARGIN))
            temp_y = (y * (self.WIDTH + self.MARGIN))
            if temp_x >scrn_height:
                self.size_h = self.size_h-1
                continue
            if temp_y > scrn_width:
                self.size_w = self.size_w-1
                continue
            if temp_y <= scrn_width and temp_x <= scrn_height:
                break

        # Set the HEIGHT and WIDTH of the screen
        self.WINDOW_SIZE = [temp_y, temp_x]

        self.screen = self.pygame.display.set_mode(self.WINDOW_SIZE)
        # screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        # Set title of screen
        self.pygame.display.set_caption("Array Backed Grid")

        self.done = False
        self.font = pygame.font.SysFont("arial",
                                        8)
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

class GameBox(threading.Thread):
    temp_done = 0
    temp_data = {}

    def __init__(self, size_w, size_h):
        super().__init__()
        self.temp = int(size_w * size_h)
        self.printer = Printer(size_h,
                               size_w)
        self.dimension = (size_h, size_w)
        self.box = self.create_box()

    def create_box(self):
        # temp = 0
        # tempoprary_list = np.array([])
        # for x in range(self.dimension[0]):
        #     temp_temp = np.array([])
        #     for y in range(self.dimension[1]):
        #         tempoprary_list = np.append(tempoprary_list,[LifeNode(y,x)])
        #         print(f"node created {self.temp}/{temp}")
        #         temp+=1
        # tempoprary_list = np.reshape(tempoprary_list,(self.dimension[0],self.dimension[1]))
        # return tempoprary_list
        temp = 0

        tempoprary_list = np.empty(shape = (self.dimension[0], self.dimension[1]),
                                   dtype = object)
        for x in range(self.dimension[0]):
            for y in range(self.dimension[1]):
                tempoprary_list[x][y] = LifeNode(x,
                                                 y,
                                                 self.printer)
                print(f"node created {self.temp}/{temp}")
                temp += 1
        print(tempoprary_list.shape)
        return tempoprary_list  # return numpy.array([[LifeNode(y,  #                               x) for x in range(self.dimension[0])] for y in range(self.dimension[1])])

    def run(self) -> None:
        self.all_node_start(start = True)
        self.printer.screen.fill(self.printer.BLACK)
        temp_repeat = []
        while True:
            # clear console
            # Set the screen background
            # self.printer.screen.fill(self.printer.BLACK)
            # Draw the grid
            # for row in a.box:
            #     for cell in row:
            #         cell: LifeNode
            #         color = WHITE
            #         if cell.condition == 1:
            #             color = GREEN
            #         pygame.draw.rect(screen,
            #                          color,
            #                          [(MARGIN + WIDTH) * cell.y + MARGIN, (MARGIN + HEIGHT) * cell.x + MARGIN, WIDTH, HEIGHT])  # screen.blit(font.render(str(cell.id),  #                                   True,  #                                   (255, 0, 0)),  #                  [(MARGIN + WIDTH) * cell.y + MARGIN, (MARGIN + HEIGHT) * cell.x + MARGIN, WIDTH, HEIGHT])
            # Limit to 60 frames per second
            self.printer.clock.tick()

            # Go ahead and update the screen with what we've drawn.
            self.printer.pygame.display.flip()  # Be IDLE friendly. If you forget this line, the program will 'hang'  # on exit.
            # al = []
            # for x in self.box:
            #     for y in x:
            #         al.append(y.condition)
            # temp_repeat.append(sum(al))

            # if len(temp_repeat)>=5:
            #     self.random_conditoon(5)
            #     temp_repeat=[]
            # else:
            #     if sum(al)<=(2/100)*(self.dimension[0]*self.dimension[1]):
            #
            #         self.random_conditoon(num=int((2/100)*(self.dimension[0]*self.dimension[1]))-sum(al))
            # all node are waiting == True
            LifeNode.get_next_move.set()

            while GameBox.temp_done != self.temp:
                time.sleep(0.00001)
            GameBox.temp_done = 0
            LifeNode.get_next_move.clear()

            LifeNode.put_next_move.set()
            while GameBox.temp_done != self.temp:
                time.sleep(0.00001)
            GameBox.temp_done = 0
            LifeNode.put_next_move.clear()

            LifeNode.wait_for_run_again.set()
            while GameBox.temp_done != self.temp:
                time.sleep(0.00001)
            GameBox.temp_done = 0
            LifeNode.wait_for_run_again.clear()

            time.sleep(0.000001)

    @property
    def conditions(self):
        alives = 0
        deads = 0
        for row in self.box:
            for node in row:
                if node.condition == 1:
                    alives += 1
                else:
                    deads += 1

        return alives, deads

    def all_node_start(self, start = None, cond = "waiting"):
        temp = numpy.array([])

        for row in self.box:
            for node in row:
                if start == True:
                    node.start()
                    x = random.randint(0,
                                       100)
                    if x < 5:
                        node.condition = 1
                t2 = numpy.array([node])
                temp = numpy.append(temp,
                                    t2)

        while len(temp) > 0:
            for i in temp:
                i: LifeNode
                if cond == "waiting":
                    if i.waiting == True:
                        temp = numpy.delete(temp,
                                            numpy.where(temp == i))
                else:
                    if i.waiting == False:
                        temp = numpy.delete(temp,
                                            numpy.where(temp == i))

    def random_conditoon(self,num=None):

        if not num:
            for row in self.box:
                for node in row:
                    x = random.randint(0,
                                       100)
                    if x <= 10:
                        node.condition = 1
        else:
            if num < 0:
                return
            temp_list = []
            for row in self.box:
                for node in row:
                    if node.condition == 0:
                        temp_list.append(node)
            if len(temp_list)>0:
                if num >len(temp_list):
                    num = len(temp_list)

                for n in range(num):
                    if len(temp_list)==0:
                        return
                    try:
                        t = temp_list.pop(random.randint(0,len(temp_list)))
                        t.condition=1
                    except:
                        return
a = GameBox(16*15 ,
            10*15 )

a.start()  # print(a.box)  # a.random_conditoon()  # print()  # print(a.box)  # cell=[1,1]
#
# print("\tconditoion",a.box[*cell].condition)
# print("\tnext_conditoion",a.box[*cell].next_condition)
# print()
# a.box[*cell].next_phase()
# print("\tconditoion",a.box[*cell].condition)
# print("\tnext_conditoion",a.box[*cell].next_condition)
# print()
