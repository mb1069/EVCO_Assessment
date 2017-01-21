# MutShrink with low mutation rate
import curses
import random
import operator
import numpy

from functools import partial
from collections import deque

import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp
# import pygraphviz as pgv
import multiprocessing
import sys
import argparse as ap

S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
XSIZE, YSIZE = 14, 14
INIT_SIZE = -1

# NOTE: YOU MAY NEED TO ADD A CHECK THAT THERE ARE ENOUGH SPACES LEFT FOR
# THE FOOD (IF THE TAIL IS VERY LONG)
NFOOD = 1
GENERATIONS = 150
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
        self.score = 0
        self.ahead = []
        self.food = []

    def _reset(self):
        self.direction = S_RIGHT
        self.body = deque([[4, 10], [4, 9], [4, 8], [4, 7], [4, 6],
                     [4, 5], [4, 4], [4, 3], [4, 2], [4, 1], [4, 0]])
        self.score = 0
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

    def sense_danger_right(self):
        tile = self.get_right_location(1)
        return self.is_tile_dangerous(tile)

    def sense_danger_2_right(self):
        tile = self.get_right_location(2)
        return self.is_tile_dangerous(tile)

    def sense_danger_left(self):
        tile = self.get_left_location(1)
        return self.is_tile_dangerous(tile)    
    
    def sense_danger_2_left(self):
        tile = self.get_left_location(1)
        return self.is_tile_dangerous(tile)    
    
    def sense_danger_2_left(self):
        tile = self.get_left_location(2)
        return self.is_tile_dangerous(tile)

    def sense_danger_ahead(self):
        self.get_ahead_location()
        return self.is_tile_dangerous(self.ahead)

    def sense_danger_2_ahead(self):
        tile = self.get_ahead_2_location()
        return self.is_tile_dangerous(tile)

    def sense_wall_ahead(self):
        self.get_ahead_location()
        return( self.ahead[0] == 0 or self.ahead[0] == (YSIZE-1) or self.ahead[1] == 0 or self.ahead[1] == (XSIZE-1) )

    def sense_food_ahead(self):
        self.get_ahead_location()
        return self.ahead in self.food

    def sense_tail_ahead(self):
        self.get_ahead_location()
        return self.ahead in self.body

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

    def sense_wall_2_left(self):
        tile = self.get_left_location(2)
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )

    def sense_wall_2_right(self):
        tile = self.get_right_location(2)
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )

    def sense_food_above(self):
        return self.food[0][0]<=self.body[0][0]

    def sense_food_right(self):
        return self.food[0][1]>=self.body[0][1]

    def sense_food_below(self):
        return not self.sense_food_above()

    def sense_food_left(self):
        return not self.sense_food_right()

    def sense_moving_up(self):
        return self.direction == S_UP

    def sense_moving_right(self):
        return self.direction == S_RIGHT

    def sense_moving_down(self):
        return self.direction == S_DOWN

    def sense_moving_left(self):
        return self.direction == S_LEFT


    def sense_against_wall(self):
        tile = self.body[0]
        return (tile[0] in [1, XSIZE-1]) or (tile[1] in [1, XSIZE-1])


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

    def if_wall_2_right(self, out1, out2):
        return partial(if_then_else, self.sense_wall_2_right, out1, out2)

    def if_food_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_food_ahead, out1, out2)

    def if_tail_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_tail_ahead, out1, out2)

    def if_danger_right(self, out1, out2):
        return partial(if_then_else, self.sense_danger_right, out1, out2)
    
    def if_danger_2_right(self, out1, out2):
        return partial(if_then_else, self.sense_danger_right, out1, out2)

    def if_danger_left(self, out1, out2):
        return partial(if_then_else, self.sense_danger_left, out1, out2)

    def if_danger_2_left(self, out1, out2):
        return partial(if_then_else, self.sense_danger_2_left, out1, out2)

    def if_danger_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_danger_ahead, out1, out2)

    def if_danger_2_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_danger_2_ahead, out1, out2)

    def if_food_above(self, out1, out2):
        return partial(if_then_else, self.sense_food_above, out1, out2)

    def if_food_right(self, out1, out2):
        return partial(if_then_else, self.sense_food_right, out1, out2)

    def if_food_left(self, out1, out2):
        return partial(if_then_else, self.sense_food_left, out1, out2)

    def if_food_down(self, out1, out2):
        return partial(if_then_else, self.sense_food_below, out1, out2)

    def if_moving_up(self, out1, out2):
        return partial(if_then_else, self.sense_moving_up, out1, out2)

    def if_moving_right(self, out1, out2):
        return partial(if_then_else, self.sense_moving_right, out1, out2)

    def if_moving_down(self, out1, out2):
        return partial(if_then_else, self.sense_moving_down, out1, out2)

    def if_moving_left(self, out1, out2):
        return partial(if_then_else, self.sense_moving_left, out1, out2)

    def if_against_wall(self, out1, out2):
        return partial(if_then_else, self.sense_against_wall, out1, out2)


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
            for y in range(1, YSIZE - 1 ):
                if [x, y] not in snake.body and [x,y] not in food:
                    free_spaces.append([x,y])
        rand = random.randint(0, len(free_spaces)-1)
        food.insert(0, free_spaces[rand])
        # randx = random.randint(1, (XSIZE - 2))
        # randy = random.randint(1, (YSIZE - 2))
        # rand_food_tile = [randy, randx]


        # if is_tile_empty(snake, food, rand_food_tile):
        #     food.insert(0, rand_food_tile)
        # else:
        #     closest_free_tile = rand_food_tile
        #     min_d = -1
        #     for x in range(XSIZE-1):
        #         for y in range(YSIZE-1):
        #             # print x,y, is_tile_empty(snake, food, [y,x])
        #             if is_tile_empty(snake, food, [y,x]):
        #                 d = numpy.sqrt(numpy.power(y-randy,2) + numpy.power(x-randx,2))
        #                 if d<min_d:
        #                     min_d = d
        #                     closest_free_tile[0] = y
        #                     closest_free_tile[1] = x
        #     food.insert(0, closest_free_tile)

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
        while not snake.snake_has_collided() and not timer == XSIZE * YSIZE:
            ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
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
        if timer == XSIZE * YSIZE:
            return -10,
        total_steps += steps
        total_score += snake.score

    avg_steps = total_steps/(NUM_EVALS*100)
    avg_score = total_score/NUM_EVALS
    coverage = float(len(tour))/float((XSIZE-2)*(YSIZE-2))
    return coverage + avg_steps,
    # return coverage * avg_steps,


def runInGame(individual, evals):
    global snake
    global pset

    routine = gp.compile(individual, pset)

    total_score = 0.0
    for run in range(0, evals):
        snake._reset()
        food = place_food(snake)
        timer = 0

        while not snake.snake_has_collided() and not timer == XSIZE * YSIZE:
            ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
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


def main(multicore):
    global snake
    global pset
    print multicore
    snake = SnakePlayer()

    pset = gp.PrimitiveSet("MAIN", 0)


# Other crap

    # pset.addPrimitive(snake.if_food_ahead, 2, name="if_food_ahead")
    # pset.addPrimitive(snake.if_tail_ahead, 2, name="if_tail_ahead")

    # pset.addPrimitive(snake.if_danger_right, 2, name="if_danger_right")
    # pset.addPrimitive(snake.if_danger_2_right, 2, name="if_danger_2_right")
    # pset.addPrimitive(snake.if_danger_left, 2, name="if_danger_left")
    # pset.addPrimitive(snake.if_danger_2_left, 2, name="if_danger_2_left")
    # pset.addPrimitive(snake.if_danger_ahead, 2, name="if_danger_ahead")
    # pset.addPrimitive(snake.if_danger_2_ahead, 2, name="if_danger_2_ahead")
    # pset.addPrimitive(snake.if_against_wall, 2, name="if_against_wall")

    # pset.addPrimitive(snake.if_food_above, 2, name="if_food_above")
    # pset.addPrimitive(snake.if_food_right, 2, name="if_food_right")

    # pset.addPrimitive(snake.if_food_left, 2, name="if_food_left")
    # pset.addPrimitive(snake.if_food_down, 2, name="if_food_down")



    pset.addPrimitive(snake.if_wall_2_away, 2, name="if_wall_2_away")

    # pset.addPrimitive(snake.if_wall_2_right, 2, name="if_wall_2_right")
    pset.addPrimitive(snake.if_wall_left, 2, name="if_wall_left")

# Necessary for fully functioning solutions
    
    pset.addPrimitive(snake.if_wall_ahead, 2, name="if_wall_ahead")
    # pset.addPrimitive(snake.if_wall_2_ahead, 2, name="if_wall_2_ahead")
    pset.addPrimitive(snake.if_wall_right, 2, name="if_wall_right")

    # pset.addPrimitive(snake.if_wall_2_left, 2, name="if_wall_2_left")

    pset.addPrimitive(snake.if_moving_up, 2, name="if_moving_up")
    pset.addPrimitive(snake.if_moving_right, 2, name="if_moving_right")
    pset.addPrimitive(snake.if_moving_down, 2, name="if_moving_down")
    pset.addPrimitive(snake.if_moving_left, 2, name="if_moving_left")

    pset.addTerminal(snake.changeDirectionUp, name="go_up")
    pset.addTerminal(snake.changeDirectionDown, name="go_down")
    pset.addTerminal(snake.changeDirectionLeft, name="go_left")
    pset.addTerminal(snake.changeDirectionRight, name="go_right")
    pset.addTerminal(snake.go_straight, name="go_straight")

    # displayStrategyRun("if_moving_left(if_wall_ahead(if_wall_2_left(if_wall_2_right(if_wall_right(go_up, go_straight), if_moving_down(go_straight, go_down)), go_down), if_wall_2_right(if_wall_2_left(if_moving_up(go_right, if_moving_right(go_right, go_left)), if_moving_right(go_right, go_straight)), if_moving_left(if_wall_2_ahead(go_left, go_straight), if_wall_2_ahead(if_moving_right(go_straight, go_left), go_right)))), if_moving_up(if_wall_2_ahead(if_wall_right(if_wall_right(go_left, if_wall_2_left(go_straight, if_wall_2_right(go_straight, go_left))), if_wall_2_left(go_straight, if_wall_2_right(go_straight, go_left))), if_wall_2_right(go_down, go_up)), if_wall_2_ahead(if_moving_down(if_moving_right(go_straight, go_left), if_moving_right(go_up, go_up)), if_wall_left(if_wall_2_right(go_right, go_right), if_wall_2_right(go_right, go_down)))))")
 

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=2, max_=6)
    toolbox.register("individual", tools.initIterate,
                     creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)

    toolbox.register("evaluate", runGame)
    # toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("select", tools.selDoubleTournament, fitness_size=5, parsimony_size=parsimony, fitness_first=True)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genFull, min_=1, max_=2, pset=pset)
    # toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
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
    # mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)

    if multicore:
        pool = multiprocessing.Pool()
        toolbox.register("map", pool.map)

    
    pop = toolbox.population(n=POP)
    hof = tools.HallOfFame(3)
    try:
        pop, log = algorithms.eaSimple(
            pop, toolbox, cxpb, mutpb, GENERATIONS, stats=mstats, halloffame=hof, verbose=True)
        # pop, log = algorithms.eaMuPlusLambda(
        #     pop, toolbox, int(POP*0.05), int(POP*0.5), cxpb, mutpb, GENERATIONS, stats=mstats, halloffame=hof, verbose=True)
        expr = tools.selBest(pop, 1)[0]
        print expr


        evals = 100
        val = runInGame(expr, evals)
        print "Evaluating: ", str(evals), "times, average score: ", str(val)

        # inp = raw_input("display best? ")
        # if len(inp)>0:
        #     displayStrategyRun(expr)

        # nodes, edges, labels = gp.graph(expr)
        # g = pgv.AGraph(nodeSep=1.0)
        # g.add_nodes_from(nodes)
        # g.add_edges_from(edges)
        # g.layout(prog="dot")
        # for i in nodes:
        #     n = g.get_node(i)
        #     n.attr["label"] = labels[i]
        # g.draw("tree.pdf")
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


    args, leftovers = parser.parse_known_args()

    iterations = 1 if args.iterations is None else int(args.iterations)
    multicore = args.multicore

    if args.seed is not None:
        iterations = 1
        multicore = False
        print "Seed detected, ignoring other flags (running single run on non-multicore process to ensure deterministic execution)."
   

    try:
        for x in range(0, iterations):
            
            if args.seed is not None:
                seed = float(args.seed)
            else:
                seed = random.random()
            random.seed(seed)
            out = main(multicore)
            record = out[0]
            if args.save_results:
                row = (record['fitness']['avg'], record['fitness']['max'], record['fitness']['std'], record['size']['avg'], record['size']['max'], record['size']['std'], out[1], "\r")
                fd = open('approach4_results.csv', 'a')
                fd.write(",".join(map(str, row)))
                fd.close()
    except KeyboardInterrupt:
        print "Terminated by user, after %s iterations" % str(x)
