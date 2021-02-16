# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy
import scipy.stats as stats
import traceback


"""
Plot the bests from two files and dump them to csv for easy read into Excel.
"""


def read_file(filename):
    """
    Read the results of the log file and return a list of the best of each run.
    """

    curr_run = -1
    lineno = 0
    last_best = -1

    bests = []

    with open(filename, 'r') as reader:
       curr_line = reader.readline()
       while (curr_line):
            lineno += 1
            curr_line = curr_line.strip()

            if (curr_line.startswith('Run')):
                curr_run += 1
                last_best = -1
            elif (curr_run > -1):
                if (len(curr_line) == 0):
                    bests.append(last_best)
                else:
                    try:
                        data_list = list(curr_line.split("\t"))
                        last_best = float(data_list[2])
                        #print('found new last_best', last_best)
                    except:
                        print('Problem in line ' + str(lineno) + ': |' + curr_line + '|')
                        traceback.print_exc()
                        pass

            curr_line = reader.readline()

    bests.append(last_best)

    return bests


# Compare two log files

fileroot1 = 'config1'
fileroot2 = 'config1'
combo_fileroot = fileroot1 + '-' + fileroot2

filename1 = 'logs/exploring/' + fileroot1 + '.txt'
filename2 = 'logs/' + fileroot2 + '.txt'

bests1 = read_file(filename1)
bests2 = read_file(filename2)
runs = numpy.linspace(1, len(bests1), num = len(bests1), endpoint=True)

# Calculate F-Test Two-Sample for Variances
mean1 = numpy.mean(bests1)
mean2 = numpy.mean(bests2)
var1 = numpy.var(bests1, ddof=1)
var2 = numpy.var(bests2, ddof=1)
obs = len(bests1)
ft_df = obs - 1
f = var1/var2
ft_p = stats.f.cdf(f, ft_df, ft_df)
alpha = 0.05
fcrit = stats.f.ppf(alpha, ft_df, ft_df)

have_equal_variances = False

print('-----------------------------')
print('\\begin{figure}[H]')
print('\\caption{' + fileroot1 + ' vs. ' + fileroot2 + ' -- Best values over ' + str(obs) + ' runs}')
print('\\centering')
print('\\includegraphics[width=8cm]{' + combo_fileroot + '.png}')
print('\\label{fig:' + combo_fileroot + '}')
print('\\end{figure}')
print()
print('\\begin{table}[H]')
print('\\centering')
print('\\caption{F-Test for ' + fileroot1 + ' vs. ' + fileroot2 + ' with $\\alpha = ' + str(alpha) + '$}')
print('\\label{tab:ftest-' + combo_fileroot + '}')
print('\\begin{tabular}{lll}')
print('\\hline')
print(' & ' + fileroot1 + ' & ' + fileroot2 + ' \\\\ \\hline')
print('\\multicolumn{1}{|l|}{Mean}     & \\multicolumn{1}{l|}{' + str(mean1) + '} & \\multicolumn{1}{l|}{' + str(mean2) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{Variance}     & \\multicolumn{1}{l|}{' + str(var1) + '} & \\multicolumn{1}{l|}{' + str(var2) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{Observations}     & \\multicolumn{1}{l|}{' + str(obs) + '} & \\multicolumn{1}{l|}{' + str(obs) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{df}     & \\multicolumn{1}{l|}{' + str(ft_df) + '} & \\multicolumn{1}{l|}{' + str(ft_df) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{F}     & \\multicolumn{1}{l|}{' + str(f) + '} & \\multicolumn{1}{l|}{} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{P(F$\leq$f) one-tail}     & \\multicolumn{1}{l|}{' + str(ft_p) + '} & \\multicolumn{1}{l|}{} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{F Critical one-tail}     & \\multicolumn{1}{l|}{' + str(fcrit) + '} & \\multicolumn{1}{l|}{} \\\\ \\hline')
print('\\end{tabular}')
print('\\end{table}')
print()

if (abs(mean1) > abs(mean2)) and (f < fcrit):
    print('\\noindent abs(mean 1) $>$ abs(mean 2) and F $<$ F Critical implies equal variances.')
    have_equal_variances = True
if (abs(mean1) > abs(mean2)) and (f > fcrit):
    print('\\noindent abs(mean 1) $>$ abs(mean 2) and F $>$ F Critical implies unequal variances.')
    have_equal_variances = False
if (abs(mean1) < abs(mean2)) and (f > fcrit):
    print('\\noindent abs(mean 1) $<$ abs(mean 2) and F $>$ F Critical implies equal variances.')
    have_equal_variances = True
if (abs(mean1) < abs(mean2)) and (f < fcrit):
    print('\\noindent abs(mean 1) $<$ abs(mean 2) and F $<$ F Critical implies unequal variances.')
    have_equal_variances = False
print()

# Calculate T-Test Two-Sample for equal or unequal variances
tt_df = (obs * 2) - 2
tcrit_two_tail = stats.t.ppf(1.0 - (alpha/2), tt_df)
(tstat, tt_p_two_tail) = stats.ttest_ind(bests1, bests2, equal_var=have_equal_variances)

print('\\begin{table}[H]')
print('\\centering')
print('\\caption{t-Test for ' + fileroot1 + ' vs. ' + fileroot2 + ' with ')
if (have_equal_variances):
    print('Equal Variances}')
else:
    print('Unequal Variances}')
print('\\label{tab:ttest-' + combo_fileroot + '}')
print('\\begin{tabular}{lll}')
print('\\hline')
print(' & ' + fileroot1 + ' & ' + fileroot2 + ' \\\\ \\hline')
print('\\multicolumn{1}{|l|}{Mean}     & \\multicolumn{1}{l|}{' + str(mean1) + '} & \\multicolumn{1}{l|}{' + str(mean2) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{Variance}     & \\multicolumn{1}{l|}{' + str(var1) + '} & \\multicolumn{1}{l|}{' + str(var2) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{Observations}     & \\multicolumn{1}{l|}{' + str(obs) + '} & \\multicolumn{1}{l|}{' + str(obs) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{df}     & \\multicolumn{1}{l|}{' + str(tt_df) + '} & \\multicolumn{1}{l|}{' + str(ft_df) + '} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{t Stat}     & \\multicolumn{1}{l|}{' + str(tstat) + '} & \\multicolumn{1}{l|}{} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{P(T$\leq$t) two-tail}     & \\multicolumn{1}{l|}{' + str(tt_p_two_tail) + '} & \\multicolumn{1}{l|}{} \\\\ \\hline')
print('\\multicolumn{1}{|l|}{t Critical two-tail}     & \\multicolumn{1}{l|}{' + str(tcrit_two_tail) + '} & \\multicolumn{1}{l|}{} \\\\ \\hline')
print('\\end{tabular}')
print('\\end{table}')
print()

if (abs(tstat) > abs(tcrit_two_tail)):
    print('\\noindent abs(t Stat) $>$ abs(t Critical two-tail) so we reject the null hypothesis -- the two samples are statistically different.')
    print('The average improvement of ' + fileroot1 + ' over ' + fileroot2 + ' is ' + str(mean1 - mean2) + '.')
else:
    print('\\noindent abs(t Stat) $<$ abs(t Critical two-tail) so we accept the null hypothesis -- the two samples are NOT statistically different.')
print('-----------------------------')

# # Dump the data to CSV for Excel
# writer = open('data/' + combo_fileroot + '.csv', 'w')
# for i in range(len(bests1)):
#     writer.write(str(bests1[i]) + ', ' + str(bests2[i]) + '\n');
# writer.close()

# Plot the data
overall_max = numpy.max([numpy.max(bests1), numpy.max(bests2)])
bins = numpy.arange(0, overall_max + 1, (overall_max / 10.0))
plt.hist([bests1, bests2], bins, label = [fileroot1, fileroot2])

plt.title('Bests: ' + fileroot1 + ' and ' + fileroot2)
plt.xlabel('Fitness')
plt.ylabel('Number of bests')
plt.legend(loc='upper right')

plt.savefig('plots/' + combo_fileroot + '.png', dpi = 600)


