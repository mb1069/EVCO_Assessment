#!/usr/bin/env python
#
#   Copyright (C) 2008  Don Smiley  ds@sidorof.com

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>

#   See the LICENSE file included in this archive
#

"""
This sample program shows a simple use of grammatical evolution.  The
evolutionary process drives the fitness values towards zero.

"""

from pyneurgen.grammatical_evolution import GrammaticalEvolution
from pyneurgen.fitness import FitnessElites, FitnessTournament
from pyneurgen.fitness import ReplacementTournament, MAX, MIN, CENTER
import curses
import random
import operator
import numpy


S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
XSIZE, YSIZE = 14, 14
INIT_SIZE = -1

# NOTE: YOU MAY NEED TO ADD A CHECK THAT THERE ARE ENOUGH SPACES LEFT FOR
# THE FOOD (IF THE TAIL IS VERY LONG)
NFOOD = 1
NUM_EVALS = 3

def run_debug(snake):


    total_score = 0
    for run in range(0,NUM_EVALS):
        snake._reset()
        food = place_food(snake)
        timer = 0


        while not snake.snake_has_collided() and not timer == XSIZE * YSIZE:
            ## EXECUTE THE SNAKE'S BEHAVIOUR HERE ##
            print snake.direction, snake.body[0], snake.sense_danger_ahead()
            snake.decide()
            print snake.direction
            snake.updatePosition()
            if snake.body[0] in food:
                snake.score += 1
                food = place_food(snake)
                timer = 0
            else:
                snake.body.pop()
                timer += 1  # timesteps since last eaten
        if snake.score==0:
            snake.score = -(abs(snake.body[0][0] - food[0][0]) + abs(snake.body[0][1] - food[0][1]))
        total_score += snake.score


    collided = snake.snake_has_collided()
    hitBounds = snake.body[0][0] == 0 or snake.body[0][0] == (
                    YSIZE - 1) or snake.body[0][1] == 0 or snake.body[0][1] == (XSIZE - 1)
    print "Collided: ", collided
    print "Hit wall: ", hitBounds
    return total_score/NUM_EVALS,

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
        tile = self.get_left_location()
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

    def if_wall_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_wall_ahead, out1, out2)

    def if_food_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_food_ahead, out1, out2)

    def if_tail_ahead(self, out1, out2):
        return partial(if_then_else, self.sense_tail_ahead, out1, out2)

    def if_danger_right(self, out1, out2):
        return partial(if_then_else, self.sense_danger_right, out1, out2)

    def if_danger_left(self, out1, out2):
        return partial(if_then_else, self.sense_danger_left, out1, out2)

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
        return partial(if_then_else, self.sense_food_down, out1, out2)

    def if_moving_up(self, out1, out2):
        return partial(if_then_else, self.sense_moving_up, out1, out2)

    def if_moving_right(self, out1, out2):
        return partial(if_then_else, self.sense_moving_right, out1, out2)

    def if_moving_down(self, out1, out2):
        return partial(if_then_else, self.sense_moving_down, out1, out2)

    def if_moving_left(self, out1, out2):
        return partial(if_then_else, self.sense_moving_left, out1, out2)

def is_tile_empty(snake, food, tile):
    return not ((tile in snake.body) or (tile in food))

# This function places a food item in the environment
# TODO convert to using a spiral search around the point
def place_food(snake):
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




def runGame(individual):
    global snake
    global pset

    routine = gp.compile(individual, pset)

    total_score = 0
    for run in range(0,NUM_EVALS):
        snake._reset()
        food = place_food(snake)
        timer = 0


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
        if snake.score==0:
            snake.score = -(abs(snake.body[0][0] - food[0][0]) + abs(snake.body[0][1] - food[0][1]))
        total_score += snake.score
    return total_score/NUM_EVALS,


# <if>                ::= <expr> if <condition> else <expr>
# <condition>         ::= snake.sense_danger_ahead()

bnf =   """
<expr>              ::= <terminal>

<terminal>          ::= snake.turn_left() | snake.turn_right() | snake.go_straight()
<S>                 ::=
snake = SnakePlayer()
def move():
    <if>
snake.decide = move
self.set_bnf_variable('<fitness>', 40)
return snake
        """

bnf =   """
<expr>              ::= <expr> <biop> <expr> | <uop> <expr> | <real> |
                        math.log(abs(<expr>)) | <pow> | math.sin(<expr> )|
                        value | (<expr>)
<biop>              ::= + | - | * | /
<uop>               ::= + | -
<pow>               ::= pow(<expr>, <real>)
<plus>              ::= +
<minus>             ::= -
<real>              ::= <int-const>.<int-const>
<int-const>         ::= <int-const> | 1 | 2 | 3 | 4 | 5 | 6 |
                        7 | 8 | 9 | 0
<S>                 ::=
import math
total = 0.0
for i in xrange(100):
    value = float(i) / float(100)
    total += abs(<expr> - pow(value, 3))
fitness = total
self.set_bnf_variable('<fitness>', 40)
        """


ges = GrammaticalEvolution()

ges.set_bnf(bnf)
ges.set_genotype_length(start_gene_length=40,
                        max_gene_length=50)
ges.set_population_size(300)
ges.set_wrap(True)

ges.set_max_generations(100)
ges.set_fitness_type(MAX, 100.0)

ges.set_max_program_length(500)
ges.set_timeouts(10, 120)
ges.set_fitness_fail(0.0)

ges.set_mutation_rate(.025)
ges.set_fitness_selections(
    FitnessElites(ges.fitness_list, .05),
    FitnessTournament(ges.fitness_list, tournament_size=2))
ges.set_max_fitness_rate(.5)

ges.set_crossover_rate(.2)
ges.set_children_per_crossover(2)
ges.set_mutation_type('m')
ges.set_max_fitness_rate(.25)

ges.set_replacement_selections(
        ReplacementTournament(ges.fitness_list, tournament_size=3))

ges.set_maintain_history(True)
ges.create_genotypes()
print ges.run()
print ges.fitness_list.sorted()
print
print
gene = ges.population[ges.fitness_list.best_member()]
print gene.get_program()
print gene.compute_fitness()
# snake = gene.get_program
# run_debug(snake)