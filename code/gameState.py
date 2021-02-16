# -*- coding: utf-8 -*-
import random
import copy


class GameState:
    """
    Class to hold game state for each eval/game
    """

    # Name some elements of the game map
    OPEN = ' '
    WALL = '#'
    PILL = '.'
    FRUIT = 'F'


    def __init__(self, game_map_info, pill_density, time_multiplier,
                 fruit_spawning_probability, fruit_score, num_pacs, num_ghosts):
        """
        Set up the game state given initialization parameters as listed.
        """
        # Establish member variables for given game map
        self.game_map = copy.deepcopy(game_map_info.game_map)
        self.width = game_map_info.width
        self.height = game_map_info.height
        self.num_walls = game_map_info.num_walls

        # initialize time and fruit variables
        self.orig_time = self.time = int(time_multiplier * self.width * self.height)
        self.score = 0
        self.fruit_spawning_probability = fruit_spawning_probability
        self.fruit_score = fruit_score
        self.fruit_eaten = 0

        # Establish member variables for positions
        self.pacs_pos = [[0, self.height - 1] for _ in range(num_pacs)]
        self.ghosts_pos = [[self.width - 1, 0] for _ in range(num_ghosts)]
        self.fruit_pos = [-1, -1]   # -1,-1 means not active

        # Put pills on the map
        self.orig_num_pills = self.put_pills(pill_density)
        self.num_pills_eaten = 0
        
        # Did the Ghost win?
        self.ghost_won = False


    def write_world_config(self, world_data):
        """
        Write the current state of the world to an array of strings.
        This is a lazy way of saving history, so that once we know
        a world is a high scorer, we can save this history away and
        eventually write it to a file if it's the overall highest.
        """

        # Write dimensions
        world_data.append(str(self.width) + '\n')
        world_data.append(str(self.height) + '\n')

        # Write Pac and Ghost positions
        self.write_world_positions(world_data)

        # Write walls
        for y in range(self.height):
            for x in range(self.width):
                if (self.game_map[y][x] == GameState.WALL):
                    world_data.append('w ' + str(x) + ' ' + str(y) + '\n')

        # Write pills
        for y in range(self.height):
            for x in range(self.width):
                if (self.game_map[y][x] == GameState.PILL):
                    world_data.append('p ' + str(x) + ' ' + str(y) + '\n')


    def write_world_time_score(self, world_data):
        """
        Write the time and score to the saved world data.
        """
        world_data.append('t ' + str(self.time) + ' ' + str(self.update_score()) + '\n')


    def write_world_positions(self, world_data):
        """
        Write the positions of Pac and Ghosts to the saved world data.
        """
        world_data.append('m ' + str(self.pacs_pos[0][0]) + ' ' + str(self.pacs_pos[0][1]) + '\n')
        world_data.append('1 ' + str(self.ghosts_pos[0][0]) + ' ' + str(self.ghosts_pos[0][1]) + '\n')
        world_data.append('2 ' + str(self.ghosts_pos[1][0]) + ' ' + str(self.ghosts_pos[1][1]) + '\n')
        world_data.append('3 ' + str(self.ghosts_pos[2][0]) + ' ' + str(self.ghosts_pos[2][1]) + '\n')


    def put_pills(self, pill_density):
        """
        Given a pill density, place pills on the game map and pill list.

        Returns number of pills placed.
        """

        num_pills = 0
        # Walk the list and determine for each eligible cell if it
        # will get a pill.
        for y in range(self.height):
            for x in range(self.width):
                if ((self.pacs_pos[0] != [x, y])
                    and (self.game_map[y][x] != GameState.WALL)
                    and (random.random() < pill_density)):
                    self.game_map[y][x] = GameState.PILL
                    num_pills += 1
        # print('Placed pills:', num_pills)
        return num_pills


    def check_pill(self):
        """
        If Pac is at a pill, count it as eaten and remove from the map and pill list.
        """
        if (self.game_map[self.pacs_pos[0][1]][self.pacs_pos[0][0]] == GameState.PILL):
            self.num_pills_eaten += 1
            self.game_map[self.pacs_pos[0][1]][self.pacs_pos[0][0]] = GameState.OPEN


    def put_fruit(self):
        """
        Place fruit into an eligible open cell.
        """
        # If the number of open cells <= 1, we can't place the fruit.
        # Why 1? Because if there is only 1 open cell (before the game
        # begins), Pac-Man must be in it.
        num_opens = sum([curr_row.count(GameState.OPEN) \
                              for curr_row in self.game_map])
        if (num_opens <= 1):
            print('No open cell for fruit')
            return

        # Randomly place the fruit into an open cell.
        placed = False
        while (not placed):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if ((self.game_map[y][x] == GameState.OPEN) and
                (self.pacs_pos[0] != [x, y])):
                self.fruit_pos = [x, y]
                placed = True


    def check_fruit(self, world_data):
        """
        If Pac is on fruit, count it as eaten and remove from the map.

        Independently of the above, if a random number is under the
        fruit spawning probability and there is no fruit on the board,
        spawn fruit.
        """

        # Check for and handle collision with fruit
        if (self.pacs_pos[0] == self.fruit_pos):
            self.fruit_eaten += 1
            self.fruit_pos = [-1, -1]

        # Check for and handle spawning new fruit
        if ((random.random() < self.fruit_spawning_probability)
            and (self.fruit_pos == [-1, -1])):
            self.put_fruit()
            if (self.fruit_pos != [-1, -1]):
                world_data.append('f ' + str(self.fruit_pos[0]) + ' ' + str(self.fruit_pos[1]) + '\n')


    @staticmethod
    def manhattan_distance(pos1, pos2):
        """
        Return the Manhattan distance between two positions.
        """
        return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))


    def G(self, pos, ghost_id = -1):
        """
        Given a position and a ghost_id, return Manhattan distance to nearest ghost
        that isn't the ghost identified by ghost_id. If ghost_id == -1, return
        distance to nearest ghost with no restrictions.
        """
        dist_nearest = 100000
        for curr_ghost_id in range(len(self.ghosts_pos)):
            if (curr_ghost_id != ghost_id):
                curr_dist = self.manhattan_distance(pos, self.ghosts_pos[curr_ghost_id])
                if (curr_dist < dist_nearest): dist_nearest = curr_dist
        return dist_nearest


    def P(self, pos):
        """
        Given a position, return Manhattan distance to nearest pill.
        """
        # Check increasingly large "taxicab circles" around the given position
        for radius in range(self.width + self.height):
            for i in range(radius + 1):
                if (((pos[0] - radius + i) >= 0)
                    and ((pos[1] - i) >= 0)
                    and self.game_map[pos[1] - i][pos[0] - radius + i] == GameState.PILL):
                    return radius
                if (((pos[0] - radius + i) >= 0)
                    and ((pos[1] + i) < self.height)
                    and self.game_map[pos[1] + i][pos[0] - radius + i] == GameState.PILL):
                    return radius
                if (((pos[0] + radius - i) < self.width)
                    and ((pos[1] - i) >= 0)
                    and self.game_map[pos[1] - i][pos[0] + radius - i] == GameState.PILL):
                    return radius
                if (((pos[0] + radius - i) < self.width)
                    and ((pos[1] + i) < self.height)
                    and self.game_map[pos[1] + i][pos[0] + radius - i] == GameState.PILL):
                    return radius

        # If we haven't found a pill... (should never get here!)
        print('Didn''t find pill!')
        return self.height + self.width


    def W(self, pos):
        """
        Given a position, return number of immediately adjacent walls.

        The edges of the board count as walls in this calculation.
        """

        num_walls = 0

        # Check up
        if ((pos[1] < (self.height - 1))
           and (self.game_map[pos[1] + 1][pos[0]] == GameState.WALL)):
            num_walls += 1
        # Check being at edge of map (implied wall)
        if (pos[1] == (self.height - 1)):
            num_walls += 1

        # Check down
        if ((pos[1] > 0)
           and (self.game_map[pos[1] - 1][pos[0]] == GameState.WALL)):
            num_walls += 1
        # Check being at edge of map (implied wall)
        if (pos[1] == 0):
            num_walls += 1

        # Check right
        if ((pos[0] < (self.width - 1))
           and (self.game_map[pos[1]][pos[0] + 1] == GameState.WALL)):
            num_walls += 1
        # Check being at edge of map (implied wall)
        if (pos[0] == (self.width - 1)):
            num_walls += 1

        # Check left
        if ((pos[0] > 0)
           and (self.game_map[pos[1]][pos[0] - 1] == GameState.WALL)):
            num_walls += 1
        # Check being at edge of map (implied wall)
        if (pos[0] == 0):
            num_walls += 1

        return num_walls


    def F(self, pos):
        """
        Given a position, return Manhattan distance to nearest fruit
        """
        if (self.fruit_pos == [-1, -1]):
            return self.height + self.width
        return self.manhattan_distance(pos, self.fruit_pos)


    def M(self, pos, pac_id = -1):
        """
        Given a position and a pac_id, return Manhattan distance to nearest Pac
        that isn't the Pac identified by pac_id. If pac_id == -1, return
        distance to nearest pac with no restrictions.
        """
        dist_nearest = 100000
        for curr_pac_id in range(len(self.pacs_pos)):
            if (curr_pac_id != pac_id):
                curr_dist = self.manhattan_distance(pos, self.pacs_pos[curr_pac_id])
                if (curr_dist < dist_nearest): dist_nearest = curr_dist
        return dist_nearest


    def get_valid_positions(self, pos, pac_or_ghost):
        """
        Given a position and whether it's for Pac or a Ghost,
        return a list of valid possible positions for the next turn.
        """
        positions = []

        # Check up
        if ((pos[1] < (self.height - 1))
           and (self.game_map[pos[1] + 1][pos[0]] != GameState.WALL)):
            positions.append([pos[0], pos[1] + 1])

        # Check down
        if ((pos[1] > 0)
           and (self.game_map[pos[1] - 1][pos[0]] != GameState.WALL)):
            positions.append([pos[0], pos[1] - 1])

        # Check right
        if ((pos[0] < (self.width - 1))
           and (self.game_map[pos[1]][pos[0] + 1] != GameState.WALL)):
            positions.append([pos[0] + 1, pos[1]])

        # Check left
        if ((pos[0] > 0)
           and (self.game_map[pos[1]][pos[0] - 1] != GameState.WALL)):
            positions.append([pos[0] - 1, pos[1]])

        # Because Pac doesn't have to move, add current position as an option
        if (pac_or_ghost == 'pac'): positions.append(pos)

        return positions


    def check_ghosts(self, prev_pacs_pos, prev_ghosts_pos):
        """
        If Pac has run into a ghost, return the ghost number hit.

        Check for direct collisions and crossed paths / swapped positions.
        """

        # Check for direct collisions and crossed paths / swapped positions.
        for p in range(len(self.pacs_pos)):
            for g in range(len(self.ghosts_pos)):
                if ((self.pacs_pos[p] == self.ghosts_pos[g])
                    or ((self.pacs_pos[p] == prev_ghosts_pos[g])
                        and (prev_pacs_pos[p] == self.ghosts_pos[g]))):
                        self.ghost_won = True
                        return g + 1
        return 0


    def update_score(self):
        """
        Update and return the score.
        """
        # % pills eaten
        self.score = int((self.num_pills_eaten * 100.0) / self.orig_num_pills)
        # Fruit eaten
        self.score += self.fruit_eaten * self.fruit_score
        # Time bonus if all pills eaten
        if (self.orig_num_pills == self.num_pills_eaten):
            self.score += int((self.time * 100.0) / self.orig_time)
        self.score = int(self.score)
        return self.score


    def play_turn(self, world_data, pac_controllers, ghost_controllers):
        """
        Play a turn of a game given world_data to log world updates
        and controllers for Pac and Ghosts.
        """
        game_over = False

        # Retain old positions to check for crossed paths later
        prev_pacs_pos = copy.deepcopy(self.pacs_pos)
        prev_ghosts_pos = copy.deepcopy(self.ghosts_pos)

        # Decide next moves
        for pac_controller in pac_controllers:
            pac_controller.decide_move(self)
        for ghost_controller in ghost_controllers:
            ghost_controller.decide_move(self)

        # Execute next moves
        for pac_controller in pac_controllers:
            pac_controller.execute_move(self)
        for ghost_controller in ghost_controllers:
            ghost_controller.execute_move(self)

        # Decrement time (yeah this is obvious but adding comment here is consistent)
        self.time -= 1

        # Update world data
        self.write_world_positions(world_data)

        # Hit or crossed paths with a ghost? Game over.
        ghost_hit = self.check_ghosts(prev_pacs_pos, prev_ghosts_pos)
        if (ghost_hit > 0):
            game_over = True

        # If Pac didn't hit a ghost, check for eating pills and fruit
        else:
            self.check_pill()
            self.check_fruit(world_data)

        # Score update
        self.update_score()
        self.write_world_time_score(world_data)

        # Out of time? Game over.
        if (self.time == 0):
            game_over = True

        # Ate all the pills? Game over.
        if (self.num_pills_eaten == self.orig_num_pills):
            game_over = True

        return game_over

