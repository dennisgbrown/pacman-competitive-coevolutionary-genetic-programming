# README for COMP 6666 Fall 2020 Assignment 2c
Dennis Brown / dgb0028@auburn.edu / 29 NOV 2020

## Overview & Usage

Code was written in Python 3 and is all in the "code" folder.

Run the assignment code by using run.sh as specified in the assignment instructions (see end of this document).
```
./run.sh
```
```
./run.sh optional_config_filepath
```

The working directory is assumed to be the main assignment folder containing run.sh (i.e. one level above code / logs / problems / solutions folders).

Config files are in the configs subfolder. If no config file is specified, "default.cfg" is used and you're stuck with whatever is in it.

Solution, log, and world files go into their respective subfolders; file names have the same root filename as the config files. Additionally, in Assignment 2c the CIAO data goes into the data folder and plots into the plots folder.

In most folders, there is an "exploring" subfolder that holds data from an initial exploration of individual-vs-all CCEGP. More details are in the report "assignment2c_report.pdf."

There are several config files as follows. Each is described in more detail in the report "assignment2c_report.pdf":
* GREEN 2 & 4:
    * config1.cfg: Baseline configuration
    * config2.cfg: Compared to baseline, changes parent and survival selection methods for Pac and Ghosts
    * config3.cfg: Compared to baseline, changes Ghost population size
* YELLOW 1: Cycling investigation with CIAO plots:
    * config4cyc.cfg: Compared to baseline, small Pac population size and less pressure on Ghost population
    * config5cyc.cfg: Compared to baseline, Ghost population parameters set to approach 'random'

Omitting the random seed from the config file results in initializing the random seed to an integer version of system time that is also written to the log file.

Malformed inputs generally cause the program to report an error and halt. Default values are employed where applicable, somewhat arbitrarily. User is highly encouraged to use command line and config file properly.

This code has been tested on the Tux network.

## Report

See file **assignment2c_report.pdf**

## Architecture

Execution kicks off in *start.py*, which parses command line arguments and sets up an Experiment instance.

The *Experiment* class contains the experiment parameters read from the config file, sets up the experiment, and executes the runs and evaluations of the experiment using a specified *Strategy*.

The *Strategy* class is the base class for solution strategies. It specifies initialization and execution (for one run) methods.

The *RandomStrategy* class executes one run of the experiment as directed by assignment 2a. This file has been given minor updates to continue working in the overall framework that was tweaked to support assignment 2c. For n evals, it randomly picks a map, initiates a new game state, runs the game, updates the log as needed, and returns the best results back to the Experiment instance. During each turn, its Pac-Man controller maintains a parse tree to calculate the weighted sum of G, P, W, F and determine actions Pac-Man will take; and its Ghost controller picks a random direction of valid possible directions.

The *HillClimbStrategy* class executes one run of the experiment as directed by assignment 2a. This file has been given minor updates to continue working in the overall framework that was tweaked to support assignment 2c. Up to n evals, it runs a hill climbing algorithm that systematically varies each weight of G, P, W, F by an adjustable step size to produce the neighborhood. It draws heavily from the pseudocode presented for Continuous Space Hill Climbing in https://en.wikipedia.org/wiki/Hill_climbing .

The *GPStrategy* class implements Genetic Programming search strategy as directed by assignment 2b. This file has been given minor updates to continue working in the overall framework that was tweaked to support assignment 2c. It contains methods to perform initialization, selection, mutation, recombination, etc. of a population where individuals are expression trees. Relevant details on the implementation are in the Assignment 2b report.

The *CCEGPStrategy* class is new for Assignment 2c and implements Competitive Coevolutionary Genetic Programming search strategy as directed by this assignment. It contains methods to perform initialization, selection, mutation, recombination, etc. of a population where individuals are expression trees. Compared to GPStrategy, it evolves a Ghost population in addition to the Pac-Man population. Relevant details on the implementation are in the report.

The *Population* class is also new for Assignment 2c. Since we now support multiple populations, variables and methods specific to the Pac population that were previously scattered in GPStrategy were refactored and generalized into this class.

The *CIAOPlotter* class is also new for Assignment 2c. It is called at the end of a run by CCEGPStrategy to plot a given matrix of normalized fitness values as a CIAO image and saves it to a PNG, all via matplotlib. As a standalone class, it can also load the matrix from a specified file and plot.

The *GameState* class contains the state of a Pac-Man game, a method to play a turn of the game, and helper functions to read and write files, calculate G, P, W, F, and now M, handle bookkeeping, etc.
&rarr; Each map is read from disk once and cached into a *GameMapInfo* instance.

The *GameMapInfo* class supports *GameState*. It was broken out into its own file for this assignment in an attempt to keep one class per module, except in cases where I didn't want to do that (e.g. controllers module -- class and module architecture is rather arbitrary and organic).
&rarr; The map state is stored in a 2D array indexed by row, col starting at 0. Coordinates are translated as needed when reading/writing files.

The *ExprTree* class represents an expression tree including a Node definition and methods to evaluate and print out a node (and its children, recursively). Compared to Assignment 2b, it now understands the 'M' input.

The *controllers* module holds the *PacController* and *GhostController* classes, which are basically fancy containers for an Expression Tree that can make moves with in the game. This file also holds a *RandomGhostController* class to maintain compatibility with strategies of previous assignments.

The *runPlotter* etc. modules are just helpful utilities for me to make plots. At this point the names are nonsensical and the code quality is atrocious. Please ignore them.

## Updates based on Assignment 2b feedback
* expanded the range for constant values from [-1, 1] to [-10, 10]
* k-tournament code in CCEGPStrategy was made a bit more sane to avoid choosing ineligible tournament members and having to re-choose repeatedly
* Set two depth limits: one for initialization (usually 7) and one as an overall hard maximum (usually 9)
* Doubled population sizes in most configurations

------------

# Original README contents:
#################################
#	Coding Standards	#
#################################

You are free to use any of the following programming languages for your submission :
	- Python 3
	- C++
	- C#
	- Java

NOTE : Sloppy, undocumented, or otherwise unreadable code will be penalized for not following good coding standards (as laid out in the grading rubric on the course website) : https://www.eng.auburn.edu/~drt0015/coding.html

#################################
#	Submission Rules	#
#################################

Included in your repository is a script named ”finalize.sh”, which you will use to indicate which version of your code is the one to be graded. When you are ready to submit your final version, run the command ./finalize.sh or ./finalize.sh -language_flag from your local Git directory, then commit and push your code. Running the finalize script without a language flag will cause the script to run an interactive prompt where you may enter your programming language. Alternatively, you can pass a -j flag when running the finalize script to indicate that you are submitting in Java (i.e. ./finalize.sh -j). The flag -j indicates Java, -cpp indicates C++, -cs indicates C#, and -p indicates Python 3. This script also has an interactive prompt where you will enter your Auburn username so the graders can identify you. The finalize script will create a text file, readyToSubmit.txt, that is populated with information in a known format for grading purposes. You may commit and push as much as you want, but your submission will be confirmed as ”final” if ”readyToSubmit.txt” exists and is populated with the text generated by ”finalize.sh” at 10:00pm on the due date. If you do not plan to submit before the deadline, then you should NOT run the ”finalize.sh” script until your final submission is ready. If you accidentally run ”finalize.sh” before you are ready to submit, do not commit or push your repo and delete ”readyToSubmit.txt.” Once your final submission is ready, run ”finalize.sh”, commit and push your code, and do not make any further changes to it

Late submissions will be penalized 5% for the first 24 hour period and an additional 10% for every 24 hour period thereafter.

#################################
#       Compiling & Running	#
#################################

Your final submission must include the script "run.sh" which should compile and run your code.

Your script should run on a standard linux machines with the following commands :
```
./run.sh
```
```
./run.sh optional_config
```
Note that running without a config implies the use of a default configuration file "default.cfg" and NOT the use of hardcoded values in your code.
