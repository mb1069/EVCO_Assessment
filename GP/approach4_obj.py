import curses
import random
import operator
import numpy

from functools import partial
from collections import deque

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp
import multiprocessing
import sys
import argparse as ap

S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
XSIZE, YSIZE = 14, 14
INIT_SIZE = -1

# NOTE: YOU MAY NEED TO ADD A CHECK THAT THERE ARE ENOUGH SPACES LEFT FOR
# THE FOOD (IF THE TAIL IS VERY LONG)
NFOOD = 1
GENERATIONS = 90
POP = 1000
NUM_EVALS = 1
cxpb = 0.7
mutpb = 0.8
parsimony = 1.05
max_tree_depth = 7

def if_then_else(condition, out1, out2):
    out1() if condition() else out2()

# This class can be used to create a basic player object (snake agent)

class SnakePlayer(list):
    global S_RIGHT, S_LEFT, S_UP, S_DOWN
    global XSIZE, YSIZE
    global INIT_SIZE
    def __init__(self):
        self.direction = S_RIGHT
        self.body = deque([[4, 10], [4, 9], [4, 8], [4, 7], [4, 6],
                     [4, 5], [4, 4], [4, 3], [4, 2], [4, 1], [4, 0]])
        INIT_SIZE = len(self.body)
        self.initial_size = len(self.body)
        self.score = 0
        self.ahead = []
        self.food = []

    def _reset(self):
        self.direction = S_RIGHT
        self.body = deque([[4, 10], [4, 9], [4, 8], [4, 7], [4, 6],
                     [4, 5], [4, 4], [4, 3], [4, 2], [4, 1], [4, 0]])
        self.score = 0
        self.initial_size = len(self.body)
        self.ahead = []
        self.food = []

    def is_tile_dangerous(self, tile):
        return (tile in self.body) or (tile[1]==0) or (tile[1]==XSIZE-1) or (tile[0]==0) or (tile[0]==YSIZE-1)

    def get_right_location(self, distance):
        tile = [self.body[0][0], self.body[0][1]]
        if self.direction == S_LEFT:
            tile[0]-=distance
        elif self.direction == S_UP:
            tile[1]+=distance
        elif self.direction == S_RIGHT:
            tile[0]+=distance
        elif self.direction == S_DOWN:
            tile[1]-=distance
        return tile

    def get_left_location(self, distance):
        tile = [self.body[0][0], self.body[0][1]]
        if self.direction == S_LEFT:
            tile[0]+=distance
        elif self.direction == S_UP:
            tile[1]-=distance
        elif self.direction == S_RIGHT:
            tile[0]-=distance
        elif self.direction == S_DOWN:
            tile[1]+=distance
        return tile

    def get_ahead_location(self):
        self.ahead = [ self.body[0][0] + (self.direction == S_DOWN and 1) + (self.direction == S_UP and -1), self.body[0][1] + (self.direction == S_LEFT and -1) + (self.direction == S_RIGHT and 1)]

    def get_ahead_2_location(self):
        tile = [self.body[0][0], self.body[0][1]]
        if self.direction == S_LEFT:
            tile[1]-=2
        elif self.direction == S_UP:
            tile[0]-=2
        elif self.direction == S_RIGHT:
            tile[1]+=2
        elif self.direction == S_DOWN:
            tile[0]+=2
        return tile

    def updatePosition(self):
        self.get_ahead_location()
        self.body.appendleft(self.ahead)

    # You are free to define more sensing options to the snake
    def turn_left(self):
        self.direction = (self.direction - 1) % 4

    # You are free to define more sensing options to the snake
    def turn_right(self):
        self.direction = (self.direction + 1) % 4

    def go_straight(self):
        pass

    def changeDirectionUp(self):
        self.direction = S_UP

    def changeDirectionRight(self):
        self.direction = S_RIGHT

    def changeDirectionDown(self):
        self.direction = S_DOWN

    def changeDirectionLeft(self):
        self.direction = S_LEFT

    def snake_has_collided(self):
        self.hit = False
        if self.body[0][0] == 0 or self.body[0][0] == (
                    YSIZE - 1) or self.body[0][1] == 0 or self.body[0][1] == (XSIZE - 1):
            self.hit = True
        # for i, val in enumerate(self.body):
        #     if (not i) and (self.body[0]==val):
        #         self.hit = True
        #         break
        for x in range (1, len(self.body)):
            if self.body[x] == self.body[0]:
                self.hit = True
                break
        # if self.body[0] in list(self.body)[1:]:
        #     self.hit = True
        return (self.hit)

    def sense_wall_ahead(self):
        self.get_ahead_location()
        return( self.ahead[0] == 0 or self.ahead[0] == (YSIZE-1) or self.ahead[1] == 0 or self.ahead[1] == (XSIZE-1) )

    def sense_food_ahead(self):
        self.get_ahead_location()
        return self.ahead in self.food

    def sense_wall_ahead(self):
        self.get_ahead_location()
        return( self.ahead[0] == 0 or self.ahead[0] == (YSIZE-1) or self.ahead[1] == 0 or self.ahead[1] == (XSIZE-1) )
    
    def sense_wall_right(self):
        tile = self.get_right_location(1)
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )

    def sense_wall_left(self):
        tile = self.get_left_location(1)
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )
    
    def sense_wall_2_ahead(self):
        tile = self.get_ahead_2_location()
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )

    def sense_moving_up(self):
        return self.direction == S_UP

    def sense_moving_right(self):
        return self.direction == S_RIGHT

    def sense_moving_down(self):
        return self.direction == S_DOWN

    def sense_moving_left(self):
        return self.direction == S_LEFT

    def sense_wall_2_away(self):
        tile = self.body[0]
        return (tile[0] in [2, XSIZE-2] or tile[1] in [2, XSIZE-2])

    def if_wall_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_wall_ahead, out1, out2)

    def if_wall_right(self, out1, out2):
        return partial(if_then_else, self.sense_wall_right, out1, out2)
    
    def if_wall_left(self, out1, out2):
        return partial(if_then_else, self.sense_wall_left, out1, out2)
    
    def if_wall_2_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_wall_2_ahead, out1, out2)

    def if_wall_2_left(self, out1, out2):
        return partial(if_then_else, self.sense_wall_2_left, out1, out2)    

    def if_food_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_food_ahead, out1, out2)

    def if_tail_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_tail_ahead, out1, out2)

    def if_moving_up(self, out1, out2):
        return partial(if_then_else, self.sense_moving_up, out1, out2)

    def if_moving_right(self, out1, out2):
        return partial(if_then_else, self.sense_moving_right, out1, out2)

    def if_moving_down(self, out1, out2):
        return partial(if_then_else, self.sense_moving_down, out1, out2)

    def if_moving_left(self, out1, out2):
        return partial(if_then_else, self.sense_moving_left, out1, out2)

    def if_wall_2_away(self, out1, out2):
        return partial(if_then_else, self.sense_wall_2_away, out1, out2)

def is_tile_empty(snake, food, tile):
    return not ((tile in snake.body) or (tile in food))

# This function places a food item in the environment
# TODO convert to using a spiral search around the point
def place_food(snake):
    food = []

    while len(food) < NFOOD:
        free_spaces = []
        for x in range(1, XSIZE - 1):
            for y in range(1, YSIZE - 1):
                if [x, y] not in snake.body and [x,y] not in food:
                    free_spaces.append([x,y])
        if len(free_spaces)==0:
            return ()
        rand = random.randint(0, len(free_spaces)-1)
        food.insert(0, free_spaces[rand])

    snake.food = food  # let the snake know where the food is
    return (food)


def runGame(individual):
    global snake
    global pset

    routine = gp.compile(individual, pset)

    total_score = 0.0
    total_steps = 0.0
    for run in range(0,NUM_EVALS):
        snake._reset()
        food = place_food(snake)
        timer = 0

        tour = set()
        tours = 0
        steps = 0 
        while not snake.snake_has_collided() and not timer == (XSIZE-2) * (YSIZE-2):
            # Verify game-winning condition
            if snake.score == ((XSIZE-2) * (YSIZE-2)) - snake.initial_size:
                break
            routine()
            snake.updatePosition()
            if snake.body[0] in food:
                snake.score += 1
                try:
                    food = place_food(snake)
                except ValueError:
                    break
                timer = 0
            else:
                snake.body.pop()
                timer += 1  # timesteps since last eaten
            steps+=1
            tour.add(str(snake.body[0]))
        # Penalise snakes which have timed out 
        if timer == XSIZE * YSIZE:
            return -10,
        total_steps += steps
        total_score += snake.score

    avg_steps = total_steps/(NUM_EVALS*100)
    avg_score = total_score/NUM_EVALS
    coverage = float(len(tour))/float((XSIZE-2)*(YSIZE-2))
    return coverage + avg_steps,


def runInGame(individual, evals):
    global snake
    global pset

    routine = gp.compile(individual, pset)

    total_score = 0.0
    for run in range(0, evals):
        snake._reset()
        food = place_food(snake)
        timer = 0

        while not snake.snake_has_collided() and not timer == (XSIZE-2) * (YSIZE-2):
            routine()
            snake.updatePosition()
            

            if snake.body[0] in food:
                snake.score += 1
                try:
                    food = place_food(snake)
                except ValueError:
                    break
                timer = 0
            else:
                snake.body.pop()
                timer += 1  # timesteps since last eaten
        total_score += snake.score
    avg_score = total_score/evals
    return avg_score



# This outline function is the same as runGame (see below). However,
# it displays the game graphically and thus runs slower
# This function is designed for you to be able to view and assess
# your strategies, rather than use during the course of evolution
def displayStrategyRun(individual):

    routine = gp.compile(individual, pset)

    curses.initscr()
    win = curses.newwin(YSIZE, XSIZE, 0, 0)
    win.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    win.border(0)
    win.nodelay(1)
    win.timeout(60)

    snake._reset()
    food = place_food(snake)

    for f in food:
        win.addch(f[0], f[1], '@')
    for b in snake.body:
        win.addch(b[0], b[1], 'o')

    timer = 0
    collided = False
    tmp = []
    while not collided and not timer == ((2 * XSIZE) * YSIZE):
        # Set up the display
        win.border(0)
        win.addstr(0, 2, 'Score : ' + str(snake.score) + ' ')
        win.getch()

        ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
        routine()
        snake.updatePosition()

        if snake.body[0] in food:
            snake.score += 1
            for f in food:
                win.addch(f[0], f[1], ' ')
            food = place_food(snake)
            timer = 0
        else:
            last = snake.body.pop()
            win.addch(last[0], last[1], ' ')
            timer += 1  # timesteps since last eaten
        win.addch(snake.body[0][0], snake.body[0][1], 'o')
        for f in food:
            win.addch(f[0], f[1], '@')

        collided = snake.snake_has_collided()
        hitBounds = snake.body[0][0] == 0 or snake.body[0][0] == (
                    YSIZE - 1) or snake.body[0][1] == 0 or snake.body[0][1] == (XSIZE - 1)
    
    curses.endwin()
    print "Collided: ", collided
    print "Hit wall: ", hitBounds
    print "Score: ", snake.score
    raw_input("Press to continue...")

    return snake.score,


def main(multicore, seeded):
    global snake
    global pset
    snake = SnakePlayer()

    pset = gp.PrimitiveSet("MAIN", 0)

    pset.addPrimitive(snake.if_wall_2_away, 2, name="if_wall_2_away")
    pset.addPrimitive(snake.if_wall_left, 2, name="if_wall_left")
    pset.addPrimitive(snake.if_wall_ahead, 2, name="if_wall_ahead")
    pset.addPrimitive(snake.if_wall_right, 2, name="if_wall_right")

    pset.addPrimitive(snake.if_moving_up, 2, name="if_moving_up")
    pset.addPrimitive(snake.if_moving_right, 2, name="if_moving_right")
    pset.addPrimitive(snake.if_moving_down, 2, name="if_moving_down")
    pset.addPrimitive(snake.if_moving_left, 2, name="if_moving_left")

    pset.addTerminal(snake.changeDirectionUp, name="go_up")
    pset.addTerminal(snake.changeDirectionDown, name="go_down")
    pset.addTerminal(snake.changeDirectionLeft, name="go_left")
    pset.addTerminal(snake.changeDirectionRight, name="go_right")
    pset.addTerminal(snake.go_straight, name="go_straight")

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=2, max_=6)
    toolbox.register("individual", tools.initIterate,
                     creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    toolbox.register("evaluate", runGame)
    toolbox.register("select", tools.selDoubleTournament, fitness_size=6, parsimony_size=parsimony, fitness_first=False)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("mutate", gp.mutNodeReplacement, pset=pset)

    toolbox.decorate("mate", gp.staticLimit(
        key=operator.attrgetter("height"), max_value=max_tree_depth))
    toolbox.decorate("mutate", gp.staticLimit(
        key=operator.attrgetter("height"), max_value=max_tree_depth))

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", lambda x: float(int(numpy.mean(x)*100))/100)
    mstats.register("std", lambda x: float(int(numpy.std(x)*100))/100)
    mstats.register("max", numpy.max)

    if multicore:
        pool = multiprocessing.Pool()
        toolbox.register("map", pool.map)

    
    pop = toolbox.population(n=POP)
    hof = tools.HallOfFame(3)
    try:
        pop, log = algorithms.eaSimple(
            pop, toolbox, cxpb, mutpb, GENERATIONS, stats=mstats, halloffame=hof, verbose=False)
        expr = tools.selBest(pop, 1)[0]
        print expr


        evals = 100
        val = runInGame(expr, evals)
        print "Evaluating: ", str(evals), "times, average score: ", str(val)

        if seeded:
            displayStrategyRun(expr)

    except KeyboardInterrupt:
        if multicore:
            pool.terminate()
            pool.join()
        raise KeyboardInterrupt
    return mstats.compile(pop), val

if __name__ == "__main__":

    parser = ap.ArgumentParser(description="My Script")
    parser.add_argument("--iterations", type=int)
    parser.add_argument("--multicore", action='store_true')
    parser.add_argument("--seed")
    parser.add_argument("--save_results", action='store_true')
    parser.add_argument("--max_gen", type=int)


    args, leftovers = parser.parse_known_args()

    iterations = 1 if args.iterations is None else int(args.iterations)
    multicore = args.multicore

    if args.seed is not None:
        iterations = 1
        multicore = False
        print "Seed detected, ignoring other flags (running single run on non-multicore process to ensure deterministic execution)."
   
    if args.max_gen is not None:
        GENERATIONS = args.max_gen
    try:
        while True:
            if args.seed is not None:
                seed = float(args.seed)
            else:
                seed = random.random()
            print "Seed: " + str(seed)
            random.seed(seed)
            out = main(multicore, args.seed is not None)
            record = out[0]
            print " Score: " +str(out[1])
            row = (out[1], str(seed), "\r")
            fd = open('approach4_seeds.csv', 'a')
            fd.write(",".join(map(str, row)))
            fd.close()
    except KeyboardInterrupt:
        print "Terminated by user, after %s iterations" % str(x)
