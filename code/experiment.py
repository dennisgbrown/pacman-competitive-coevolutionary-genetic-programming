# -*- coding: utf-8 -*-
import configparser
import random
import time
import traceback
import sys

sys.path.append('code')
from gameMapInfo import GameMapInfo
from randomStrategy import RandomStrategy
from hillClimbStrategy import HillClimbStrategy
from gpStrategy import GPStrategy
from ccegpStrategy import CCEGPStrategy


class Experiment:
    """
    Provide capabilities to run an experiment within given
    configuration parameters.
    """

    def __init__(self, config_file_path):
        """
        Set up an experiment given a configuration file path and
        problem file path.
        """
        self.config_parser = None

        self.random_seed = None
        self.strategy = 'random'
        self.num_runs_per_experiment = 1
        self.num_fitness_evals_per_run = 100
        self.log_file_path = 'logs/defaultLog.txt'
        self.log_file = None
        self.pac_solution_file_path = 'solutions/defaultPacSolution.txt'
        self.ghost_solution_file_path = 'solutions/defaultGhostSolution.txt'
        self.high_score_world_file_path = 'worlds/defaultWorld.txt'
        self.map_file_path = None

        self.world_data = None  # Array of strings that will be written to world data file
        self.game_map = None
        self.pill_density = 0.5
        self.fruit_spawning_probability = 0.5
        self.fruit_score = 10
        self.time_multiplier = 1

        self.num_pacs = 1
        self.num_ghosts = 3

        self.pac_exp_high_fitness = float('-inf')
        self.pac_exp_best_world_data = None
        self.pac_exp_best_solution = None
        self.ghost_exp_high_fitness = float('-inf')
        self.ghost_exp_best_solution = None

        self.pre_loaded_maps = []

        try:
            self.config_parser = configparser.ConfigParser()
            self.config_parser.read(config_file_path)

            try:
                self.random_seed = self.config_parser.getint('basic_options', 'random_seed')
                print('config: random_seed =', self.random_seed)
            except:
                print('config: random_seed not specified; using system time')
                self.random_seed = int(time.time() * 1000.0)
            random.seed(self.random_seed)

            try:
                self.strategy = self.config_parser.get('basic_options', 'strategy')
                print('config: strategy =', self.strategy)
            except:
                print('config: strategy not properly specified; using', self.strategy)

            try:
                self.num_runs_per_experiment = self.config_parser.getint('basic_options', 'num_runs_per_experiment')
                print('config: num_runs_per_experiment =', self.num_runs_per_experiment)
            except:
                print('config: num_runs_per_experiment not properly specified; using', self.num_runs_per_experiment)

            try:
                self.num_fitness_evals_per_run = self.config_parser.getint('basic_options',
                                                                           'num_fitness_evals_per_run')
                print('config: num_fitness_evals_per_run =', self.num_fitness_evals_per_run)
            except:
                print('config: num_fitness_evals_per_run not properly specified; using',
                      self.num_fitness_evals_per_run)

            try:
                self.log_file_path = self.config_parser.get('basic_options', 'log_file_path')
                print('config: log_file_path =', self.log_file_path)
            except:
                print('config: log_file_path not properly specified; using', self.log_file_path)

            try:
                self.high_score_world_file_path = self.config_parser.get('basic_options', 'high_score_world_file_path')
                print('config: high_score_world_file_path =', self.high_score_world_file_path)
            except:
                print('config: high_score_world_file_path not properly specified; using', self.high_score_world_file_path)

            try:
                self.pac_solution_file_path = self.config_parser.get('basic_options', 'pac_solution_file_path')
                print('config: pac_solution_file_path =', self.pac_solution_file_path)
            except:
                print('config: pac_solution_file_path not properly specified; using', self.pac_solution_file_path)

            try:
                self.ghost_solution_file_path = self.config_parser.get('basic_options', 'ghost_solution_file_path')
                print('config: ghost_solution_file_path =', self.ghost_solution_file_path)
            except:
                print('config: ghost_solution_file_path not properly specified; using', self.ghost_solution_file_path)

            try:
                self.pill_density = self.config_parser.getfloat('basic_options', 'pill_density')
                print('config: pill_density =', self.pill_density)
            except:
                print('config: pill_density not properly specified; using', self.pill_density)

            try:
                self.fruit_spawning_probability = self.config_parser.getfloat('basic_options', 'fruit_spawning_probability')
                print('config: fruit_spawning_probability =', self.fruit_spawning_probability)
            except:
                print('config: fruit_spawning_probability not properly specified; using', self.fruit_spawning_probability)

            try:
                self.fruit_score = self.config_parser.getfloat('basic_options', 'fruit_score')
                print('config: fruit_score =', self.fruit_score)
            except:
                print('config: fruit_score not properly specified; using', self.fruit_score)

            try:
                self.time_multiplier = self.config_parser.getfloat('basic_options', 'time_multiplier')
                print('config: time_multiplier =', self.time_multiplier)
            except:
                print('config: time_multiplier not properly specified; using', self.time_multiplier)

            # Dump parms to log file
            try:
                self.log_file = open(self.log_file_path, 'w')

                self.log_file.write('Result Log\n\n')
                self.log_file.write('random seed: '
                                    + str(self.random_seed) + '\n')
                self.log_file.write('strategy: '
                                    + self.strategy + '\n')
                self.log_file.write('number of runs per experiment: '
                                    + str(self.num_runs_per_experiment) + '\n')
                self.log_file.write('number of fitness evals per run: '
                                    + str(self.num_fitness_evals_per_run) + '\n')
                self.log_file.write('pac solution file path: '
                                    + self.pac_solution_file_path + '\n')
                self.log_file.write('ghost solution file path: '
                                    + self.ghost_solution_file_path + '\n')
                self.log_file.write('highest-scoring world file path: '
                                    + self.high_score_world_file_path + '\n')
                self.log_file.write('pill density: '
                                    + str(self.pill_density) + '\n')
                self.log_file.write('fruit spawning probability: '
                                    + str(self.fruit_spawning_probability) + '\n')
                self.log_file.write('fruit score: '
                                    + str(self.fruit_score) + '\n')
                self.log_file.write('time multiplier: '
                                    + str(self.time_multiplier) + '\n')

            except:
                print('config: problem with log file', self.log_file_path)
                traceback.print_exc()
                return None

        except:
            traceback.print_exc()
            return None


    def pre_load_maps(self):
        """
        Pre-load all the possible game maps.
        """
        for i in range(100):
            self.pre_loaded_maps.append(GameMapInfo('maps/map' + str(i) + '.txt'))


    def run_experiment(self):
        """
        Run the experiment defined by the member variables contained in this
        experiment instance on the provided puzzle state.
        """

        start_time = time.time()

        self.pre_load_maps()

        strategy_instance = None
        if (self.strategy == 'random'):
            strategy_instance = RandomStrategy(self)
        elif (self.strategy == 'hillclimb'):
            strategy_instance = HillClimbStrategy(self)
        elif (self.strategy == 'gp'):
            strategy_instance = GPStrategy(self)
        elif (self.strategy == 'ccegp'):
            strategy_instance = CCEGPStrategy(self)
        else:
            print('strategy unknown:', self.strategy)
            sys.exit(1)

        # For each run...
        for curr_run in range(1, self.num_runs_per_experiment + 1):

            # Update log
            self.curr_run = curr_run
            print('\nRun', curr_run)
            self.log_file.write('\nRun ' + str(curr_run) + '\n')

            # Execute one run and get best values.
            pac_run_high_fitness, pac_run_best_world_data, pac_run_best_solution, \
                ghost_run_high_fitness, ghost_run_best_solution \
                = strategy_instance.execute_one_run()

            # If best of run is best overall, update appropriate values
            if (self.strategy != 'ccegp'):
                if (pac_run_high_fitness > self.pac_exp_high_fitness):
                    self.pac_exp_high_fitness = pac_run_high_fitness
                    print('New exp Pac high fitness: ', self.pac_exp_high_fitness)
                    self.pac_exp_best_world_data = pac_run_best_world_data
                    self.pac_exp_best_solution = pac_run_best_solution
            # If Competitive Co-evolution, add fitnesses (use Pac to store most data)
            else:
                if ((pac_run_high_fitness + ghost_run_high_fitness) > self.pac_exp_high_fitness):
                    self.pac_exp_high_fitness = (pac_run_high_fitness + ghost_run_high_fitness)
                    print('New exp Pac+Ghost high fitness: ', self.pac_exp_high_fitness)
                    self.pac_exp_best_world_data = pac_run_best_world_data
                    self.pac_exp_best_solution = pac_run_best_solution
                    self.ghost_exp_best_solution = ghost_run_best_solution


        # Dump best world to file
        the_file = open(self.high_score_world_file_path, 'w')
        for line in self.pac_exp_best_world_data:
            the_file.write(line)
        the_file.close()

        # Dump best Pac solution to file
        the_file = open(self.pac_solution_file_path, 'w')
        the_file.write(self.pac_exp_best_solution)
        the_file.close()

        # Dump best Ghost solution to file
        if (self.strategy == 'ccegp'):
            the_file = open(self.ghost_solution_file_path, 'w')
            the_file.write(self.ghost_exp_best_solution)
            the_file.close()

        # Close out the log file
        if (not(self.log_file is None)):
            self.log_file.close()

        print(time.time() - start_time, 'seconds')
