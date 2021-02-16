# -*- coding: utf-8 -*-
import random
import sys

sys.path.append('code')


class PacController():
    """
    Pac-Man controller
    """
    def __init__(self, pac_id, tree):
        """
        Initialization requires the expression tree asociated with this controller.
        """
        self.pac_id = pac_id
        self.tree = tree
        self.next_move = None


    def decide_move(self, game_state):
        """
        To device next move, calculate the value of each possible move
        and pick the highest.
        """
        # Get all possible moves
        valid_pos = game_state.get_valid_positions(game_state.pacs_pos[self.pac_id], 'pac')
        # Get the value of the expression tree for each possible move.
        # Feed the calculator the values of G, P, W, F, M instead of
        # recalculating those values each time we hit them in the tree.
        valid_pos_vals = [ self.tree.root.calc([game_state.G(pos),
                                                game_state.P(pos),
                                                game_state.W(pos),
                                                game_state.F(pos),
                                                game_state.M(pos, pac_id = self.pac_id)]) \
                          for pos in valid_pos ]
        # Find the index of the highest-valued move
        new_pos_idx = valid_pos_vals.index(max(valid_pos_vals))
        # Set the next move
        self.next_move = valid_pos[new_pos_idx]


    def execute_move(self, game_state):
        """
        Actually execute the stored move
        """
        game_state.pacs_pos[self.pac_id] = self.next_move


class GhostController():
    """
    Ghost controller
    """
    def __init__(self, ghost_id, tree):
        """
        Use instances of the same class for each ghost -- need to know
        which ghost this class instance is for.
        """
        self.ghost_id = ghost_id
        self.tree = tree
        self.next_move = None


    def decide_move(self, game_state):
        """
        Decide next move for a ghost: Randomly pick a valid move.
        """
        # Get all possible moves
        valid_pos = game_state.get_valid_positions(game_state.ghosts_pos[self.ghost_id],
                                                   'ghost')
        # Get the value of the expression tree for each possible move.
        # Feed the calculator the values of G, P, W, F, M instead of
        # recalculating those values each time we hit them in the tree.
        valid_pos_vals = [ self.tree.root.calc([game_state.G(pos, ghost_id = self.ghost_id),
                                                game_state.P(pos),
                                                game_state.W(pos),
                                                game_state.F(pos),
                                                game_state.M(pos)]) \
                          for pos in valid_pos ]
        # Find the index of the highest-valued move
        new_pos_idx = valid_pos_vals.index(max(valid_pos_vals))
        # Set the next move
        self.next_move = valid_pos[new_pos_idx]


    def execute_move(self, game_state):
        """
        Actually execute the stored move
        """
        # Set new location based on which ghost this is
        game_state.ghosts_pos[self.ghost_id] = self.next_move


class RandomGhostController():
    """
    Random Ghost controller (as used by assignments 2a and 2b)
    """
    def __init__(self, ghost_id):
        """
        Use instances of the same class for each ghost -- need to know
        which ghost this class instance is for.
        """
        self.ghost_id = ghost_id
        self.next_move = None


    def decide_move(self, game_state):
        """
        Decide next move for a ghost: Randomly pick a valid move.
        """
        # Get starting position based on which ghost this is
        pos = game_state.ghosts_pos[self.ghost_id]

        # Get a list of valid new positions and pick one randomly
        valid_pos = game_state.get_valid_positions(pos, 'ghost')
        new_pos_idx = random.randint(0, len(valid_pos) - 1)
        self.next_move = valid_pos[new_pos_idx]


    def execute_move(self, game_state):
        """
        Actually execute the stored move
        """
        # Set new location based on which ghost this is
        game_state.ghosts_pos[self.ghost_id] = self.next_move

