# -*- coding: utf-8 -*-
import random
import sys

sys.path.append('code')
from strategy import Strategy
from gameState import GameState
from controllers import PacController, RandomGhostController
from exprTree import Node, ExprTree


class RandomStrategy(Strategy):
    """
    Random search strategy.
    """
    def __init__(self, experiment):
        self.pac_controllers = [None for _ in range(experiment.num_pacs)]
        self.ghost_controllers = [RandomGhostController(x) for x in range(experiment.num_ghosts)]
        self.experiment = experiment


    def execute_one_game(self):
        """
        Execute one game / eval of a run. Return score.
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
                      left = Node('constant', constant = random.uniform(-1, 1)),
                      right = Node('G'))
        p_node = Node(expr = '*',
                      left = Node('constant', constant = random.uniform(-1, 1)),
                      right = Node('P'))
        w_node = Node(expr = '*',
                      left = Node('constant', constant = random.uniform(-1, 1)),
                      right = Node('W'))
        f_node = Node(expr = '*',
                      left = Node('constant', constant = random.uniform(-1, 1)),
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
        run_high_score = -1
        run_best_world_data = None
        run_best_solution = None

        # Execute prescribed number of evaluations (games)
        for curr_eval in range(1, self.experiment.num_fitness_evals_per_run + 1):

            # Provide status message every nth evaluation.
            if ((curr_eval % 10) == 0):
                print('\r', curr_eval, 'evals', end =" ")

            # Play a game
            score = self.execute_one_game()

            # Check and handle new high score
            if (score > run_high_score):
                run_high_score = score
                print('New run high score: ', run_high_score)
                self.experiment.log_file.write(str(curr_eval) + '\t' \
                                               + str(run_high_score) + '\n')
                run_best_world_data = self.experiment.world_data
                run_best_solution = str(self.pac_controllers[0].tree.root)

        return run_high_score, run_best_world_data, run_best_solution, 0, None

