# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

"""
Read a log file and dump coordinates to a matplotlib plot.
"""

datafiles = [
             'config1',
             'config2',
             'config3'
             ]

plotfile = 'Individual vs Individual'

best_x_values = [[] for _ in range(len(datafiles))]
best_y_values = [[] for _ in range(len(datafiles))]

for curr_file in range(len(datafiles)):
    # The current run
    curr_x_values = []
    curr_y_values = []

    filename = 'logs/' + datafiles[curr_file] + '.txt'

    # Read the data from the file and identify the best run
    with open(filename, 'r') as reader:
        passed_config_info = False
        # read numbers
        for curr_line in reader:
            curr_line = curr_line.strip()
            #print(curr_line)

            # Skip blank lines
            if (curr_line):
                # If we've started a run, reset the current values
                # and note that we've passed the config info so everything
                # past here should be eval numbers or "Run x"
                if (curr_line.startswith('Run')):
                    curr_x_values = []
                    curr_y_values = []
                    passed_config_info = True

                # If the log file is properly formed we can assume this
                # line contains two tab-separated numbers.
                elif (passed_config_info):
                    coord_list = list(curr_line.split("\t"))
                    x = float(coord_list[0])
                    y = float(coord_list[2])
                    curr_x_values.append(x)
                    curr_y_values.append(y)

                    # If we don't have best values yet, OR,
                    # if the current y value is greater than the max
                    # of the best y values, then just make the best
                    # values be a copy of the current lists.
                    # This approach will make more list copies than a
                    # smarter algorithm, but it's simple and it works
                    # because y values are monotonically increasing
                    # within each run.
                    if ((len(best_y_values[curr_file]) == 0)
                        or (y > max(best_y_values[curr_file]))):
                        best_x_values[curr_file] = curr_x_values.copy()
                        best_y_values[curr_file] = curr_y_values.copy()

    # Add final element to complete top stair step.
    # We magically know there were 2000 evals.
    best_x_values[curr_file].append(2000)
    best_y_values[curr_file].append(best_y_values[curr_file][-1])

    print('final best x for:', datafiles[curr_file], best_x_values[curr_file])
    print('final best y for:', datafiles[curr_file], best_y_values[curr_file])

    # Create the scatter plot of the best run
    plt.step(best_x_values[curr_file], best_y_values[curr_file],
             label = datafiles[curr_file])

plt.title(plotfile + ' Best Runs')
plt.xlabel('Evaluations')
plt.ylabel('Fitness')
plt.xlim(left = 0)
plt.ylim(bottom = 0)
plt.grid(True)
plt.legend(loc='lower right')
plt.savefig('plots/' + plotfile + '.png', dpi = 600)

