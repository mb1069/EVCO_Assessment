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
from snake import SnakePlayer

S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
XSIZE, YSIZE = 14, 14

INIT_SIZE = -1

# NOTE: YOU MAY NEED TO ADD A CHECK THAT THERE ARE ENOUGH SPACES LEFT FOR
# THE FOOD (IF THE TAIL IS VERY LONG)
NFOOD = 1
NUM_EVALS = 3
generations = 1000
population = 400

# <if>                ::= <expr> if <condition> else <expr>
# <condition>         ::= snake.sense_danger_ahead()

bnf =   """
<expr>              ::= <terminal> | <if> 
<if>                ::= (<expr> if <condition> else <expr>)
<terminal>          ::= snake.turn_left() | snake.turn_right() | snake.go_straight()
<condition>         ::= snake.sense_moving_left() | snake.sense_moving_down() | snake.sense_moving_up() | snake.sense_moving_right() | snake.sense_food_ahead() | snake.sense_danger_ahead() | snake.sense_food_above() | snake.sense_food_right() | snake.sense_danger_2_ahead()
<S>                 ::=
from snake import SnakePlayer, run_game, run_debug, display_run
S_UP, S_RIGHT, S_DOWN, S_LEFT = 0, 1, 2, 3
XSIZE, YSIZE = 14, 14

snake = SnakePlayer()
def move():
    <if>
snake.decide = move
fitness = run_game(snake)

try:
    self.set_bnf_variable('<fitness>', fitness)
except NameError:
    display_run(snake)
    pass
        """

# bnf =   """
# <expr>              ::= <expr> <biop> <expr> | <uop> <expr> | <real> |
#                         math.log(abs(<expr>)) | <pow> | math.sin(<expr> )|
#                         value | (<expr>)
# <biop>              ::= + | - | * | /
# <uop>               ::= + | -
# <pow>               ::= pow(<expr>, <real>)
# <plus>              ::= +
# <minus>             ::= -
# <real>              ::= <int-const>.<int-const>
# <int-const>         ::= <int-const> | 1 | 2 | 3 | 4 | 5 | 6 |
#                         7 | 8 | 9 | 0
# <S>                 ::=
# import math
# total = 0.0
# for i in xrange(100):
#     value = float(i) / float(100)
#     total += abs(<expr> - pow(value, 3))
# fitness = total
# self.set_bnf_variable('<fitness>', 40)
#         """

snake = SnakePlayer()

ges = GrammaticalEvolution()

ges.set_bnf(bnf)
ges.set_genotype_length(start_gene_length=40,
                        max_gene_length=100)
ges.set_population_size(population)
ges.set_wrap(True)

ges.set_max_generations(generations)
ges.set_fitness_type(MAX, 100.0)

ges.set_max_program_length(5000)
ges.set_timeouts(10, 1200)
ges.set_fitness_fail(-100.0)

ges.set_mutation_rate(.3)
ges.set_fitness_selections(
    FitnessElites(ges.fitness_list, .03),
    FitnessTournament(ges.fitness_list, tournament_size=2))
ges.set_max_fitness_rate(.5)

ges.set_crossover_rate(.5)
ges.set_children_per_crossover(2)
ges.set_mutation_type('m')
ges.set_max_fitness_rate(.99)

ges.set_replacement_selections(
        ReplacementTournament(ges.fitness_list, tournament_size=3))

ges.set_maintain_history(True)
ges.create_genotypes()
ges.run()
print ges.get_fitness_history()
print
print
gene = ges.population[ges.fitness_list.best_member()]
print gene.get_program()
print

print gene.compute_fitness()

inp = raw_input("display best? ")
if len(inp)>0:
    tmp = compile(gene.get_program(), 'fakemodule', 'exec')
    exec(tmp)
