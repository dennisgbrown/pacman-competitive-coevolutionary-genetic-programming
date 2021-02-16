# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy
import traceback

"""
Read a log file plot best vs. average with "error bars" to show min-max range
"""

plotfileroot = 'config1-pars-10s'

logfile = 'logs/config1P10s.txt'

parslogfile = 'data/parsimonyConfig1P10s.txt'

curr_run = -1
run_evals = []

run_average_score_lists = []
run_best_score_lists = []

run_average_fitness_lists = []
run_best_fitness_lists = []

run_average_depth_lists = []
run_best_depth_lists = []

run_average_size_lists = []
run_best_size_lists = []

lineno = 0

with open(logfile, 'r') as reader:
   curr_line = reader.readline()
   while (curr_line):
        lineno += 1
        curr_line = curr_line.strip()

        if (curr_line.startswith('Run')):
            curr_run += 1
            curr_eval = 0

        elif ((len(curr_line) > 0) and (curr_run > -1)):
            try:
                data_list = list(curr_line.split("\t"))
                if (len(run_evals) < (curr_eval + 1)):
                    run_evals.append(int(data_list[0]))
                if (len(run_average_score_lists) < (curr_eval + 1)):
                    run_average_score_lists.append([])
                if (len(run_best_score_lists) < (curr_eval + 1)):
                    run_best_score_lists.append([])
                run_average_score_lists[curr_eval].append(float(data_list[1]))
                run_best_score_lists[curr_eval].append(float(data_list[2]))
                curr_eval += 1
            except:
                print('Problem in line ' + str(lineno) + ': |' + curr_line + '|')
                traceback.print_exc()
                pass

        curr_line = reader.readline()

with open(parslogfile, 'r') as reader:
   curr_line = reader.readline()
   while (curr_line):
        lineno += 1
        curr_line = curr_line.strip()

        if (curr_line.startswith('Run')):
            curr_run += 1
            curr_eval = 0

        elif ((len(curr_line) > 0) and (curr_run > -1)):
            try:
                data_list = list(curr_line.split("\t"))

                if (len(run_average_fitness_lists) < (curr_eval + 1)):
                    run_average_fitness_lists.append([])
                if (len(run_best_fitness_lists) < (curr_eval + 1)):
                    run_best_fitness_lists.append([])
                run_average_fitness_lists[curr_eval].append(float(data_list[5]))
                run_best_fitness_lists[curr_eval].append(float(data_list[6]))

                if (len(run_average_depth_lists) < (curr_eval + 1)):
                    run_average_depth_lists.append([])
                if (len(run_best_depth_lists) < (curr_eval + 1)):
                    run_best_depth_lists.append([])
                run_average_depth_lists[curr_eval].append(float(data_list[1]))
                run_best_depth_lists[curr_eval].append(float(data_list[2]))

                if (len(run_average_size_lists) < (curr_eval + 1)):
                    run_average_size_lists.append([])
                if (len(run_best_size_lists) < (curr_eval + 1)):
                    run_best_size_lists.append([])
                run_average_size_lists[curr_eval].append(float(data_list[3]))
                run_best_size_lists[curr_eval].append(float(data_list[4]))

                curr_eval += 1
            except:
                print('Problem in line ' + str(lineno) + ': |' + curr_line + '|')
                traceback.print_exc()
                pass

        curr_line = reader.readline()


run_evals = numpy.array(run_evals)

run_average_score_averages = numpy.zeros(len(run_evals))
run_max_score_averages = numpy.zeros(len(run_evals))
run_min_score_averages = numpy.zeros(len(run_evals))
run_std_score_averages = numpy.zeros(len(run_evals))

run_average_score_bests = numpy.zeros(len(run_evals))
run_max_score_bests = numpy.zeros(len(run_evals))
run_min_score_bests = numpy.zeros(len(run_evals))
run_std_score_bests = numpy.zeros(len(run_evals))

run_average_fitness_averages = numpy.zeros(len(run_evals))
run_max_fitness_averages = numpy.zeros(len(run_evals))
run_min_fitness_averages = numpy.zeros(len(run_evals))
run_std_fitness_averages = numpy.zeros(len(run_evals))

run_average_fitness_bests = numpy.zeros(len(run_evals))
run_max_fitness_bests = numpy.zeros(len(run_evals))
run_min_fitness_bests = numpy.zeros(len(run_evals))
run_std_fitness_bests = numpy.zeros(len(run_evals))

run_average_depth_averages = numpy.zeros(len(run_evals))
run_max_depth_averages = numpy.zeros(len(run_evals))
run_min_depth_averages = numpy.zeros(len(run_evals))
run_std_depth_averages = numpy.zeros(len(run_evals))

run_average_depth_bests = numpy.zeros(len(run_evals))
run_max_depth_bests = numpy.zeros(len(run_evals))
run_min_depth_bests = numpy.zeros(len(run_evals))
run_std_depth_bests = numpy.zeros(len(run_evals))

run_average_size_averages = numpy.zeros(len(run_evals))
run_max_size_averages = numpy.zeros(len(run_evals))
run_min_size_averages = numpy.zeros(len(run_evals))
run_std_size_averages = numpy.zeros(len(run_evals))

run_average_size_bests = numpy.zeros(len(run_evals))
run_max_size_bests = numpy.zeros(len(run_evals))
run_min_size_bests = numpy.zeros(len(run_evals))
run_std_size_bests = numpy.zeros(len(run_evals))

for i in range(len(run_evals)):

    run_average_score_averages[i] = numpy.mean(run_average_score_lists[i])
    run_max_score_averages[i] = numpy.amax(run_average_score_lists[i])
    run_min_score_averages[i] = numpy.amin(run_average_score_lists[i])
    run_std_score_averages[i] = numpy.std(run_average_score_lists[i])

    run_average_score_bests[i] = numpy.mean(run_best_score_lists[i])
    run_max_score_bests[i] = numpy.amax(run_best_score_lists[i])
    run_min_score_bests[i] = numpy.amin(run_best_score_lists[i])
    run_std_score_bests[i] = numpy.std(run_best_score_lists[i])

    run_average_fitness_averages[i] = numpy.mean(run_average_fitness_lists[i])
    run_max_fitness_averages[i] = numpy.amax(run_average_fitness_lists[i])
    run_min_fitness_averages[i] = numpy.amin(run_average_fitness_lists[i])
    run_std_fitness_averages[i] = numpy.std(run_average_fitness_lists[i])

    run_average_fitness_bests[i] = numpy.mean(run_best_fitness_lists[i])
    run_max_fitness_bests[i] = numpy.amax(run_best_fitness_lists[i])
    run_min_fitness_bests[i] = numpy.amin(run_best_fitness_lists[i])
    run_std_fitness_bests[i] = numpy.std(run_best_fitness_lists[i])

    run_average_depth_averages[i] = numpy.mean(run_average_depth_lists[i])
    run_max_depth_averages[i] = numpy.amax(run_average_depth_lists[i])
    run_min_depth_averages[i] = numpy.amin(run_average_depth_lists[i])
    run_std_depth_averages[i] = numpy.std(run_average_depth_lists[i])

    run_average_depth_bests[i] = numpy.mean(run_best_depth_lists[i])
    run_max_depth_bests[i] = numpy.amax(run_best_depth_lists[i])
    run_min_depth_bests[i] = numpy.amin(run_best_depth_lists[i])
    run_std_depth_bests[i] = numpy.std(run_best_depth_lists[i])

    run_average_size_averages[i] = numpy.mean(run_average_size_lists[i])
    run_max_size_averages[i] = numpy.amax(run_average_size_lists[i])
    run_min_size_averages[i] = numpy.amin(run_average_size_lists[i])
    run_std_size_averages[i] = numpy.std(run_average_size_lists[i])

    run_average_size_bests[i] = numpy.mean(run_best_size_lists[i])
    run_max_size_bests[i] = numpy.amax(run_best_size_lists[i])
    run_min_size_bests[i] = numpy.amin(run_best_size_lists[i])
    run_std_size_bests[i] = numpy.std(run_best_size_lists[i])


plt.errorbar(run_evals, run_average_score_averages,
             [run_average_score_averages - run_min_score_averages,
              run_max_score_averages - run_average_score_averages],
             lw = 0.3, fmt = 'b', label = 'score averages')
plt.errorbar(run_evals, run_average_score_averages, run_std_score_averages,
             lw = 0.6, fmt = 'b')

plt.errorbar(run_evals, run_average_score_bests,
             [run_average_score_bests - run_min_score_bests,
              run_max_score_bests - run_average_score_bests],
             lw = 0.3, fmt = 'g', label = 'score bests')
plt.errorbar(run_evals, run_average_score_bests, run_std_score_bests,
             lw = 0.6, fmt = 'g')

plt.errorbar(run_evals, run_average_fitness_averages,
             [run_average_fitness_averages - run_min_fitness_averages,
              run_max_fitness_averages - run_average_fitness_averages],
             lw = 0.3, fmt = 'r', label = 'fitness averages')
plt.errorbar(run_evals, run_average_fitness_averages, run_std_fitness_averages,
             lw = 0.6, fmt = 'r')

plt.errorbar(run_evals, run_average_fitness_bests,
             [run_average_fitness_bests - run_min_fitness_bests,
              run_max_fitness_bests - run_average_fitness_bests],
             lw = 0.3, fmt = 'c', label = 'fitness bests')
plt.errorbar(run_evals, run_average_fitness_bests, run_std_fitness_bests,
             lw = 0.6, fmt = 'c')

plt.errorbar(run_evals, run_average_depth_averages,
             [run_average_depth_averages - run_min_depth_averages,
              run_max_depth_averages - run_average_depth_averages],
             lw = 0.3, fmt = 'm', label = 'depth averages')
plt.errorbar(run_evals, run_average_depth_averages, run_std_depth_averages,
             lw = 0.6, fmt = 'm')

plt.errorbar(run_evals, run_average_depth_bests,
             [run_average_depth_bests - run_min_depth_bests,
              run_max_depth_bests - run_average_depth_bests],
             lw = 0.3, fmt = 'y', label = 'depth max')
plt.errorbar(run_evals, run_average_depth_bests, run_std_depth_bests,
             lw = 0.6, fmt = 'y')

plt.errorbar(run_evals, run_average_size_averages,
             [run_average_size_averages - run_min_size_averages,
              run_max_size_averages - run_average_size_averages],
             lw = 0.3, fmt = 'k', label = 'size averages')
plt.errorbar(run_evals, run_average_size_averages, run_std_size_averages,
             lw = 0.6, fmt = 'k')

plt.errorbar(run_evals, run_average_size_bests,
             [run_average_size_bests - run_min_size_bests,
              run_max_size_bests - run_average_size_bests],
             lw = 0.3, fmt = 'gray', label = 'size max')
plt.errorbar(run_evals, run_average_size_bests, run_std_size_bests,
             lw = 0.6, fmt = 'gray')


plt.title(plotfileroot)
plt.xlabel('Evaluations')
# plt.ylabel('Fitness')
plt.legend(loc='upper right')

# plt.show()

plt.savefig('plots/' + plotfileroot + '.png', dpi = 600)

# Ref:
# https://stackoverflow.com/questions/33328774/box-plot-with-min-max-average-and-standard-deviation


