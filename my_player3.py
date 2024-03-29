import random
import sys
from read import readInput, readOutput
from write import writeOutput, writeNextInput
from copy import deepcopy
import pdb
import os


class QLearningPlayer():
    def __init__(self):
        pass

    def get_input(self, go, piece_type):
        pass


'''
copied from host.py as directed by the faculty.
'''


class GO:
    def __init__(self, n):
        """
        Go game.

        :param n: size of the board n*n
        """
        self.size = n
        # self.previous_board = None # Store the previous board
        self.X_move = True  # X chess plays first
        self.died_pieces = []  # Intialize died pieces to be empty
        self.n_move = 0  # Trace the number of moves
        self.max_move = n * n - 1  # The max movement of a Go game
        self.komi = n/2  # Komi rule
        self.verbose = False  # Verbose only when there is a manual player

    def init_board(self, n):
        '''
        Initialize a board with size n*n.

        :param n: width and height of the board.
        :return: None.
        '''
        board = [[0 for x in range(n)]
                 for y in range(n)]  # Empty space marked as 0
        # 'X' pieces marked as 1
        # 'O' pieces marked as 2
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        '''
        Initialize board status.
        :param previous_board: previous board state.
        :param board: current board state.
        :return: None.
        '''

        # 'X' pieces marked as 1
        # 'O' pieces marked as 2

        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        # self.piece_type = piece_type
        self.previous_board = previous_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0:
            neighbors.append((i-1, j))
        if i < len(board) - 1:
            neighbors.append((i+1, j))
        if j > 0:
            neighbors.append((i, j-1))
        if j < len(board) - 1:
            neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def num_pieces_in_the_center(self, piece_type):
        line_2 = [
            [1, 1],
            [1, 2],
            [1, 3],
            [2, 1],
            [2, 2],
            [2, 3],
            [3, 1],
            [3, 2],
            [3, 3]
        ]
        board = self.board
        num_pieces = 0
        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if [i, j] in line_2 and board[i][j] == piece_type:
                    num_pieces += 1
        return num_pieces

    def find_died_pieces(self, piece_type):
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j):
                        died_pieces.append((i, j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        '''
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces:
            return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        '''
        Remove the stones of certain locations.

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        '''
        Place a chess stone in the board.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        # self.n_move += 1
        return True

    def valid_place_check(self, i, j, piece_type, test_check=False):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board
        verbose = self.verbose
        if test_check:
            verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(
                    len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(
                    len(board) - 1))
            return False

        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False

        # Copy the board for testing
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        # If not, remove the died pieces of opponent and check again
        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                if verbose:
                    print(
                        'Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True

    def update_board(self, new_board):
        '''
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''
        self.board = new_board

    def visualize_board(self):
        '''
        Visualize the board.

        :return: None
        '''
        board = self.board

        print('-' * len(board) * 2)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * len(board) * 2)

    def game_end(self, piece_type, action="MOVE"):
        '''
        Check if the game should end.

        :param piece_type: 1('X') or 2('O').
        :param action: "MOVE" or "PASS".
        :return: boolean indicating whether the game should end.
        '''

        # Case 1: max move reached
        if self.n_move >= self.max_move:
            return True
        # Case 2: two players all pass the move.
        if self.compare_board(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):
        '''
        Get score of a player by counting the number of stones.

        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the game should end.
        '''

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt

    def judge_winner(self):
        '''
        Judge the winner of the game by number of pieces for each player.

        :param: None.
        :return: piece type of winner of the game (0 if it's a tie).
        '''

        cnt_1 = self.score(1)
        cnt_2 = self.score(2)
        if cnt_1 > cnt_2 + self.komi:
            return 1
        elif cnt_1 < cnt_2 + self.komi:
            return 2
        else:
            return 0

    def play(self, player1, player2, verbose=False):
        '''
        The game starts!

        :param player1: Player instance.
        :param player2: Player instance.
        :param verbose: whether print input hint and error information
        :return: piece type of winner of the game (0 if it's a tie).
        '''
        self.init_board(self.size)
        # Print input hints and error message if there is a manual player
        if player1.type == 'manual' or player2.type == 'manual':
            self.verbose = True
            print('----------Input "exit" to exit the program----------')
            print('X stands for black chess, O stands for white chess.')
            self.visualize_board()

        verbose = self.verbose
        # Game starts!
        while 1:
            piece_type = 1 if self.X_move else 2

            # Judge if the game should end
            if self.game_end(piece_type):
                result = self.judge_winner()
                if verbose:
                    print('Game ended.')
                    if result == 0:
                        print('The game is a tie.')
                    else:
                        print('The winner is {}'.format(
                            'X' if result == 1 else 'O'))
                return result

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(player + " makes move...")

            # Game continues
            if piece_type == 1:
                action = player1.get_input(self, piece_type)
            else:
                action = player2.get_input(self, piece_type)

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(action)

            if action != "PASS":
                # If invalid input, continue the loop. Else it places a chess on the board.
                if not self.place_chess(action[0], action[1], piece_type):
                    if verbose:
                        self.visualize_board()
                    continue

                self.died_pieces = self.remove_died_pieces(
                    3 - piece_type)  # Remove the dead pieces of opponent
            else:
                self.previous_board = deepcopy(self.board)

            if verbose:
                self.visualize_board()  # Visualize the board again
                print()

            self.n_move += 1
            print("updated n_move, ", self.n_move)
            self.X_move = not self.X_move  # Players take turn


def judge(n_move, verbose=False):

    N = 5

    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.verbose = verbose
    go.set_board(piece_type, previous_board, board)
    go.n_move = n_move
    try:
        action, x, y = readOutput()
    except:
        print("output.txt not found or invalid format")
        sys.exit(3-piece_type)

    if action == "MOVE":
        if not go.place_chess(x, y, piece_type):
            print('Game end.')
            print('The winner is {}'.format(
                'X' if 3 - piece_type == 1 else 'O'))
            sys.exit(3 - piece_type)

        go.died_pieces = go.remove_died_pieces(3 - piece_type)

    if verbose:
        go.visualize_board()
        print()

    if go.game_end(piece_type, action):
        result = go.judge_winner()
        if verbose:
            print('Game end.')
            if result == 0:
                print('The game is a tie.')
            else:
                print('The winner is {}'.format('X' if result == 1 else 'O'))
        sys.exit(result)

    piece_type = 2 if piece_type == 1 else 1

    if action == "PASS":
        go.previous_board = go.board
    writeNextInput(piece_type, go.previous_board, go.board)

    sys.exit(0)


'''
implementation notes

start building the tree after a few turns so the choices actually have an effect
depth: 4, branching factor: 10
steps:
-get current state
-build the tree as a member variable
-once the tree has been built to a certain depth, score all the nodes
-(alpha beta step: prune the nodes that do not need to be evaluated)
-choose the node of the root that has the highest evaluation

evaluation function for each state according to a strategy
- number of stones on the center
- number of stones on the edges
- number of stones on the board for each player - score function
- number of stones captured
other strategies
- do not place stones on the edges on your first turn
change the depth and branching factors depending on the time you have left
e.g. search more when you have time; search less when you have less



questions
-since we have go = GO(N), is it okay to use the member functions of go?
-in get_input, we use go.size

tasks
-account for when both players pass
    -the opponent can play again even if you pass
-evaluate only at the leaf nodes
'''


class Node:
    
    def __init__(self):
        self.board = None
        #move that resulted in this state
        self.move = [-1, -1]
        self.score = -100
        #player who is making the next move
        self.piece_type = 0
        self.terminal = False
        self.children = []
    
    
    '''
    def __init__(self, data, move, score, piece_type):
        self.go = data
        self.move = [-1, -1]
        self.score = score
        self.piece_type = 0
        self.children = []
        # self.num_moves = 0
        # self.board = []
        # self.previous_board = []
    '''

    def addChild(self, node):
        self.children.append(node)


class MinimaxPlayer():
    def __init__(self):
        self.type = 'minimax'
        # self.num_moves = 0
        self.minimax_tree = Node()  # make a node with the current state
        self.piece_type = 0

    def write_num_moves(self, num_moves):
        f = open("num_moves.txt", "w")
        f.write(str(num_moves))

    def get_num_moves(self):
        file = open('num_moves.txt', 'r')
        lines = file.readlines()

        num_moves = 0
        for line in lines:
            num_moves = int(line.strip())
            break

        return num_moves

    '''
    Get one input.

    :param go: Go instance.
    :param piece_type: 1('X') or 2('O').
    :return: (row, column) coordinate of input.
    '''

    def get_input(self, go, piece_type):

        test = True

        # determine the number of moves that've been played
        num_moves_previous = 0
        num_moves_current = 0
        num_moves = 0
        previous_player_passed = True
        for i in range(go.size):
            for j in range(go.size):
                if go.previous_board[i][j] != 0:
                    num_moves_previous += 1
                if go.board[i][j] != 0:
                    num_moves_current += 1
                if go.previous_board[i][j] != go.board[i][j]:
                    previous_player_passed = False
        if num_moves_previous == 0 and num_moves_current == 0:
            self.write_num_moves(num_moves)
        elif num_moves_previous == 0:
            num_moves += 1  # account for the opponent's move
            self.write_num_moves(num_moves)
        else:
            num_moves = self.get_num_moves()
            num_moves += 1  # account for the opponent's move
            self.write_num_moves(num_moves)

        #check if previous player passed

        print("num moves:", self.get_num_moves())
        # decides the number of depth of the minimax tree
        turn_number = self.get_num_moves() + 1



        #don't place pieces on the third line in the beginning
        #assume no pieces would be captured
        if test == True:
            current_node = Node()
            current_node.board = deepcopy(go)
            current_node.move = [-1, -1]
            current_node.piece_type = piece_type
            #print("move:", (self.build_minimax_tree(current_node, 2, -101, 101, True)).move)
            return (self.build_minimax_tree(current_node, 2, -101, 101, True)).move
            #print("next move:", current_node.next_move)
            #return [-1, -1]


        elif turn_number < 7:
            possible_placements = []
            for i in range(1, go.size-1):
                for j in range(1, go.size-1):
                    if go.valid_place_check(i, j, piece_type, test_check=True):
                        possible_placements.append((i, j))
            num_moves += 1
            self.write_num_moves(num_moves)
            return random.choice(possible_placements)

        elif turn_number >= 7 and turn_number < 25:
            # if you go last, you would only need to make a tree of depth 2 (1 for current state)
            print("building minimax tree")
            # self.build_minimax_tree(go, piece_type, 1)
            root = Node(go)
            # root is at depth 1, and it's the current state
            if piece_type == 2:  # O, num_moves == even
                # depth_max = 4  # exits when depth == depth_max
                depth_max = 2
                depth_start = 0
                self.build_minimax_tree_recursive(
                    root, piece_type, depth_max, depth_start, previous_player_passed)
                maxNode = self.read_minimax_tree_recursive(
                    root, True, depth_max, depth_start)
                # get the child that has the most optimal move
                #maxChild = Node(0)
                for child in maxNode.children:
                    if child.score >= maxChild.score:
                        maxChild = child
                print("max evaluation: ", maxChild.move,
                        "move: ", maxChild.move)

                num_moves += 1
                self.write_num_moves(num_moves)
                return maxChild.move
            else:
                # depth_max = 5
                depth_max = 2
                depth_start = 0
                self.build_minimax_tree_recursive(
                    root, piece_type, depth_max, depth_start, previous_player_passed)
                maxNode = self.read_minimax_tree_recursive(
                    root, True, depth_max, depth_start)
                # get the child that has the most optimal move
                #maxChild = Node(0)
                for child in maxNode.children:
                    if child.score >= maxChild.score:
                        maxChild = child
                print("max evaluation: ", maxChild.move,
                        "move: ", maxChild.move)
                num_moves += 1
                self.write_num_moves(num_moves)
                return maxChild.move

    #prune
    def alpha_beta_prune(self, node, depth, alpha, beta, isMax):
        if (depth == 0 or node.terminal):
            return node.score
        if isMax:
            score = -101
            for child in node.children:
                score = max(score, self.alpha_beta_prune(child, depth - 1, alpha, beta, False))
                if score >= beta:
                    break #beta cut off
                alpha = max(alpha, score)
            return score
        else:
            score = 101
            for child in node.children:
                score = min(score, self.alpha_beta_prune(child, depth - 1, alpha, beta, True))
                if score <= alpha:
                    break #alpha cutoff
                beta = min(beta, score)
            return score
    
    #def alpha_beta_prune_2()




    def read_minimax_tree_recursive(self, root, isMax, depth_max, depth):
        print("minimax tree read recursive called, move: ",
              root.move, "is max:", isMax, "score:", root.score)
        # pdb.set_trace()
        if depth == depth_max:
            return root

        if isMax:
            root.score = -100  # negative infinity

            for node in root.children:
                maxNode = self.read_minimax_tree_recursive(
                    node, not isMax, depth_max, depth+1)
                if maxNode.score >= root.score:
                    root.score = maxNode.score

            #maxNode.move = root.move
            print("max's score", root.score,
                  "length of children:", len(root.children))
            return root

        else:
            #minNode = Node(0)
            root.score = +100  # positive infinity

            for node in root.children:
                minNode = self.read_minimax_tree_recursive(
                    node, not isMax, depth_max, depth+1)
                if minNode.score <= root.score:
                    root.score = minNode.score

            # the returned move should be the root's move, not the child's
            #minNode.move = root.move
            print("min's score", root.score,
                  "length of children:", len(root.children))
            return root

    # this will always be in the perspective of my_player
    # if it's a terminal state, win: +1, loss: 0, draw: 0.5
    # connections
    # the difference in the number of pieces; would account for captures
    # the eye

    '''
    def evaluate(self, node, piece_type, terminal):
        if terminal:
            if node.go.judge_winner() == piece_type:
                return 15
            elif node.go.judge_winner() == (3-piece_type):
                return 0
            elif node.go.judge_winner() == 0:
                return 7.5
        else:
            # factors
            # difference in the number of stones on the board
            
            print("evaluating non-terminal node:", node.go.num_pieces_captured)
            return node.go.num_pieces_captured
            
            print("evaluating non-terminal node:", node.go.score(piece_type) - node.go.score(3-piece_type))
            return node.go.score(piece_type) - node.go.score(3-piece_type)
    '''

    #def evaluate(self, node):



    
    def build_minimax_tree(self, node, depth, alpha, beta, isMax):
        print("depth:", depth)
        if depth == 0 or node.terminal:
            #node.terminal = True
            #node.score = self.evaluate(node)
            node.score = random.randint(1, 20)
            print("terminal node's score:", node.score, "move:", node.move)
            return node
        


        if isMax:
            branching_factor = 5
            num_branches = 0
            node.score = -102
            #for child in node.children:

            for i in range(node.board.size):
                for j in range(node.board.size):
                    if node.board.valid_place_check(i, j, node.piece_type):
                        num_branches += 1
                        child = deepcopy(node)
                        child.move = [i, j]
                        child.piece_type = (3-node.piece_type)
                        child.board.place_chess(i, j, node.piece_type)
                        child.board.remove_died_pieces(3-node.piece_type)
                        if num_branches < branching_factor:
                            node.addChild(child)

            for child in node.children:
                if node.score < (self.build_minimax_tree(child, depth - 1, alpha, beta, False)).score:
                    node.move = child.move
                    node.score = (self.build_minimax_tree(child, depth - 1, alpha, beta, False)).score
                
                if node.score >= beta:
                    print("node.score:", node.score, "beta:", beta, "break")
                    break
                alpha = max(alpha, node.score)
            print("max score:", node.score, "move:", node.move)
            return node
            
        else:
            branching_factor = 5
            num_branches = 0
            node.score = 102

            for i in range(node.board.size):
                for j in range(node.board.size):
                    if node.board.valid_place_check(i, j, node.piece_type):
                        num_branches += 1
                        child = deepcopy(node)
                        child.move = [i, j]
                        child.piece_type = (3-node.piece_type)
                        child.board.place_chess(i, j, node.piece_type)
                        child.board.remove_died_pieces(3-node.piece_type)
                        if num_branches < branching_factor:
                            
                            node.addChild(child)

            for child in node.children:
                if node.score > (self.build_minimax_tree(child, depth-1, alpha, beta, True)).score:
                    node.move = child.move
                    node.score = (self.build_minimax_tree(child, depth-1, alpha, beta, True)).score
                if node.score <= alpha:
                    print("node.score:", node.score, "alpha:", alpha, "break")
                    break
                beta = min(beta, node.score)
            print("min score:", node.score, "move:", node.move)
            return node
            
        
        for i in range(node.board.size):
            for j in range(node.board.size):
                if node.board.valid_place_check(i, j, node.piece_type):
                    num_branches += 1
                    if num_branches >= branching_factor:
                        pass
                    else:
                        child = Node()
                        child.move = [i, j]
                        child.board = deepcopy(node.board)
                        child.board.place_chess(i, j, piece_type)
                        child.board.remove_died_pieces(3-piece_type)
                        #prune: don't add the child if ??? condition
                        node.addChild(child)
                        self.build_minimax_tree(child, depth-1, not isMax)
                        
                        '''
                        if child.score > node.score:
                            node.score = child.score
                            node.next_move = child.move
                            '''
                    #print("node's score:", node.score, "node's move:", node.next_move)
    

                        



    def build_minimax_tree_recursive(self, root, piece_type, depth_max, depth, previous_player_passed):
        print("depth", depth, "depth max:", depth_max)
        if depth == depth_max:  # maximum depth to explore
            print("returning root")
            return root

        current_state = deepcopy(root.go)
        branching_factor = 4  # observation
        num_branches = 0
        valid_place_found = False
        for i in range(current_state.size):
            for j in range(current_state.size):
                if current_state.valid_place_check(i, j, piece_type, test_check=True):
                    valid_place_found = True
                    num_branches += 1
                    if num_branches >= branching_factor:
                        pass
                    else:
                        next_state = deepcopy(current_state)
                        next_state.place_chess(i, j, piece_type)
                        next_state.num_pieces_captured = len(
                            next_state.find_died_pieces(3-piece_type))
                        next_state.remove_died_pieces(3-piece_type)
                        child = Node(next_state)
                        child.move = [i, j]
                        # child.num_moves += 1
                        # pass the node to check if it has any children
                        print("move", i,
                              j, "piece type", piece_type)
                        # evaluate the state if it's terminal
                        # added 1 to make it the turn number
                        if (self.get_num_moves()+1+(depth)) == 24:
                            # evaluate in the perspective of the player
                            child.score = self.evaluate(
                                child, self.piece_type, True)
                        elif (depth == depth_max - 1):
                            child.score = self.evaluate(
                            child, self.piece_type, False)
                            #child.score = self.evaluate(
                            #    child, self.piece_type, False)
                        print("evaluation ", child.score)
                        root.addChild(child)

                        self.build_minimax_tree_recursive(
                            child, 3-piece_type, depth_max, depth+1, previous_player_passed)
        # exits the loop if there was no valid place; the only action left is to pass
        # if both players pass, return the node as a terminal state
        if not valid_place_found:
            if previous_player_passed:
            #if root.move == [-1, -1]:
                print("both players passed")
                root.score = self.evaluate(root, self.piece_type, True)
                return root
            else:
                print(str(piece_type), "player passes\n")
                child = Node(current_state)
                child.move = [-1, -1]
                root.addChild(child)
                self.build_minimax_tree_recursive(
                    child, 3-piece_type, depth_max, depth+1, True)
        '''
        if current_state.game_end(piece_type, "PASS"):
            print("my player passes\n")
            print("depth", depth, ", move", i,
                  j, "piece type", piece_type)
            root.score = self.evaluate(root, self.piece_type)
            print("evaluation ", root.score)
            return root
        '''


class RandomPlayer():
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''

        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MinimaxPlayer()
    player.piece_type = piece_type
    action = player.get_input(go, piece_type)
    writeOutput(action)
