# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy
import traceback

"""
Read a log file plot best vs. average with "error bars" to show min-max range
"""

fileroot = 'config5cyc'

filename = 'logs/' + fileroot + '.txt'

curr_run = -1
run_evals = []
run_average_lists = []
run_best_lists = []
lineno = 0

with open(filename, 'r') as reader:
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
                if (len(run_average_lists) < (curr_eval + 1)):
                    run_average_lists.append([])
                if (len(run_best_lists) < (curr_eval + 1)):
                    run_best_lists.append([])
                run_average_lists[curr_eval].append(float(data_list[1]))
                run_best_lists[curr_eval].append(float(data_list[2]))
                curr_eval += 1
            except:
                print('Problem in line ' + str(lineno) + ': |' + curr_line + '|')
                traceback.print_exc()
                pass

        curr_line = reader.readline()

run_evals = numpy.array(run_evals)
run_average_averages = numpy.zeros(len(run_evals))
run_max_averages = numpy.zeros(len(run_evals))
run_min_averages = numpy.zeros(len(run_evals))
run_std_averages = numpy.zeros(len(run_evals))
run_average_bests = numpy.zeros(len(run_evals))
run_max_bests = numpy.zeros(len(run_evals))
run_min_bests = numpy.zeros(len(run_evals))
run_std_bests = numpy.zeros(len(run_evals))

for i in range(len(run_evals)):
    run_average_averages[i] = numpy.mean(run_average_lists[i])
    run_max_averages[i] = numpy.amax(run_average_lists[i])
    run_min_averages[i] = numpy.amin(run_average_lists[i])
    run_std_averages[i] = numpy.std(run_average_lists[i])
    run_average_bests[i] = numpy.mean(run_best_lists[i])
    run_max_bests[i] = numpy.amax(run_best_lists[i])
    run_min_bests[i] = numpy.amin(run_best_lists[i])
    run_std_bests[i] = numpy.std(run_best_lists[i])


# Fudge factor: plot the averages 10 units offset so we can see them better
plt.errorbar(run_evals + 10, run_average_averages,
             [run_average_averages - run_min_averages,
              run_max_averages - run_average_averages],
             lw = 0.3, ecolor = 'red', fmt = 'r', label = 'averages')
plt.errorbar(run_evals, run_average_averages, run_std_averages,
             lw = 0.6, ecolor = 'red', fmt = 'r')

plt.errorbar(run_evals, run_average_bests,
             [run_average_bests - run_min_bests,
              run_max_bests - run_average_bests],
             lw = 0.3, ecolor = 'blue', fmt = 'b', label = 'bests')
plt.errorbar(run_evals, run_average_bests, run_std_bests,
             lw = 0.6, ecolor = 'blue', fmt = 'b')

plt.title(fileroot)
plt.xlabel('Evaluations')
plt.ylabel('Fitness')
plt.legend(loc='lower right')

# plt.show()

plt.savefig('plots/' + fileroot + '.png', dpi = 600)

# Ref:
# https://stackoverflow.com/questions/33328774/box-plot-with-min-max-average-and-standard-deviation


