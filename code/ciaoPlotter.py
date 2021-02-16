# -*- coding: utf-8 -*-
import numpy
import matplotlib.pyplot as plt

class CIAOPlotter():
    """
    Create a CIAO Plot using matlobplot's imshow function.

    This is a standalone class & file so that it can be used outside of
    the competitive coevolution GP code.
    """

    @staticmethod
    def plot(file_root, fitnesses):
        """
        Plot given fitnesses array as an image and save to filename based
        on file_root.
        """
        # We can plot the fitness matrix as-is
        plt.imshow(fitnesses, cmap = 'gray')
        plt.title(file_root + ' CIAO Plot')
        plt.xlabel('Best of Ghost Generations')
        plt.ylabel('Best of Pac Generations')

        # Change tick marks to indicate generation numbers
        num_gens = fitnesses.shape[0]
        x_positions = numpy.arange(num_gens)
        y_positions = numpy.arange(num_gens - 1, -1, step = -1)
        gen_labels = numpy.arange(1, num_gens + 1)
        plt.xticks(x_positions, gen_labels, fontsize = 4)
        plt.yticks(y_positions, gen_labels, fontsize = 4)

        # Save the plot
        plt.savefig('plots/' + file_root + '_CIAO_Plot.png', dpi = 600)


if __name__ == '__main__':
    file_root ='default_Run1'
    fitnesses = numpy.loadtxt('data/' + file_root + '_CIAO_Data.txt')
    CIAOPlotter.plot(file_root, fitnesses)
