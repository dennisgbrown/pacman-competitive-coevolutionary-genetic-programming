# -*- coding: utf-8 -*-
import random
import copy
import traceback
import sys

sys.path.append('code')
from strategy import Strategy
from gameState import GameState
from controllers import PacController, RandomGhostController
from exprTree import Node, ExprTree


class GPStrategy(Strategy):
    """
    Genetic Programming search strategy.
    """
    def __init__(self, experiment):
        self.pac_controllers = [None for _ in range(experiment.num_pacs)]
        self.ghost_controllers = [RandomGhostController(x) for x in range(experiment.num_ghosts)]
        self.experiment = experiment

        self.ea_mu = 10
        self.ea_lambda = 5
        self.dmax = 5
        self.parent_selection = 'fitness_proportional_selection'
        self.overselection_top = 0.32
        self.p_m = 0.05
        self.survival_selection = 'truncation'
        self.tournament_size_for_survival_selection = 4
        self.parsimony_technique = 'size'
        self.pppc = 0.05  # parsimony pressure penalty coefficient
        self.parsimony_log_file_path = 'data/defaultParsimonyLog.txt'
        self.parsimony_log = None
        self.termination = 'number_of_evals'
        self.n_for_convergence = 10

        try:
            self.ea_mu = experiment.config_parser.getint('gp_options', 'mu')
            print('config: mu =', self.ea_mu)
        except:
            print('config: mu not specified; using', self.ea_mu)

        try:
            self.ea_lambda = experiment.config_parser.getint('gp_options', 'lambda')
            print('config: lambda =', self.ea_lambda)
        except:
            print('config: lambda not specified; using', self.ea_lambda)

        try:
            self.dmax = experiment.config_parser.getint('gp_options', 'dmax')
            print('config: dmax =', self.dmax)
        except:
            print('config: dmax not specified; using', self.dmax)

        try:
            self.parent_selection = experiment.config_parser.get('gp_options',
                                                                 'parent_selection').lower()
            print('config: parent_selection =', self.parent_selection)
        except:
            print('config: parent_selection not specified; using', self.parent_selection)

        if (self.parent_selection == 'overselection'):
            try:
                self.overselection_top = experiment.config_parser.getfloat('gp_options',
                                                                           'overselection_top')
                print('config: overselection_top =',
                      self.overselection_top)
            except:
                print('config: overselection_top not specified; using',
                      self.overselection_top)

        try:
            self.p_m = experiment.config_parser.getfloat('gp_options', 'p_m')
            print('config: p_m =', self.p_m)
        except:
            print('config: p_m not specified; using', self.p_m)

        try:
            self.survival_selection = experiment.config_parser.get('gp_options',
                                                                   'survival_selection').lower()
            print('config: survival_selection =', self.survival_selection)
        except:
            print('config: survival_selection not specified; using', self.survival_selection)

        if (self.survival_selection == 'k_tournament_without_replacement'):
            try:
                self.tournament_size_for_survival_selection = experiment.config_parser.getint(
                    'gp_options', 'tournament_size_for_survival_selection')
                print('config: tournament_size_for_survival_selection =',
                      self.tournament_size_for_survival_selection)
            except:
                print('config: tournament_size_for_survival_selection not specified; using',
                      self.tournament_size_for_survival_selection)

        try:
            self.parsimony_technique = experiment.config_parser.get('gp_options',
                                                                   'parsimony_technique').lower()
            print('config: parsimony_technique =', self.parsimony_technique)
        except:
            print('config: parsimony_technique not specified; using', self.parsimony_technique)

        try:
            self.pppc = experiment.config_parser.getfloat('gp_options', 'pppc')
            print('config: pppc =', self.pppc)
        except:
            print('config: pppc not specified; using', self.pppc)

        try:
            self.parsimony_log_file_path = experiment.config_parser.get('gp_options',
                                                                        'parsimony_log_file_path')
            print('config: parsimony_log_file_path =', self.parsimony_log_file_path)
        except:
            print('config: parsimony_log_file_path not properly specified; using', self.parsimony_log_file_path)

        try:
            self.termination = experiment.config_parser.get('gp_options',
                                                            'termination').lower()
            print('config: termination =', self.termination)
        except:
            print('config: termination not specified; using', self.termination)

        if (self.termination == 'convergence'):
            try:
                self.n_for_convergence = experiment.config_parser.getint('gp_options',
                                                                         'n_for_convergence')
                print('config: n_for_convergence =', self.n_for_convergence)
            except:
                print('config: n_for_convergence not specified; using', self.n_for_convergence)

        # Write configuration items to log file
        experiment.log_file.write('mu: ' + str(self.ea_mu) + '\n')
        experiment.log_file.write('lambda: ' + str(self.ea_lambda) + '\n')
        experiment.log_file.write('dmax: ' + str(self.dmax) + '\n')
        experiment.log_file.write('parent selection method: ' + self.parent_selection + '\n')
        if (self.parent_selection == 'overselection'):
            experiment.log_file.write('overselection top for parent selection: '
                                      + str(self.overselection_top) + '\n')
        experiment.log_file.write('probability of mutation p_m: ' + str(self.p_m) + '\n')
        experiment.log_file.write('survival selection method: ' + self.survival_selection + '\n')
        if (self.survival_selection == 'k_tournament_without_replacement'):
            experiment.log_file.write('tournament size for survival selection: '
                                      + str(self.tournament_size_for_survival_selection) + '\n')
        experiment.log_file.write('parsimony technique: ' + self.parsimony_technique + '\n')
        experiment.log_file.write('parsimony pressure penalty coefficient: ' + str(self.pppc) + '\n')
        experiment.log_file.write('parsimony log file: ' + self.parsimony_log_file_path + '\n')
        experiment.log_file.write('termination method: ' + self.termination + '\n')
        if (self.termination == 'convergence'):
            experiment.log_file.write('n evals for convergence: '
                                      + str(self.n_for_convergence) + '\n')

        # Open parsimony log
        try:
            self.parsimony_log = open(self.parsimony_log_file_path, 'w')
        except:
            print('config: problem with parsimony log file', self.parsimony_log_file_path)
            traceback.print_exc()
            return None


    def build_tree(self, node, depth, grow_or_full):
        """
        Recursively build an expression tree to the given depth using either
        the 'grow' or 'full' method.
        """
        # Randomly choose a new expression. If not at depth limit,
        # choose an inner node from a set that depends on method 'grow' or 'full'
        if (depth < self.dmax):
            # Grow selects from all functions and terminals at this depth
            if (grow_or_full == 'grow'):
                expr = (ExprTree.functions + ExprTree.pac_terminals) \
                    [random.randint(0, (len(ExprTree.functions) + len(ExprTree.pac_terminals) - 1))]
            # Full selects only from functions at this depth
            else:
                expr = ExprTree.functions[random.randint(0, len(ExprTree.functions) - 1)]
        # If depth is at Dmax, choose a terminal.
        else:
            expr = ExprTree.pac_terminals[random.randint(0, len(ExprTree.pac_terminals) - 1)]

        # Make a new tree node with this expression.
        node.expr = expr
        if (expr == 'constant'):
            node.constant = random.uniform(-10, 10)  # TO DO: parameterize
        node.depth = depth

        # If this node is a function, make its children and update
        # height and count of this node.
        if (expr in ExprTree.functions):
            node.left = Node()
            self.build_tree(node.left, depth + 1, grow_or_full)
            node.right = Node()
            self.build_tree(node.right, depth + 1, grow_or_full)

        return node


    def initialize_population(self, size):
        """
        Generate and return an initial population of expression trees
        using Ramped Half-and-Half
        """
        population = [None for _ in range(size)]

        for i in range(size):
            root = Node()
            # Full method
            if (random.random() < 0.5):
                self.build_tree(root, 0, 'full')
            # Grow method
            else:
                self.build_tree(root, 0, 'grow')

            population[i] = ExprTree(root)
            population[i].root.reset_metrics()

        return population


    def random_selection_without_replacement(self, population, num_to_select):
        """
        Return a selection made up of num_to_select randomly-
        selected individuals from the given population
        """
        if (len(population) < num_to_select):
            print('Stuck in random selection without replacement because',
                  len(population), 'insufficient to choose', num_to_select)

        random.shuffle(population)
        selection = population[0:num_to_select]
        return selection


    def fitness_proportional_selection(self, population, num_to_select):
        """
        Given a population, return a selection using Fitness Proportional Selection
        """
        selection = []
        probabilities = []

        # Find total fitness of population. Account for negative fitnesses
        # with an offset.
        min_fitness = population[0].fitness
        for individual in population:
            if (individual.fitness < min_fitness):
                min_fitness = individual.fitness
        offset = 0
        if (min_fitness < 0):
            offset = abs(min_fitness)
        total_fitness = 0
        for individual in population:
            total_fitness += (individual.fitness + offset)

        # If total fitness is nonzero, good to go.
        if (total_fitness != 0):
            # Calculate probability distribution
            accumulation = 0.0
            for individual in population:
                accumulation += ((individual.fitness + offset) / total_fitness)
                probabilities.append(accumulation)

            # Build new population using roulette wheel algorithm
            while (len(selection) < num_to_select):
                randval = random.random()
                curr_member = 0
                while (probabilities[curr_member] < randval):
                    curr_member += 1
                if (curr_member > (len(population) - 1)):
                    curr_member = len(population) - 1
                selection.append(population[curr_member])

        # Edge case: If total_fitness == 0, then just pick from population
        # with uniform probability, because the roulette wheel can't
        # handle having an infinite number of 0-width wedges.
        else:
            selection = self.random_selection_without_replacement(population, num_to_select)

        return selection


    def overselection(self, population, num_to_select):
        """
        Select 80% from the top x% of the population rnaked by fitness,
        and 20% from the rest of the population.
        """
        # Sort the population by decreasing fitness
        population = sorted(population, key = lambda item: item.fitness,
                            reverse = True)

        # Find the split point and identify top and bottom populations
        split = int(len(population) * self.overselection_top)
        top = population[0:split]
        bottom = population[split:len(population) - 1]

        # Randomly build the new population with 80% chance of choosing
        # from top and 20% chance of choosing from bottom
        selection = []
        while (len(selection) < num_to_select):
            if (random.random() < 0.8):
                selection.append(top[random.randint(0, len(top) - 1)])
            else:
                selection.append(bottom[random.randint(0, len(bottom) - 1)])

        return selection


    def k_tournament_selection_without_replacement(self, population,
                                                   tournament_size, num_to_select):
        """
        Given a population, return a selection using k-tournament Selection
        without replacement
        """
        if (len(population) < num_to_select):
            print('Stuck in k-tournament selection without replacement because',
                  len(population), 'insufficient to choose', num_to_select)

        selection = []
        selected_indices = []

        while (len(selection) < num_to_select):
            # Pick tournament contestants
            k_contestants = []
            k_indices = []

            # If we can't fill a tournament with unselected individuals,
            # reduce tournament size to what's left
            if ((len(population) - len(selected_indices)) < tournament_size):
                tournament_size = len(population) - len(selected_indices)

            while (len(k_contestants) < tournament_size):
                # Pick a contestant
                selected_index = random.randint(0, len(population) - 1)
                selected_contestant = population[selected_index]

                # Add contestant if it's not already in tournament AND has
                # never been selected
                if ((k_indices.count(selected_index) == 0)
                    and (selected_indices.count(selected_index) == 0)):
                    k_contestants.append((selected_contestant, selected_index))
                    k_indices.append(selected_index)

            # Choose the best-rated contestant if at least one exists.
            if (len(k_contestants) > 0):
                k_contestants = sorted(k_contestants, key=lambda item: item[0].fitness, reverse=True)
                selection.append(k_contestants[0][0])
                selected_indices.append(k_contestants[0][1])

        return selection


    def truncation_selection(self, population, num_to_select):
        """
        Truncation selection. Sort the population and select the top individuals.
        """
        sorted_population = sorted(population, key=lambda item: item.fitness, reverse=True)
        selection = []
        for curr_individual in range(self.ea_mu):
            selection.append(sorted_population[curr_individual])
        return selection


    def select_parents(self, population):
        """
        Given a population, return a mating pool using the configured method.
        """
        if (self.parent_selection == "fitness_proportional_selection"):
            return self.fitness_proportional_selection(population,
                                                       self.ea_lambda)
        elif (self.parent_selection == "overselection"):
            return self.overselection(population, self.ea_lambda)
        else:
            print("Unknown parent selection method:", self.parent_selection)
            sys.exit(1)


    def mutate(self, parent):
        """
        Given a parent, return a mutated offspring
        """
        # Start with a copy of the parent
        offspring = copy.deepcopy(parent)

        # Randomly pick a node in the expression tree
        selected_node = offspring.root.find_nth_node(random.randint(1, offspring.root.size))

        # Build a new (sub)tree there. Arbitrarily choose 'grow' method.
        self.build_tree(selected_node, selected_node.depth, 'grow')

        # Reset the tree metrics we just screwed up
        offspring.root.reset_metrics()

        return offspring


    def recombine(self, parent1, parent2):
        """
        Given two parents, return two recombined offspring.
        """
        # Start with copies of the parents
        offspring1 = copy.deepcopy(parent1)
        offspring2 = copy.deepcopy(parent2)

        # Randomly pick nodes from each tree and swap them.
        match_found = False
        while (not(match_found)):
            # Pick a node in each tree
            selected_node1 = offspring1.root.find_nth_node(random.randint(1, offspring1.root.size))
            selected_node2 = offspring2.root.find_nth_node(random.randint(1, offspring2.root.size))

            # If the swap would cause either offspring to exceed Dmax,
            # try again.
            # NOTE: This check is disabled. Let the offspring grow large
            # and let parsimony pressure do its thing.
            # if (((selected_node1.depth + selected_node2.height) > self.dmax)
            #     or ((selected_node2.depth + selected_node1.height) > self.dmax)):
            #     continue

            # Match found -- make swap
            temp_node = Node()
            temp_node.copy(selected_node1)
            selected_node1.copy(selected_node2)
            selected_node2.copy(temp_node)
            match_found = True

        # Reset the tree metrics we just screwed up
        offspring1.root.reset_metrics()
        offspring2.root.reset_metrics()

        return [offspring1, offspring2]


    def recombine_mutate(self, parents):
        """
        Given a set of parents, return a set of offpsring of equal size
        created through stochastic choice of mutation or recombination
        """
        offspring = []

        # Walk through parents list either mutating or pair-wise recombining
        # to create offspring
        parent_counter = 0
        while (len(offspring) < len(parents)):
            # Mutate if random value within probability of mutation
            # OR if we only have 1 parent left
            if ((random.random() < self.p_m)
                or (parent_counter == (len(parents) - 1))):
                offspring.append(self.mutate(parents[parent_counter]))
                parent_counter += 1
            # Otherwise, recombine
            else:
                offspring += self.recombine(parents[parent_counter],
                                            parents[parent_counter + 1])
                parent_counter += 2

        return offspring


    def select_survivors(self, population):
        """
        Given a population, return a selection of survivors using the
        configured method.
        """
        # print('select', self.ea_mu, 'from', len(population))
        if (self.survival_selection == 'truncation'):
            return self.truncation_selection(population, self.ea_mu)
        elif (self.survival_selection == 'k_tournament_without_replacement'):
            return self.k_tournament_selection_without_replacement(population,
                                                                   self.tournament_size_for_survival_selection,
                                                                   self.ea_mu)
        else:
            print('Unknown parent selection method:', self.survival_selection)
            exit(1)


    def execute_one_game(self, pac_expr_tree):
        """
        Execute one game / eval of a run given experiment data
        and the root of an expression tree for controlling Pac.

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

        # Create a new Pac controller
        self.pac_controllers[0] = PacController(0, pac_expr_tree)

        # While the game isn't over, play game turns.
        game_over = False
        while (not game_over):
            game_over = game_state.play_turn(self.experiment.world_data,
                                             self.pac_controllers,
                                             self.ghost_controllers)

        # Implement parsimony pressure
        fitness = 0
        if (self.parsimony_technique == 'size'):
            fitness = game_state.score - (self.pppc * pac_expr_tree.root.size)
        else:
            fitness = game_state.score - (self.pppc * pac_expr_tree.root.height)

        return fitness, game_state.score


    def execute_one_run(self):
        """
        Execute one run of an experiment.

        Return highest score and its associated world and solution data
        for Pac and empty placeholder data for Ghost.
        """
        run_high_score = -1
        run_best_world_data = None
        run_best_solution = None
        evals_with_no_change = 0

        self.parsimony_log.write('\nRun\n')

        # Initialize the population
        population = self.initialize_population(self.ea_mu)
        eval_count = 0
        for individual in population:
            individual.fitness, individual.score = self.execute_one_game(individual)
            individual.world_data = self.experiment.world_data
            eval_count += 1

            # Provide status message every nth evaluation.
            if ((eval_count % 10) == 0):
                print('\r', eval_count, 'evals', end =" ")

        # Run generation after generation until we hit termination condition
        # and break out of the loop
        while (True):

            # Update generation max & avg score, tree height, and tree size
            gen_high_fitness = float('-inf')
            gen_high_score = -1
            gen_fitness_total = 0
            gen_score_total = 0
            gen_best_world_data = None
            gen_best_solution = None
            gen_max_tree_height = -1
            gen_tree_height_total = 0
            gen_max_tree_size = -1
            gen_tree_size_total = 0
            for individual in population:
                gen_fitness_total += individual.fitness
                if (individual.fitness > gen_high_fitness):
                    gen_high_fitness = individual.fitness
                gen_score_total += individual.score
                if (individual.score > gen_high_score):
                    gen_high_score = individual.score
                    gen_best_world_data = individual.world_data
                    gen_best_solution = str(individual.root)
                gen_tree_height_total += individual.root.height
                if (individual.root.height > gen_max_tree_height):
                    gen_max_tree_height = individual.root.height
                gen_tree_size_total += individual.root.size
                if (individual.root.size > gen_max_tree_size):
                    gen_max_tree_size = individual.root.size

            # Update log
            self.experiment.log_file.write(str(eval_count) + '\t' \
                                          + str(gen_score_total / len(population)) + '\t'
                                          + str(gen_high_score) + '\n')

            # Update parsimony log
            self.parsimony_log.write(str(eval_count) + '\t' \
                                     + str(gen_tree_height_total / len(population)) + '\t'
                                     + str(gen_max_tree_height) + '\t'
                                     + str(gen_tree_size_total / len(population)) + '\t'
                                     + str(gen_max_tree_size) + '\t'
                                     + str(gen_fitness_total / len(population)) + '\t'
                                     + str(gen_high_fitness) + '\n')

            # Check and handle new run high fitness
            if (gen_high_score > run_high_score):
                run_high_score = gen_high_score
                print('New run high score: ', run_high_score)
                run_best_world_data = gen_best_world_data
                run_best_solution = gen_best_solution

            # Check for termination
            if (self.termination == 'number_of_evals'):
                if (eval_count >= self.experiment.num_fitness_evals_per_run):
                    break
            elif (self.termination == 'convergence'):
                if (evals_with_no_change >= self.n_for_convergence):
                    print('CONVERGED at', eval_count, 'evals')
                    break
            else:
                print('Unknown termination method:', self.termination)
                sys.exit(1)

            # Not terminating? Let's proceed!

            # Select parents
            parents = self.select_parents(population)

            # Recombine and/or mutate
            offspring = self.recombine_mutate(parents)

            # Evaluate offspring
            for individual in offspring:
                individual.fitness, individual.score = \
                    self.execute_one_game(individual)
                individual.world_data = self.experiment.world_data

                # Update termination variables
                eval_count += 1
                if (individual.fitness <= gen_high_fitness):
                    evals_with_no_change += 1
                else:
                    evals_with_no_change = 0

                # Provide status message every nth evaluation.
                if ((eval_count % 10) == 0):
                    print('\r', eval_count, 'evals', end =" ")

            # Survival selection
            population += offspring
            population = self.select_survivors(population)

        return run_high_score, run_best_world_data, run_best_solution, 0, None

