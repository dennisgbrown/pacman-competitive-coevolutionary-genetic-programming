# -*- coding: utf-8 -*-
import copy

class Population():
    """
    Hold relevant information and bookkeeping functions for a population.
    """
    def __init__(self, pop_name, ea_mu, ea_lambda, dmax_init, dmax_overall,
                 parent_selection, overselection_top, p_m, survival_selection,
                 tournament_size_for_survival_selection, parsimony_technique,
                 pppc, functions, terminals):
        self.pop_name = pop_name
        self.ea_mu = ea_mu
        self.ea_lambda = ea_lambda
        self.dmax_init = dmax_init
        self.dmax_overall = dmax_overall
        self.parent_selection = parent_selection
        self.overselection_top = overselection_top
        self.p_m = p_m
        self.survival_selection = survival_selection
        self.tournament_size_for_survival_selection = tournament_size_for_survival_selection
        self.parsimony_technique = parsimony_technique
        self.pppc = pppc
        self.functions = functions
        self.terminals = terminals

        self.individuals = None  # list of ExprTree instances
        self.best_individuals = [] # list of best individuals of each generation

        # Per-run bookkeeping values
        self.run_high_fitness = float('-inf')
        self.run_high_score = float('-inf')
        self.run_best_world_data = None
        self.run_best_individual = None
        self.evals_with_no_change = 0

        # Per-generation bookkeeping values
        self.gen_high_fitness = float('-inf')
        self.gen_high_score = float('-inf')
        self.gen_fitness_total = 0
        self.gen_score_total = 0
        self.gen_best_world_data = None
        self.gen_best_individual = None
        self.gen_best_solution = None
        self.gen_max_tree_height = -1
        self.gen_tree_height_total = 0
        self.gen_max_tree_size = -1
        self.gen_tree_size_total = 0


    def reset_run_values(self):
        """
        Reset values to prepare for a new run.
        """
        self.individuals = None
        self.best_individuals = []
        self.run_high_fitness = float('-inf')
        self.run_high_score = float('-inf')
        self.run_best_world_data = None
        self.run_best_solution = None
        self.evals_with_no_change = 0


    def calc_run_stats(self):
        """
        Update stats for the current run. To be called immediately
        after a generation has completed including bookkeeping.
        """
        # Check and handle new run high score and fitness
        if (self.gen_high_score > self.run_high_score):
            self.run_high_score = self.gen_high_score
        if (self.gen_high_fitness > self.run_high_fitness):
            self.run_high_fitness = self.gen_high_fitness
            print('New run', self.pop_name, 'high fitness: ', self.run_high_fitness)
            self.run_best_individual = self.gen_best_individual

        # # ALTERNATE METHOD:
        # # We only care about the best from the final generation, so
        # # just blindly copy after each generation and when this method
        # # is no longer called, that's the final generation
        # self.run_high_score = self.gen_high_score
        # self.run_high_fitness = self.gen_high_fitness
        # self.run_best_individual = self.gen_best_individual
        # print('Gen', self.pop_name, 'high fitness: ', self.run_high_fitness)


    def generation_bookkeeping(self):
        """
        Update stats for the current generation. To be called immediately
        after a generation has completed.
        """
        self.gen_high_fitness = float('-inf')
        self.gen_high_score = float('-inf')
        self.gen_fitness_total = 0
        self.gen_score_total = 0
        self.gen_best_individual = None
        self.gen_max_tree_height = -1
        self.gen_tree_height_total = 0
        self.gen_max_tree_size = -1
        self.gen_tree_size_total = 0

        for individual in self.individuals:
            self.gen_fitness_total += individual.fitness
            if (individual.fitness > self.gen_high_fitness):
                self.gen_high_fitness = individual.fitness
                self.gen_best_individual = copy.deepcopy(individual)
            self.gen_score_total += individual.score
            if (individual.score > self.gen_high_score):
                self.gen_high_score = individual.score
            self.gen_tree_height_total += individual.root.height
            if (individual.root.height > self.gen_max_tree_height):
                self.gen_max_tree_height = individual.root.height
            self.gen_tree_size_total += individual.root.size
            if (individual.root.size > self.gen_max_tree_size):
                self.gen_max_tree_size = individual.root.size

        # Save off best individual of the generation
        self.best_individuals.append(copy.deepcopy(self.gen_best_individual))


    def update_logs(self, eval_count, experiment_log, parsimony_log):
        """
        Update the experiment and parsimony logs
        """
        # Update log
        experiment_log.write(str(eval_count) + '\t' \
                             + str(self.gen_fitness_total / len(self.individuals)) + '\t'
                             + str(self.gen_high_fitness) + '\n')

        # Update parsimony log
        parsimony_log.write(str(eval_count) + '\t' \
                            + str(self.gen_tree_height_total / len(self.individuals)) + '\t'
                            + str(self.gen_max_tree_height) + '\t'
                            + str(self.gen_tree_size_total / len(self.individuals)) + '\t'
                            + str(self.gen_max_tree_size) + '\t'
                            + str(self.gen_score_total / len(self.individuals)) + '\t'
                            + str(self.gen_high_score) + '\n')

