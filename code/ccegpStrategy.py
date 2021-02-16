# -*- coding: utf-8 -*-
import random
import copy
import traceback
import numpy
import sys

sys.path.append('code')
from strategy import Strategy
from gameState import GameState
from controllers import PacController, GhostController
from exprTree import Node, ExprTree
from population import Population
from ciaoPlotter import CIAOPlotter


class CCEGPStrategy(Strategy):
    """
    Competitive Co-Evolutionary Genetic Programming search strategy.
    """
    def __init__(self, experiment):
        self.experiment = experiment

        # Information for setting up and controlling the Pac population
        self.pac_controllers = [None for _ in range(experiment.num_pacs)]
        self.pac_mu = 10
        self.pac_lambda = 5
        self.pac_dmax_init = 5
        self.pac_dmax_overall = 5
        self.pac_parent_selection = 'fitness_proportional_selection'
        self.pac_overselection_top = 0.32
        self.pac_p_m = 0.05
        self.pac_survival_selection = 'truncation'
        self.pac_tournament_size_for_survival_selection = 4
        self.pac_parsimony_technique = 'size'
        self.pac_pppc = 0.05  # parsimony pressure penalty coefficient

        # Information for csetting up and ontrolling the Ghost population
        self.ghost_controllers = [None for _ in range(experiment.num_ghosts)]
        self.ghost_mu = 10
        self.ghost_lambda = 5
        self.ghost_dmax_init = 5
        self.ghost_dmax_overall = 5
        self.ghost_parent_selection = 'fitness_proportional_selection'
        self.ghost_overselection_top = 0.32
        self.ghost_p_m = 0.05
        self.ghost_survival_selection = 'truncation'
        self.ghost_tournament_size_for_survival_selection = 4
        self.ghost_parsimony_technique = 'size'
        self.ghost_pppc = 0.05  # parsimony pressure penalty coefficient

        # Logging and termination information
        self.ciao_file_path_root = 'data/defaultCIAOData'
        self.parsimony_log_file_path = 'data/defaultParsimonyLog.txt'
        self.parsimony_log = None
        self.termination = 'number_of_evals'
        self.n_for_convergence = 10

        # Parse config properties
        try:
            self.pac_mu = experiment.config_parser.getint('ccegp_options', 'pac_mu')
            print('config: pac_mu =', self.pac_mu)
        except:
            print('config: pac_mu not specified; using', self.pac_mu)

        try:
            self.pac_lambda = experiment.config_parser.getint('ccegp_options', 'pac_lambda')
            print('config: pac_lambda =', self.pac_lambda)
        except:
            print('config: pac_lambda not specified; using', self.pac_lambda)

        try:
            self.pac_dmax_init = experiment.config_parser.getint('ccegp_options', 'pac_dmax_init')
            print('config: pac_dmax_init =', self.pac_dmax_init)
        except:
            print('config: pac_dmax_init not specified; using', self.pac_dmax_init)

        try:
            self.pac_dmax_overall = experiment.config_parser.getint('ccegp_options', 'pac_dmax_overall')
            print('config: pac_dmax_overall =', self.pac_dmax_overall)
        except:
            print('config: pac_dmax_overall not specified; using', self.pac_dmax_overall)

        try:
            self.pac_parent_selection = experiment.config_parser.get('ccegp_options',
                                                                     'pac_parent_selection').lower()
            print('config: pac_parent_selection =', self.pac_parent_selection)
        except:
            print('config: pac_parent_selection not specified; using', self.pac_parent_selection)

        if (self.pac_parent_selection == 'overselection'):
            try:
                self.pac_overselection_top = experiment.config_parser.getfloat('ccegp_options',
                                                                               'pac_overselection_top')
                print('config: pac_overselection_top =',
                      self.pac_overselection_top)
            except:
                print('config: pac_overselection_top not specified; using',
                      self.pac_overselection_top)

        try:
            self.pac_p_m = experiment.config_parser.getfloat('ccegp_options', 'pac_p_m')
            print('config: pac_p_m =', self.pac_p_m)
        except:
            print('config: pac_p_m not specified; using', self.pac_p_m)

        try:
            self.pac_survival_selection = experiment.config_parser.get('ccegp_options',
                                                                       'pac_survival_selection').lower()
            print('config: pac_survival_selection =', self.pac_survival_selection)
        except:
            print('config: pac_survival_selection not specified; using', self.pac_survival_selection)

        if (self.pac_survival_selection == 'k_tournament_without_replacement'):
            try:
                self.pac_tournament_size_for_survival_selection = experiment.config_parser.getint(
                    'ccegp_options', 'pac_tournament_size_for_survival_selection')
                print('config: pac_tournament_size_for_survival_selection =',
                      self.pac_tournament_size_for_survival_selection)
            except:
                print('config: pac_tournament_size_for_survival_selection not specified; using',
                      self.pac_tournament_size_for_survival_selection)

        try:
            self.pac_parsimony_technique = experiment.config_parser.get('ccegp_options',
                                                                        'pac_parsimony_technique').lower()
            print('config: pac_parsimony_technique =', self.pac_parsimony_technique)
        except:
            print('config: pac_parsimony_technique not specified; using', self.pac_parsimony_technique)

        try:
            self.pac_pppc = experiment.config_parser.getfloat('ccegp_options', 'pac_pppc')
            print('config: pac_pppc =', self.pac_pppc)
        except:
            print('config: pac_pppc not specified; using', self.pac_pppc)

        try:
            self.ghost_mu = experiment.config_parser.getint('ccegp_options', 'ghost_mu')
            print('config: ghost_mu =', self.ghost_mu)
        except:
            print('config: ghost_mu not specified; using', self.ghost_mu)

        try:
            self.ghost_lambda = experiment.config_parser.getint('ccegp_options', 'ghost_lambda')
            print('config: ghost_lambda =', self.ghost_lambda)
        except:
            print('config: ghost_lambda not specified; using', self.ghost_lambda)

        try:
            self.ghost_dmax_init = experiment.config_parser.getint('ccegp_options', 'ghost_dmax_init')
            print('config: ghost_dmax_init =', self.ghost_dmax_init)
        except:
            print('config: ghost_dmax_init not specified; using', self.ghost_dmax_init)

        try:
            self.ghost_dmax_overall = experiment.config_parser.getint('ccegp_options', 'ghost_dmax_overall')
            print('config: ghost_dmax_overall =', self.ghost_dmax_overall)
        except:
            print('config: ghost_dmax_overall not specified; using', self.ghost_dmax_overall)

        try:
            self.ghost_parent_selection = experiment.config_parser.get('ccegp_options',
                                                                       'ghost_parent_selection').lower()
            print('config: ghost_parent_selection =', self.ghost_parent_selection)
        except:
            print('config: ghost_parent_selection not specified; using', self.ghost_parent_selection)

        if (self.ghost_parent_selection == 'overselection'):
            try:
                self.ghost_overselection_top = experiment.config_parser.getfloat('ccegp_options',
                                                                               'ghost_overselection_top')
                print('config: ghost_overselection_top =',
                      self.ghost_overselection_top)
            except:
                print('config: ghost_overselection_top not specified; using',
                      self.ghost_overselection_top)

        try:
            self.ghost_p_m = experiment.config_parser.getfloat('ccegp_options', 'ghost_p_m')
            print('config: ghost_p_m =', self.ghost_p_m)
        except:
            print('config: ghost_p_m not specified; using', self.ghost_p_m)

        try:
            self.ghost_survival_selection = experiment.config_parser.get('ccegp_options',
                                                                       'ghost_survival_selection').lower()
            print('config: ghost_survival_selection =', self.ghost_survival_selection)
        except:
            print('config: ghost_survival_selection not specified; using', self.ghost_survival_selection)

        if (self.ghost_survival_selection == 'k_tournament_without_replacement'):
            try:
                self.ghost_tournament_size_for_survival_selection = experiment.config_parser.getint(
                    'ccegp_options', 'ghost_tournament_size_for_survival_selection')
                print('config: ghost_tournament_size_for_survival_selection =',
                      self.ghost_tournament_size_for_survival_selection)
            except:
                print('config: ghost_tournament_size_for_survival_selection not specified; using',
                      self.ghost_tournament_size_for_survival_selection)

        try:
            self.ghost_parsimony_technique = experiment.config_parser.get('ccegp_options',
                                                                          'ghost_parsimony_technique').lower()
            print('config: ghost_parsimony_technique =', self.ghost_parsimony_technique)
        except:
            print('config: ghost_parsimony_technique not specified; using', self.ghost_parsimony_technique)

        try:
            self.ghost_pppc = experiment.config_parser.getfloat('ccegp_options', 'ghost_pppc')
            print('config: ghost_pppc =', self.ghost_pppc)
        except:
            print('config: ghost_pppc not specified; using', self.ghost_pppc)

        try:
            self.termination = experiment.config_parser.get('ccegp_options',
                                                            'termination').lower()
            print('config: termination =', self.termination)
        except:
            print('config: termination not specified; using', self.termination)

        if (self.termination == 'convergence'):
            try:
                self.n_for_convergence = experiment.config_parser.getint('ccegp_options',
                                                                         'n_for_convergence')
                print('config: n_for_convergence =', self.n_for_convergence)
            except:
                print('config: n_for_convergence not specified; using', self.n_for_convergence)

        try:
            self.ciao_file_path_root = experiment.config_parser.get('ccegp_options',
                                                                         'ciao_file_path_root')
            print('config: ciao_file_path_root =', self.ciao_file_path_root)
        except:
            print('config: ciao_file_path_root not properly specified; using', self.ciao_file_path_root)

        try:
            self.parsimony_log_file_path = experiment.config_parser.get('ccegp_options',
                                                                        'parsimony_log_file_path')
            print('config: parsimony_log_file_path =', self.parsimony_log_file_path)
        except:
            print('config: parsimony_log_file_path not properly specified; using', self.parsimony_log_file_path)

        # Set up populations
        self.pac_pop = Population('Pac', self.pac_mu, self.pac_lambda,
                                  self.pac_dmax_init, self.pac_dmax_overall,
                                  self.pac_parent_selection, self.pac_overselection_top,
                                  self.pac_p_m, self.pac_survival_selection,
                                  self.pac_tournament_size_for_survival_selection,
                                  self.pac_parsimony_technique, self.pac_pppc,
                                  ExprTree.functions, ExprTree.pac_terminals)
        self.ghost_pop = Population('Ghost', self.ghost_mu, self.ghost_lambda,
                                    self.ghost_dmax_init, self.ghost_dmax_overall,
                                    self.ghost_parent_selection, self.ghost_overselection_top,
                                    self.ghost_p_m, self.ghost_survival_selection,
                                    self.ghost_tournament_size_for_survival_selection,
                                    self.ghost_parsimony_technique, self.ghost_pppc,
                                    ExprTree.functions, ExprTree.ghost_terminals)

        # Write configuration items to log file
        experiment.log_file.write('pac_mu: ' + str(self.pac_mu) + '\n')
        experiment.log_file.write('pac_lambda: ' + str(self.pac_lambda) + '\n')
        experiment.log_file.write('pac_dmax_init: ' + str(self.pac_dmax_init) + '\n')
        experiment.log_file.write('pac_dmax_overall: ' + str(self.pac_dmax_overall) + '\n')
        experiment.log_file.write('pac_parent selection method: ' + self.pac_parent_selection + '\n')
        if (self.pac_parent_selection == 'overselection'):
            experiment.log_file.write('pac_overselection top for parent selection: '
                                      + str(self.pac_overselection_top) + '\n')
        experiment.log_file.write('pac_probability of mutation p_m: ' + str(self.pac_p_m) + '\n')
        experiment.log_file.write('pac_survival selection method: ' + self.pac_survival_selection + '\n')
        if (self.pac_survival_selection == 'k_tournament_without_replacement'):
            experiment.log_file.write('pac_tournament size for survival selection: '
                                      + str(self.pac_tournament_size_for_survival_selection) + '\n')
        experiment.log_file.write('pac_parsimony technique: ' + self.pac_parsimony_technique + '\n')
        experiment.log_file.write('pac_parsimony pressure penalty coefficient: ' + str(self.pac_pppc) + '\n')
        experiment.log_file.write('ghost_mu: ' + str(self.ghost_mu) + '\n')
        experiment.log_file.write('ghost_lambda: ' + str(self.ghost_lambda) + '\n')
        experiment.log_file.write('ghost_dmax_init: ' + str(self.ghost_dmax_init) + '\n')
        experiment.log_file.write('ghost_dmax_overall: ' + str(self.ghost_dmax_overall) + '\n')
        experiment.log_file.write('ghost_parent selection method: ' + self.ghost_parent_selection + '\n')
        if (self.ghost_parent_selection == 'overselection'):
            experiment.log_file.write('ghost_overselection top for parent selection: '
                                      + str(self.ghost_overselection_top) + '\n')
        experiment.log_file.write('ghost_probability of mutation p_m: ' + str(self.ghost_p_m) + '\n')
        experiment.log_file.write('ghost_survival selection method: ' + self.ghost_survival_selection + '\n')
        if (self.ghost_survival_selection == 'k_tournament_without_replacement'):
            experiment.log_file.write('ghost_tournament size for survival selection: '
                                      + str(self.ghost_tournament_size_for_survival_selection) + '\n')
        experiment.log_file.write('ghost_parsimony technique: ' + self.ghost_parsimony_technique + '\n')
        experiment.log_file.write('ghost_parsimony pressure penalty coefficient: ' + str(self.ghost_pppc) + '\n')
        experiment.log_file.write('termination method: ' + self.termination + '\n')
        if (self.termination == 'convergence'):
            experiment.log_file.write('n evals for convergence: '
                                      + str(self.n_for_convergence) + '\n')
        experiment.log_file.write('CIAO data file path root: ' + self.ciao_file_path_root + '\n')
        experiment.log_file.write('parsimony log file path: ' + self.parsimony_log_file_path + '\n')

        # Open parsimony log
        try:
            self.parsimony_log = open(self.parsimony_log_file_path, 'w')
        except:
            print('config: problem with parsimony log file', self.parsimony_log_file_path)
            traceback.print_exc()
            return None


    def build_tree(self, pop, node, depth, dmax, grow_or_full):
        """
        Recursively build an expression tree to the given depth using either
        the 'grow' or 'full' method.
        """
        # Randomly choose a new expression. If not at depth limit,
        # choose an inner node from a set that depends on method 'grow' or 'full'
        if (depth < dmax):
            # Grow selects from all functions and terminals at this depth
            if (grow_or_full == 'grow'):
                expr = (ExprTree.functions + pop.terminals) \
                    [random.randint(0, (len(ExprTree.functions) + len(pop.terminals) - 1))]
            # Full selects only from functions at this depth
            else:
                expr = ExprTree.functions[random.randint(0, len(ExprTree.functions) - 1)]
        # If depth is at Dmax, choose a terminal.
        else:
            expr = pop.terminals[random.randint(0, len(pop.terminals) - 1)]

        # Make a new tree node with this expression.
        node.expr = expr
        if (expr == 'constant'):
            # The random bounds are hard-coded. I should make this a config file
            # item but I don't plan on varying it so, hard-coded it is.
            node.constant = random.uniform(-10, 10)
        node.depth = depth

        # If this node is a function, make its children and update
        # height and count of this node.
        if (expr in ExprTree.functions):
            node.left = Node()
            self.build_tree(pop, node.left, depth + 1, dmax, grow_or_full)
            node.right = Node()
            self.build_tree(pop, node.right, depth + 1, dmax, grow_or_full)

        return node


    def initialize_population(self, pop):
        """
        Given an empty population, generate and return an initial population
        of expression trees using Ramped Half-and-Half
        """
        pop.individuals = [None for _ in range(pop.ea_mu)]

        for i in range(pop.ea_mu):
            root = Node()
            # Full method
            if (random.random() < 0.5):
                self.build_tree(pop, root, 0, pop.dmax_init, 'full')
            # Grow method
            else:
                self.build_tree(pop, root, 0, pop.dmax_init, 'grow')

            pop.individuals[i] = ExprTree(root)
            pop.individuals[i].root.reset_metrics()


    def random_selection_without_replacement(self, pop, num_to_select):
        """
        Given a population, return a selection made up of num_to_select randomly-
        selected individuals from the given population
        """
        if (len(pop.individuals) < num_to_select):
            print('Stuck in random selection without replacement because',
                  len(pop.individuals), 'insufficient to choose', num_to_select)

        random.shuffle(pop.individuals)
        selection = pop.individuals[0:num_to_select]
        return selection


    def fitness_proportional_selection(self, pop, num_to_select):
        """
        Given a population, return a selection using Fitness Proportional Selection
        """
        selection = []
        probabilities = []

        # Find total fitness of population. Account for negative fitnesses
        # with an offset.
        min_fitness = pop.individuals[0].fitness
        for individual in pop.individuals:
            if (individual.fitness < min_fitness):
                min_fitness = individual.fitness
        offset = 0
        if (min_fitness < 0):
            offset = abs(min_fitness)
        total_fitness = 0
        for individual in pop.individuals:
            total_fitness += (individual.fitness + offset)

        # If total fitness is nonzero, good to go.
        if (total_fitness != 0):
            # Calculate probability distribution
            accumulation = 0.0
            for individual in pop.individuals:
                accumulation += ((individual.fitness + offset) / total_fitness)
                probabilities.append(accumulation)

            # Build new population using roulette wheel algorithm
            while (len(selection) < num_to_select):
                randval = random.random()
                curr_member = 0
                while (probabilities[curr_member] < randval):
                    curr_member += 1
                if (curr_member > (len(pop.individuals) - 1)):
                    curr_member = len(pop.individuals) - 1
                selection.append(pop.individuals[curr_member])

        # Edge case: If total_fitness == 0, then just pick from population
        # with uniform probability, because the roulette wheel can't
        # handle having an infinite number of 0-width wedges.
        else:
            selection = self.random_selection_without_replacement(pop, num_to_select)

        return selection


    def overselection(self, pop, num_to_select):
        """
        Given a population, select 80% from the top x% of the population
        ranked by fitness, and 20% from the rest of the population,
        where x% is specified in the configuration file.
        """
        # Sort the population by decreasing fitness
        pop.individuals = sorted(pop.individuals, key = lambda item: item.fitness,
                                 reverse = True)

        # Find the split point and identify top and bottom populations
        split = int(len(pop.individuals) * pop.overselection_top)
        top = pop.individuals[0:split]
        bottom = pop.individuals[split:len(pop.individuals) - 1]

        # Randomly build the new population with 80% chance of choosing
        # from top and 20% chance of choosing from bottom
        selection = []
        while (len(selection) < num_to_select):
            if (random.random() < 0.8):
                if (len(top) > 0):
                    selection.append(top[random.randint(0, len(top) - 1)])
            else:
                if (len(bottom) > 0):
                    selection.append(bottom[random.randint(0, len(bottom) - 1)])

        return selection


    def k_tournament_selection_without_replacement(self, pop, num_to_select):
        """
        Given a population, return a selection using k-tournament Selection
        without replacement.

        Updated to be less dumb by keeping a list of eligible tournament members
        instead of allowing choosing ineligible members.
        """
        if (len(pop.individuals) < num_to_select):
            print('Stuck in k-tournament selection without replacement because',
                  len(pop.individuals), 'insufficient to choose', num_to_select)

        selection = []
        selected_indices = set()

        while (len(selection) < num_to_select):
            # Identify those eligible to be contestants (not already selected)
            k_eligible = {x for x in range(len(pop.individuals))}
            k_eligible = k_eligible - selected_indices

            # If we can't fill a tournament with unselected individuals,
            # reduce tournament size to what's left
            tournament_size = pop.tournament_size_for_survival_selection
            if ((len(pop.individuals) - len(selection)) < tournament_size):
                tournament_size = len(pop.individuals) - len(selection)

            # Pick tournament contestants from those eligible to be contestants
            k_contestants = []
            while (len(k_contestants) < tournament_size):
                contestant_index = list(k_eligible)[random.randint(0, len(k_eligible) - 1)]
                k_eligible.remove(contestant_index)
                k_contestants.append(contestant_index)

            # Choose the best-rated contestant
            k_contestants = sorted(k_contestants,
                                   key=lambda item: pop.individuals[item].fitness,
                                   reverse = True)
            best_index = k_contestants[0]
            selected_indices.add(best_index)
            selection.append(pop.individuals[best_index])

        return selection


    def truncation_selection(self, pop, num_to_select):
        """
        Truncation selection. Given a population, sort the population and
        select the top individuals.
        """
        sorted_population = sorted(pop.individuals, key=lambda item: item.fitness, reverse = True)
        selection = []
        for curr_individual in range(pop.ea_mu):
            selection.append(sorted_population[curr_individual])
        return selection


    def select_parents(self, pop):
        """
        Given a population, return a mating pool using the configured method.
        """
        if (pop.parent_selection == "fitness_proportional_selection"):
            return self.fitness_proportional_selection(pop, pop.ea_lambda)
        elif (pop.parent_selection == "overselection"):
            return self.overselection(pop, pop.ea_lambda)
        else:
            print("Unknown parent selection method:", pop.parent_selection)
            sys.exit(1)


    def mutate(self, pop, parent):
        """
        Given a population and a parent, return a mutated offspring
        """
        # Start with a copy of the parent
        offspring = copy.deepcopy(parent)

        # Randomly pick a node in the expression tree
        selected_node = offspring.root.find_nth_node(random.randint(1, offspring.root.size))

        # Build a new (sub)tree there. Arbitrarily choose 'grow' method and limit depth to dmax_overall.
        self.build_tree(pop, selected_node, selected_node.depth, pop.dmax_overall, 'grow')

        # Reset the tree metrics we just screwed up
        offspring.root.reset_metrics()

        return offspring


    def recombine(self, pop, parent1, parent2):
        """
        Given a population and two parents, return two recombined offspring.
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
            if (((selected_node1.depth + selected_node2.height) > pop.dmax_overall)
                or ((selected_node2.depth + selected_node1.height) > pop.dmax_overall)):
                continue

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


    def recombine_mutate(self, pop, parents):
        """
        Given a population and a set of parents, return a set of offspring
        of equal size created through stochastic choice of mutation or
        recombination.
        """
        offspring = []

        # Walk through parents list either mutating or pair-wise recombining
        # to create offspring
        parent_counter = 0
        while (len(offspring) < len(parents)):
            # Mutate if random value within probability of mutation
            # OR if we only have 1 parent left
            if ((random.random() < pop.p_m)
                or (parent_counter == (len(parents) - 1))):
                offspring.append(self.mutate(pop, parents[parent_counter]))
                parent_counter += 1
            # Otherwise, recombine
            else:
                offspring += self.recombine(pop, parents[parent_counter],
                                            parents[parent_counter + 1])
                parent_counter += 2

        return offspring


    def select_survivors(self, pop):
        """
        Given a population, return a selection of survivors using the
        configured method.
        """
        if (pop.survival_selection == 'truncation'):
            return self.truncation_selection(pop, pop.ea_mu)
        elif (pop.survival_selection == 'k_tournament_without_replacement'):
            return self.k_tournament_selection_without_replacement(pop,
                                                                   pop.ea_mu)
        else:
            print('Unknown parent selection method:', pop.survival_selection)
            exit(1)


    def execute_one_game(self, pac_individual, ghost_individual):
        """
        Execute one game / eval of a run given a Pac individual and
        Ghost individual selected from their respective populations.
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

        # Create new Pac and Ghost controllers
        for curr_pac_id in range(self.experiment.num_pacs):
            self.pac_controllers[curr_pac_id] = PacController(curr_pac_id, pac_individual)
        for curr_ghost_id in range(self.experiment.num_ghosts):
            self.ghost_controllers[curr_ghost_id] = GhostController(curr_ghost_id,
                                                                    ghost_individual)

        # While the game isn't over, play game turns.
        game_over = False
        while (not game_over):
            game_over = game_state.play_turn(self.experiment.world_data,
                                             self.pac_controllers,
                                             self.ghost_controllers)

        # Set Pac fitness and implement parsimony pressure
        pac_individual.fitness = game_state.score
        if (self.pac_pop.parsimony_technique == 'size'):
            pac_individual.fitness -= (self.pac_pop.pppc * pac_individual.root.size)
        else:
            pac_individual.fitness -= (self.pac_pop.pppc * pac_individual.root.height)

        # Set Ghost fitness and implement parsimony pressure
        ghost_individual.fitness = -(game_state.score)
        if (game_state.ghost_won):
            ghost_individual.fitness += int((game_state.time * 100.0) / game_state.orig_time)
        if (self.ghost_pop.parsimony_technique == 'size'):
            ghost_individual.fitness -= (self.ghost_pop.pppc * ghost_individual.root.size)
        else:
            ghost_individual.fitness -= (self.ghost_pop.pppc * ghost_individual.root.height)

        # Set Pac and Ghost scores
        pac_individual.score = game_state.score # Score is raw game score without parsimony pressure for Pac
        ghost_individual.score = ghost_individual.fitness # Score and fitness interchangeable for Ghost


    def generation_evals(self, pacs, ghosts, eval_count, evals_with_no_change, pac_gen_high_fitness):
        """
        Run evaluations of the Pac vs Ghost populations given Pac and Ghost
        populations. Also takes current eval count, evals with no change, and
        pac generation high fitness in order to do bookkeeping related to
        termination conditions. Returns updated eval count and evals with no change.

        Run games with Pac vs Ghost from the provided populations.
        Average fitnesses of multiple evaluations of the same individual.
        """
        # Set up matrices to hold per-game fitness values for Pac and Ghost
        pac_fitnesses = [[] for _ in range(len(pacs))]
        ghost_fitnesses = [[] for _ in range(len(ghosts))]

        # Shuffle the pacs and ghosts, then play each Pac against one Ghost
        random.shuffle(pacs)
        random.shuffle(ghosts)
        num_games = max(len(pacs), len(ghosts))
        for curr_game in range(num_games):
            # If num pacs < num ghosts, some pacs will go multiple times
            pac_index = curr_game % len(pacs)
            # If num ghosts < num pacs, some ghosts will go multiple times
            ghost_index = curr_game % len(ghosts)
            pac_individual = pacs[pac_index]
            ghost_individual = ghosts[ghost_index]
            self.execute_one_game(pac_individual, ghost_individual)
            # Save the fitness in a list so we can average the results later
            pac_fitnesses[pac_index].append(pac_individual.fitness)
            ghost_fitnesses[ghost_index].append(ghost_individual.fitness)

            # Bookkeeping
            eval_count += 1
            if (pac_individual.fitness <= pac_gen_high_fitness):
                evals_with_no_change += 1
            else:
                evals_with_no_change = 0

            # Provide status message every nth evaluation.
            if ((eval_count % 10) == 0):
                print('\r', eval_count, 'evals', end =" ")

        # Set the fitness of each Pac and Ghost to the average of its list of fitnesses
        for pac_index in range(len(pacs)):
            pacs[pac_index].fitness = numpy.mean(pac_fitnesses[pac_index])
        for ghost_index in range(len(ghosts)):
            ghosts[ghost_index].fitness = numpy.mean(ghost_fitnesses[ghost_index])

        # ALTERNATE METHOD: Play every Pac against every Ghost and average fitnesses
        # [Takes WAY too many evaluations]
        # # Set up matrices to hold per-game fitness values for Pac and Ghost
        # pac_fitnesses = numpy.zeros((len(self.pac_pop.individuals),
        #                              len(self.ghost_pop.individuals)))
        # ghost_fitnesses = numpy.zeros((len(self.ghost_pop.individuals),
        #                                len(self.pac_pop.individuals)))
        # # Play every Pac against every Ghost and perform bookkeeping
        # for pac_index in range(len(self.pac_pop.individuals)):
        #     pac_individual = self.pac_pop.individuals[pac_index]
        #     for ghost_index in range(len(self.ghost_pop.individuals)):
        #         ghost_individual = self.ghost_pop.individuals[ghost_index]
        #         self.execute_one_game(pac_individual, ghost_individual)
        #         pac_fitnesses[pac_index][ghost_index] = pac_individual.fitness
        #         ghost_fitnesses[ghost_index][pac_index] = ghost_individual.fitness
        #         # Bookkeeping
        #         eval_count += 1
        #         if (pac_individual.fitness <= pac_gen_high_fitness):
        #             evals_with_no_change += 1
        #         else:
        #             evals_with_no_change = 0
        #         # Provide status message every nth evaluation.
        #         if ((eval_count % 10) == 0):
        #             print('\r', eval_count, 'evals', end =" ")
        # # Set the fitness of each Pac to the mean of its fitnesses against every Ghost
        # # and vice-versa for the Ghosts.
        # for pac_index in range(len(self.pac_pop.individuals)):
        #     pac_individual = self.pac_pop.individuals[pac_index]
        #     pac_individual.fitness = numpy.mean(pac_fitnesses[pac_index])
        # for ghost_index in range(len(self.ghost_pop.individuals)):
        #     ghost_individual = self.ghost_pop.individuals[ghost_index]
        #     ghost_individual.fitness = numpy.mean(ghost_fitnesses[ghost_index])

        return eval_count, evals_with_no_change


    def ciao_plot(self):
        """
        Play the best Pac and Ghost of every generation against each other
        to create CIAO plot.

        Pac = Attacker = Y axis (rows)
        Ghost = Defender = X axis (columns)
        """
        num_gens = len(self.pac_pop.best_individuals)

        fitnesses = numpy.zeros((num_gens, num_gens))
        eval_count = 0
        print('CIAO: play', num_gens, 'generations of bests')
        for ghost in range(num_gens):
            for pac in range(ghost, num_gens):
                self.execute_one_game(self.pac_pop.best_individuals[pac],
                                      self.ghost_pop.best_individuals[ghost])
                eval_count += 1
                # 0,0 is lower left, so adjust the row index
                fitnesses[num_gens - pac - 1][ghost] = self.pac_pop.best_individuals[pac].fitness

                # Provide status message every nth evaluation.
                if ((eval_count % 10) == 0):
                    print('\r', eval_count, 'evals', end = ' ')

        # Normalize fitnesses to [0.0 - 1.0] where 1.0 is best
        min_fitness = numpy.min(fitnesses)
        if (min_fitness < 0):
            fitnesses = fitnesses + numpy.abs(min_fitness)
        else:
            fitnesses = fitnesses - min_fitness
        max_fitness = numpy.max(fitnesses)
        if (max_fitness != 0):
            fitnesses = (fitnesses / max_fitness)

        # Reset the matrix below the anti-diagonal. We should just be able to
        # ignore these values but if we set them to 1.0 (max luminance)
        # it can make plotting them simpler since 1.0 will show up as white
        # and disappear into the background (assuming white background).
        for i in range(1, num_gens):
            for j in range(i, num_gens):
                fitnesses[num_gens - i][j] = 1.0

        # Write out CIAO data to file for separate tool to plot it
        numpy.savetxt('data/' + self.ciao_file_path_root + '_Run' \
                      + str(self.experiment.curr_run) + '_CIAO_Data.txt',
                      fitnesses)
        CIAOPlotter.plot(self.ciao_file_path_root + '_Run' + str(self.experiment.curr_run),
                         fitnesses)


    def execute_one_run(self):
        """
        Execute one run of an experiment.

        Return highest score and its associated world and solution data.
        """
        # Initialize run values of populations
        self.pac_pop.reset_run_values()
        self.ghost_pop.reset_run_values()

        self.parsimony_log.write('\nRun ' + str(self.experiment.curr_run) + '\n')

        generation = 1
        print('\rGeneration', generation, end = ' ')

        # Initialize the populations and starting fitnesses
        self.initialize_population(self.pac_pop)
        self.initialize_population(self.ghost_pop)
        eval_count, self.pac_pop.evals_with_no_change = \
            self.generation_evals(self.pac_pop.individuals,
                                  self.ghost_pop.individuals,
                                  0, 0, float('-inf'))

        # Run generation after generation until we hit termination condition
        # and break out of the loop
        while (True):

            # Update generation bookkeeping
            self.pac_pop.generation_bookkeeping()
            self.pac_pop.update_logs(eval_count, self.experiment.log_file, self.parsimony_log)
            self.ghost_pop.generation_bookkeeping()

            # Update run bookkeeping
            self.pac_pop.calc_run_stats()
            self.ghost_pop.calc_run_stats()

            # Check for termination
            if (self.termination == 'number_of_evals'):
                if (eval_count >= self.experiment.num_fitness_evals_per_run):
                    break
            elif (self.termination == 'convergence'):
                if (self.pac_pop.evals_with_no_change >= self.n_for_convergence):
                    print('CONVERGED at', eval_count, 'evals')
                    break
            else:
                print('Unknown termination method:', self.termination)
                sys.exit(1)

            # Not terminating? Let's proceed!

            generation += 1
            print('\rGeneration', generation, end = ' ')

            # Select parents
            pac_parents = self.select_parents(self.pac_pop)
            ghost_parents = self.select_parents(self.ghost_pop)

            # Recombine and/or mutate
            pac_offspring = self.recombine_mutate(self.pac_pop, pac_parents)
            self.pac_pop.individuals += pac_offspring
            ghost_offspring = self.recombine_mutate(self.ghost_pop, ghost_parents)
            self.ghost_pop.individuals += ghost_offspring

            # Evaluate offspring
            eval_count, self.pac_pop.evals_with_no_change = \
                self.generation_evals(pac_offspring, ghost_offspring,
                                      eval_count, self.pac_pop.evals_with_no_change,
                                      self.pac_pop.gen_high_fitness)

            # Survival selection
            self.pac_pop.individuals = self.select_survivors(self.pac_pop)
            self.ghost_pop.individuals = self.select_survivors(self.ghost_pop)


        # Do CIAO plot here
        self.ciao_plot()

        # Play "exhibition game" to get best world data (does not count against Eval total).
        # This has a side effect of setting self.experiment.world_data
        print('Exhibition game: Pac', self.pac_pop.run_best_individual.fitness,
              'vs Ghost', self.ghost_pop.run_best_individual.fitness)
        self.execute_one_game(self.pac_pop.run_best_individual,
                              self.ghost_pop.run_best_individual)

        return self.pac_pop.run_high_fitness, self.experiment.world_data, \
            str(self.pac_pop.run_best_individual.root), \
            self.ghost_pop.run_high_fitness, str(self.ghost_pop.run_best_individual.root)

