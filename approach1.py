# This code defines the agent (as in the playable version) in a way that can be called and executed from an evolutionary algorithm. The code is partial and will not execute. You need to add to the code to create an evolutionary algorithm that evolves and executes a snake agent.
import curses
import random
import operator
import numpy

from functools import partial

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp
import	pygraphviz	as	pgv

S_UP, S_RIGHT, S_LEFT, S_DOWN = 0,1,2,3
XSIZE,YSIZE = 14,14
NFOOD = 1 # NOTE: YOU MAY NEED TO ADD A CHECK THAT THERE ARE ENOUGH SPACES LEFT FOR THE FOOD (IF THE TAIL IS VERY LONG)
MAX_MOVES = XSIZE*YSIZE

def progn(*args):
    for arg in args:
        arg()

def prog2(out1, out2):
    return partial(progn,out1,out2)

def prog3(out1, out2, out3):
    return partial(progn,out1,out2,out3)

def if_then_else(condition, out1, out2):
    out1() if condition() else out2()



# This function places a food item in the environment
def placeFood(snake):
	food = []
	while len(food) < NFOOD:
		potentialfood = [random.randint(1, (YSIZE-2)), random.randint(1, (XSIZE-2))]
		if not (potentialfood in snake.body) and not (potentialfood in food):
			food.append(potentialfood)
	snake.food = food  # let the snake know where the food is
	return( food )

# This class can be used to create a basic player object (snake agent)
class SnakePlayer(list):
	global S_RIGHT, S_LEFT, S_UP, S_DOWN
	global XSIZE, YSIZE
	global MAX_MOVES

	def __init__(self):
		self.direction = S_RIGHT
		self.body = [ [4,10], [4,9], [4,8], [4,7], [4,6], [4,5], [4,4], [4,3], [4,2], [4,1],[4,0] ]
		self.score = 0
		self.ahead = []
		self.food = []
		self.moves = 0

	def _reset(self):
		self.direction = S_RIGHT
		self.body[:] = [ [4,10], [4,9], [4,8], [4,7], [4,6], [4,5], [4,4], [4,3], [4,2], [4,1],[4,0] ]
		self.score = 0
		self.ahead = []
		self.food = []
		self.moves = 0

	def getAheadLocation(self):
		self.ahead = [ self.body[0][0] + (self.direction == S_DOWN and 1) + (self.direction == S_UP and -1), self.body[0][1] + (self.direction == S_LEFT and -1) + (self.direction == S_RIGHT and 1)]

	def updatePosition(self):
		self.getAheadLocation()
		self.body.insert(0, self.ahead )

	def run(self,routine):
		self._reset()
		while self.moves < MAX_MOVES:
		    # self.moves += 1
		    routine()


	def move_forward(self):
		if self.moves < MAX_MOVES:
			self.moves += 1
			self.row = (self.row + self.dir_row[self.dir]) % self.matrix_row
			self.col = (self.col + self.dir_col[self.dir]) % self.matrix_col
			if [col, row] in self.food:
				self.score+=1
				self.moves = 0
				place_food()
				self.body.insert(0, [row,col])
			else:
				self.body.pop()
	## You are free to define more sensing options to the snake

	def turn_left(self):

	def turn_right(self):


	def changeDirectionUp(self):
		self.direction = S_UP

	def changeDirectionRight(self):
		self.direction = S_RIGHT

	def changeDirectionDown(self):
		self.direction = S_DOWN

	def changeDirectionLeft(self):
		self.direction = S_LEFT

	def snakeHasCollided(self):
		self.hit = False
		if self.body[0][0] == 0 or self.body[0][0] == (YSIZE-1) or self.body[0][1] == 0 or self.body[0][1] == (XSIZE-1): self.hit = True
		if self.body[0] in self.body[1:]: self.hit = True
		return( self.hit )

	def sense_wall_ahead(self):
		self.getAheadLocation()
		return( self.ahead[0] == 0 or self.ahead[0] == (YSIZE-1) or self.ahead[1] == 0 or self.ahead[1] == (XSIZE-1) )

	def sense_body_ahead(self):
		self.getAheadLocation()
		return (self.ahead in self.body)


	def sense_food_ahead(self):
		self.getAheadLocation()
		return self.ahead in self.food

	def sense_danger_ahead(self):
		self.getAheadLocation()
		return (self.ahead in self.body) or (self.ahead[0]<0) or (self.ahead[1]<0) or (self.ahead[0]>YSIZE) or (self.ahead[0]>XSIZE)


	def if_body_ahead(self, out1, out2):
		return partial(if_then_else, self.sense_body_ahead, out1, out2)

	def if_food_ahead(self, out1, out2):
		return partial(if_then_else, self.send_food_ahead, out1, out2)


	def if_wall_ahead(self, out1, out2):
		return partial(if_then_else, self.sense_wall_ahead, out1, out2)

	def if_tail_ahead(self, out1, out2):
		return partial(if_then_else, self.sense_tail_ahead, out1, out2)

	def sense_tail_ahead(self):
		self.getAheadLocation()
		return self.ahead in self.body


snake = SnakePlayer()

pset = gp.PrimitiveSet("MAIN", 0)
# pset.addPrimitive(operator.and_, 2, name="aNd")
# pset.addPrimitive(operator.or_, 2, name="Or")
# pset.addPrimitive(operator.not_, 2, name="not")
pset.addPrimitive(prog2, 2)
pset.addPrimitive(prog3, 3)

pset.addPrimitive(snake.if_food_ahead, 2, name="if_food_ahead")
pset.addPrimitive(snake.if_tail_ahead, 2, name="if_body_ahead")
pset.addPrimitive(snake.if_wall_ahead, 2, name="if_wall_ahead")
pset.addPrimitive(snake.turn_left, 1, name="turn_left")
pset.addPrimitive(snake.turn_right, 1, name="turn_left")
pset.addTerminal(snake.move_forward)






creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)



toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

# This outline function provides partial code for running the game with an evolved agent
# There is no graphical output, and it runs rapidly, making it ideal for
# you need to modify it for running your agents through the game for evaluation
# which will depend on what type of EA you have used, etc.
# Feel free to make any necessary modifications to this section.
# Evaluation function for the ant
def evalArtificialSnake(individual):
    # Transform the tree expression to functionnal Python code
	print individual
	routine = gp.compile(individual, pset)

    # Run the generated routine

	snake.run(routine)
	return snake.score,

toolbox.register("evaluate", evalArtificialSnake)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)


stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
stats_size = tools.Statistics(len)
mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
mstats.register("avg", numpy.mean)
mstats.register("std", numpy.std)
mstats.register("min", numpy.min)
mstats.register("max", numpy.max)



# This outline function is the same as runGame (see below). However,
# it displays the game graphically and thus runs slower
# This function is designed for you to be able to view and assess
# your strategies, rather than use during the course of evolution
def displayStrategyRun():
	global snake
	global pset

	routine = gp.compile(individual, pset)

	curses.initscr()
	win = curses.newwin(YSIZE, XSIZE, 0, 0)
	win.keypad(1)
	curses.noecho()
	curses.curs_set(0)
	win.border(0)
	win.nodelay(1)
	win.timeout(120)

	snake._reset()
	food = placeFood(snake)

	for f in food:
		win.addch(f[0], f[1], '@')

	timer = 0
	collided = False
	while not collided and not timer == ((2*XSIZE) * YSIZE):

		# Set up the display
		win.border(0)
		win.addstr(0, 2, 'Score : ' + str(snake.score) + ' ')
 		win.getch()

		## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##

		snake.updatePosition()

		if snake.body[0] in food:
			snake.score += 1
			for f in food: win.addch(f[0], f[1], ' ')
			food = placeFood(snake)
			for f in food: win.addch(f[0], f[1], '@')
			timer = 0
		else:
			last = snake.body.pop()
			win.addch(last[0], last[1], ' ')
			timer += 1 # timesteps since last eaten
		win.addch(snake.body[0][0], snake.body[0][1], 'o')

		collided = snake.snakeHasCollided()
		hitBounds = (timer == ((2*XSIZE) * YSIZE))

	curses.endwin()

	print collided
	print hitBounds
	raw_input("Press to continue...")

	return snake.score,


def main():
	global snake
	global pset

	## THIS IS WHERE YOUR CORE EVOLUTIONARY ALGORITHM WILL GO #
	random.seed(69)
	pop = toolbox.population(n=300)
	hof = tools.HallOfFame(5)
	pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.2, 100, stats=mstats,
                                       halloffame=hof, verbose=True)

	return pop, mstats, hof
main()
