# -*- coding: utf-8 -*-
import sys

sys.path.append('code')
from experiment import Experiment

def main():
    """
    Parse command line argument and run the experiment.
    """
    config_file_path = 'configs/default.cfg'

    if (len(sys.argv) > 1):
        print(f'The config file passed is: {sys.argv[1]}')
        config_file_path = sys.argv[1]
    else:
        print('No config file specified -- using', config_file_path)

    experiment = Experiment(config_file_path)
    if (not(experiment is None)):
        experiment.run_experiment()

    print('\n---Experiment concluded---')

if __name__ == '__main__':
    main()


