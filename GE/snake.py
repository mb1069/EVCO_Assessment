from pyneurgen.grammatical_evolution import GrammaticalEvolution
from pyneurgen.fitness import FitnessElites, FitnessTournament
from pyneurgen.fitness import ReplacementTournament, MAX, MIN, CENTER
import curses
import random
import operator
import numpy

S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
XSIZE, YSIZE = 14, 14
NUM_EVALS = 1
NFOOD = 1

class SnakePlayer(list):

    def __init__(self):
        self.direction = S_RIGHT
        self.body = [[4, 10], [4, 9], [4, 8], [4, 7], [4, 6],
                     [4, 5], [4, 4], [4, 3], [4, 2], [4, 1], [4, 0]]
        INIT_SIZE = len(self.body)
        self.score = 0
        self.ahead = []
        self.food = []

    def _reset(self):
        self.direction = S_RIGHT
        self.body[:] = [[4, 10], [4, 9], [4, 8], [4, 7], [4, 6],
                        [4, 5], [4, 4], [4, 3], [4, 2], [4, 1], [4, 0]]
        self.score = 0
        self.ahead = []
        self.food = []

    def is_tile_dangerous(self, tile):
        return (tile in self.body) or (tile[1]==0) or (tile[1]==XSIZE-1) or (tile[0]==0) or (tile[0]==YSIZE-1)

    def get_right_location(self):
        tile = [self.body[0][0], self.body[0][1]]
        if self.direction == S_LEFT:
            tile[0]-=1
        elif self.direction == S_UP:
            tile[1]+=1
        elif self.direction == S_RIGHT:
            tile[0]+=1
        elif self.direction == S_DOWN:
            tile[1]-=1
        return tile

    def get_left_location(self):
        tile = [self.body[0][0], self.body[0][1]]
        if self.direction == S_LEFT:
            tile[0]+=1
        elif self.direction == S_UP:
            tile[1]-=1
        elif self.direction == S_RIGHT:
            tile[0]-=1
        elif self.direction == S_DOWN:
            tile[1]+=1
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
        self.body.insert(0, self.ahead)

    def decide(self):
        pass

    # You are free to define more sensing options to the snake

    def turn_left(self):
        self.direction = (self.direction - 1) % 4
    # You are free to define more sensing options to the snake

    def turn_right(self):
        self.direction = (self.direction + 1) % 4

    def go_straight(self):
        pass

    def snake_has_collided(self):
        self.hit = False
        if self.body[0][0] == 0 or self.body[0][0] == (
                    YSIZE - 1) or self.body[0][1] == 0 or self.body[0][1] == (XSIZE - 1):
            self.hit = True
        if self.body[0] in self.body[1:]:
            self.hit = True
        return (self.hit)

    def sense_danger_right(self):
        tile = self.get_right_location()
        return self.is_tile_dangerous(tile)

    def sense_danger_left(self):
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
        tile = self.get_right_location()
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )
    
    def sense_wall_2_ahead(self):
        tile = self.get_ahead_2_location()
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )

    def sense_wall_2_left(self):
        tile = self.get_left_location(2)
        return( tile[0] == 0 or tile[0] == (YSIZE-1) or tile[1] == 0 or tile[1] == (XSIZE-1) )

    def sense_moving_up(self):
        return self.direction == S_UP

    def sense_moving_right(self):
        return self.direction == S_RIGHT

    def sense_moving_down(self):
        return self.direction == S_DOWN

    def sense_moving_left(self):
        return self.direction == S_LEFT

def run_game(snake):


    total_score = 0
    total_steps = 0
    for run in range(0,NUM_EVALS):
        snake._reset()
        food = place_food(snake)
        timer = 0

        tour = set()
        tours = 0
        steps = 0 
        while not snake.snake_has_collided() and not timer == XSIZE * YSIZE:
            ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
            snake.decide()
            snake.updatePosition()
            if snake.body[0] in food:
                snake.score += 1
                food = place_food(snake)
                timer = 0
            else:
                snake.body.pop()
                timer += 1  # timesteps since last eaten
            steps+=1
            tour.add(str(snake.body[0]))
            if len(tour)==((XSIZE-2)*(YSIZE-2)):
                tour.clear()
                tours+=1
        total_steps += steps
        total_score += snake.score + (steps/100)
    total_score/=NUM_EVALS
    # return (max(len(tour)/((XSIZE-2)*(YSIZE-2)), tours), total_score/NUM_EVALS)
    return (float(len(tour))/((XSIZE-2)*(YSIZE-2)))+tours + (total_score if total_score>5 else 0)


def is_tile_empty(snake, food, tile):
    return not ((tile in snake.body) or (tile in food))

# This function places a food item in the environment
# TODO convert to using a spiral search around the point
def place_food(snake):
    S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
    XSIZE, YSIZE = 14, 14
    food = []
    while len(food) < NFOOD:
        randx = random.randint(1, (XSIZE - 2))
        randy = random.randint(1, (YSIZE - 2))
        rand_food_tile = [randy, randx]


        if is_tile_empty(snake, food, rand_food_tile):
            food.insert(0, rand_food_tile)
        else:
            closest_free_tile = rand_food_tile
            min_d = -1
            for x in range(XSIZE-1):
                for y in range(YSIZE-1):
                    # print x,y, is_tile_empty(snake, food, [y,x])
                    if is_tile_empty(snake, food, [y,x]):
                        d = numpy.sqrt(numpy.power(y-randy,2) + numpy.power(x-randx,2))
                        if d<min_d:
                            min_d = d
                            closest_free_tile[0] = y
                            closest_free_tile[1] = x
            food.insert(0, closest_free_tile)

    snake.food = food  # let the snake know where the food is
    return (food)

def run_debug(snake):
    S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
    XSIZE, YSIZE = 14, 14
    total_score = 0
    snake._reset()
    food = place_food(snake)
    timer = 0

    prev_direction = snake.direction
    while not snake.snake_has_collided() and not timer == XSIZE * YSIZE:
        ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
        if snake.sense_danger_ahead():
            print "Danger ahead", snake.direction, snake.body[0], snake.sense_danger_ahead()
        if snake.direction != prev_direction:
            print "Turned", snake.direction, snake.body[0], snake.sense_danger_ahead()            
            prev_direction = snake.direction
        snake.decide()
        snake.updatePosition()
        if snake.body[0] in food:
            print "Got food: ", snake.body[0]
            snake.score += 1
            food = place_food(snake)
            print "Placed food: ", food
            timer = 0
        else:
            snake.body.pop()
            timer += 1  # timesteps since last eaten
    total_score += snake.score


    collided = snake.snake_has_collided()
    hitBounds = snake.body[0][0] == 0 or snake.body[0][0] == (
                    YSIZE - 1) or snake.body[0][1] == 0 or snake.body[0][1] == (XSIZE - 1)
    print "Collided: ", collided
    print "Hit wall: ", hitBounds
    print "Score: ", total_score
    return total_score/NUM_EVALS

# This outline function is the same as runGame (see below). However,
# it displays the game graphically and thus runs slower
# This function is designed for you to be able to view and assess
# your strategies, rather than use during the course of evolution
def display_run(snake):

    curses.initscr()
    win = curses.newwin(YSIZE, XSIZE, 0, 0)
    win.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    win.border(0)
    win.nodelay(1)
    win.timeout(120)

    snake._reset()
    food = place_food(snake)

    for f in food:
        win.addch(f[0], f[1], '@')

    timer = 0
    collided = False
    tmp = []
    while not collided and not timer == ((2 * XSIZE) * YSIZE):
        # Set up the display
        win.border(0)
        win.addstr(0, 2, 'Score : ' + str(snake.score) + ' ')
        win.getch()

        ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
        snake.decide()
        snake.updatePosition()

        if snake.body[0] in food:
            snake.score += 1
            for f in food:
                win.addch(f[0], f[1], ' ')
            food = place_food(snake)
            for f in food:
                win.addch(f[0], f[1], '@')
            timer = 0
        else:
            last = snake.body.pop()
            win.addch(last[0], last[1], ' ')
            timer += 1  # timesteps since last eaten
        win.addch(snake.body[0][0], snake.body[0][1], 'o')

        collided = snake.snake_has_collided()
        hitBounds = snake.body[0][0] == 0 or snake.body[0][0] == (
                    YSIZE - 1) or snake.body[0][1] == 0 or snake.body[0][1] == (XSIZE - 1)
    curses.endwin()
    print "Collided: ", collided
    print "Hit wall: ", hitBounds
    print "Score: ", snake.score
    raw_input("Press to continue...")

    return snake.score