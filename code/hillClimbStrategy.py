# -*- coding: utf-8 -*-
import random
import sys

sys.path.append('code')
from strategy import Strategy
from gameState import GameState
from controllers import PacController, RandomGhostController
from exprTree import Node, ExprTree


class HillClimbStrategy(Strategy):
    """
    Hill Climbing search strategy.
    """
    def __init__(self, experiment):
        self.pac_controllers = [None for _ in range(experiment.num_pacs)]
        self.ghost_controllers = [RandomGhostController(x) for x in range(experiment.num_ghosts)]
        self.experiment = experiment


    def execute_one_game(self, weights):
        """
        Execute one game / eval of a run.

        Initialize the Pac controller with the given weights.

        Return score.
        """
        # Pick a new map and set up a new game state.
        game_map = self.experiment.pre_loaded_maps[random.randint(0, 99)]
        self.experiment.world_data = []
        game_state = GameState(game_map,
                               self.experiment.pill_density,
                               self.experiment.time_multiplier,
                               self.experiment.fruit_spawning_probability,
                               self.experiment.fruit_score,
                               self.experiment.num_pacs,
                               self.experiment.num_ghosts)
        game_state.write_world_config(self.experiment.world_data)
        game_state.write_world_time_score(self.experiment.world_data)

        # Create a new Pac controller with a hard-coded expression tree
        # to add a weighted sum of G, P, W, and F.
        g_node = Node(expr = '*',
                      left = Node('constant', constant = weights[0]),
                      right = Node('G'))
        p_node = Node(expr = '*',
                      left = Node('constant', constant = weights[1]),
                      right = Node('P'))
        w_node = Node(expr = '*',
                      left = Node('constant', constant = weights[2]),
                      right = Node('W'))
        f_node = Node(expr = '*',
                      left = Node('constant', constant = weights[3]),
                      right = Node('F'))
        add1_node = Node(expr = '+', left = g_node, right = p_node)
        add2_node = Node(expr = '+', left = w_node, right = f_node)
        root_node = Node(expr = '+', left = add1_node, right = add2_node)
        self.pac_controllers[0] = PacController(0, ExprTree(root_node))

        # While the game isn't over, play game turns.
        game_over = False
        while (not game_over):
            game_over = game_state.play_turn(self.experiment.world_data,
                                             self.pac_controllers,
                                             self.ghost_controllers)

        return game_state.score


    def execute_one_run(self):
        """
        Execute one run of an experiment.

        Return highest score and its associated world and solution data
        for Pac and empty placeholder data for Ghost.
        """
        run_high_score = -2
        run_best_world_data = None
        run_best_solution = None

        # Hill Climbing method inspired heavily by https://en.wikipedia.org/wiki/Hill_climbing

        # Pac formula weights are random to start each run --
        # so over multiple runs, this method
        # is effectively Hill Climbing with Random Restarts
        weights = [random.uniform(-1.0, 1.0),
                   random.uniform(-1.0, 1.0),
                   random.uniform(-1.0, 1.0),
                   random.uniform(-1.0, 1.0)]

        # Initial step sizes
        step_sizes = [1.0, 1.0, 1.0, 1.0]

        # Acceleration value
        acceleration = 1.2

        # Candidate factors to be tests against each weight
        candidates = [-acceleration, -1.0/acceleration, 0, 1.0/acceleration, acceleration]

        # Run through the alloted number of evals, rather than checking for convergence.
        curr_eval = 0
        while (curr_eval < self.experiment.num_fitness_evals_per_run):
            step_high_score = -1
            step_best_solution = None
            step_best_world_data = None

            # For each weight element, find adjustment that gets best result
            for i in range(len(weights)):
                best_candidate = -1
                best_score = 0

                # Adjust current weight element with each candidate
                for j in range(len(candidates)):
                    weights[i] += (step_sizes[i] * candidates[j])
                    curr_score = self.execute_one_game(weights)
                    curr_eval += 1
                    weights[i] -= (step_sizes[i] * candidates[j])

                    # If this is best so far, save candidate
                    if (curr_score > best_score):
                        best_score = curr_score
                        best_candidate = j

                    # Save best score of this step
                    if (curr_score > step_high_score):
                        step_high_score = curr_score
                        step_best_solution = str(self.pac_controllers[0].tree.root)
                        step_best_world_data = self.experiment.world_data

                    # Save best of run (so far) for logging
                    if (step_high_score > run_high_score):
                        run_high_score = step_high_score
                        run_best_solution = step_best_solution
                        run_best_world_data = step_best_world_data
                        print('New run high score: ', step_high_score)
                        self.experiment.log_file.write(str(curr_eval) + '\t' \
                                                       + str(step_high_score) + '\n')

                # Adjust current step size element and weight element
                # If best result was with no step, adjust step size
                # with acceleration only
                if (candidates[best_candidate] == 0):
                    step_sizes[i] /= acceleration
                # Otherwise adjust step size by best candidate
                else:
                    weights[i] += (step_sizes[i] * candidates[best_candidate])
                    step_sizes[i] *= candidates[best_candidate]

            print(curr_eval, 'ev; i', i, 'sc', step_high_score,
                  'wt', ['%0.2f' % i for i in weights],
                  'st', ['%0.2f' % i for i in step_sizes])

        return run_high_score, run_best_world_data, run_best_solution, 0, None

