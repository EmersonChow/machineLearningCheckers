from random import randint
from BoardClasses import Move
from BoardClasses import Board
from time import time

import math

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

#module load python/3.5.2
#We White
#python3 AI_Runner.py 7 7 2 l Sample_AIs/Average_AI/main.py ../src/checkers-python/main.py
#We Black
#python3 AI_Runner.py 7 7 2 l ../src/checkers-python/main.py Sample_AIs/Average_AI/main.py


#We White
#python3 AI_Runner.py 9 8 2 l Sample_AIs/Average_AI/main.py ../src/checkers-python/main.py
#We Black
#python3 AI_Runner.py 9 8 2 l ../src/checkers-python/main.py Sample_AIs/Average_AI/main.py

class Node():

    def __init__(self, move, parent, color):
        self.move = move
        self.next = []
        self.parent = parent
        self.color = color
        self.ucb = float("inf")
        self.wins = 0
        self.simCount = 0


class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.secondsLeft = 480


    def get_move(self,move):
        startTime = time()
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        if self.col > 7:
            if self.secondsLeft > 450:
                move = self.mcts(500)
            elif self.secondsLeft > 60:
                move = self.mcts(850)
            elif self.secondsLeft > 3:
                move = self.mcts(300)
            else:
                moves = self.board.get_all_possible_moves(self.color)
                index = randint(0, len(moves) - 1)
                inner_index = randint(0, len(moves[index]) - 1)
                move = moves[index][inner_index]

        else:
            if self.secondsLeft > 3:
                move = self.mcts(850)
            else:
                moves = self.board.get_all_possible_moves(self.color)
                index = randint(0, len(moves) - 1)
                inner_index = randint(0, len(moves[index]) - 1)
                move = moves[index][inner_index]


        self.board.make_move(move,self.color)
        endTime = time()
        self.secondsLeft -= endTime - startTime

        return move


    def selectionAlg(self, parentNode, cValue):     #parentNode = root = None, None, self.color

        maxUCB = float("-inf")
        maxNode = None
        currColor = parentNode.color       #root's color

        moveCount = 0
        done = False

        while not done:
            #get highest UCB value node to expand/follow
            for node in parentNode.next:
                if node.simCount > 0:
                    node.ucb = (node.wins / node.simCount) + (cValue * math.sqrt(math.log(node.parent.simCount) / node.simCount))
                if node.ucb > maxUCB:
                    maxNode = node
                    maxUCB = node.ucb

            #update board state, keep track of how many moves in order to undo later
            self.board.make_move(maxNode.move, currColor)
            moveCount += 1

            #swap colors
            currColor = self.opponent[currColor]



            #expand maxNode or go down tree
            if len(maxNode.next) == 0:
                for moves in self.board.get_all_possible_moves(currColor):
                    for move in moves:
                        maxNode.next.append(Node(move, maxNode, self.opponent[currColor]))

                done = True
            else:
                parentNode = maxNode
                maxUCB = float("-inf")
                currColor = parentNode.color
                maxNode = None

        return maxNode, moveCount


    def simulate(self, leafNode):
        movesMade = 0
        currColor = leafNode.color
        updateList = set()
        bottomNode = leafNode
        holdingList = []
        while bottomNode is not None:
            updateList.add(bottomNode)
            bottomNode = bottomNode.parent

        #if there's no winner here.
        if len(leafNode.next) > 0:
            #pick a random move

            leafNode = leafNode.next[randint(0, len(leafNode.next) - 1)]
            for node in updateList:
                for myMove in node.next:
                    if myMove.move == leafNode.move:
                        holdingList.append(myMove)
            for node in holdingList:
                updateList.add(node)
            holdingList = []

            self.board.make_move(leafNode.move, currColor)

            movesMade += 1

            # swap colors
            currColor = self.opponent[currColor]

            #randomly generate new moves until win
            while len(self.board.get_all_possible_moves(currColor)) > 0:
                moves = self.board.get_all_possible_moves(currColor)

                if len(moves) > 0:
                    index = randint(0, len(moves) - 1)
                    inner_index = randint(0, len(moves[index]) - 1)
                    move = moves[index][inner_index]

                    for node in updateList:
                        for myMove in node.next:
                            if myMove.move == move:
                                holdingList.append(myMove)
                    for node in holdingList:
                        updateList.add(node)
                    holdingList = []

                    self.board.make_move(move, currColor)
                    movesMade += 1
                    # swap colors
                    currColor = self.opponent[currColor]

        winner = self.board.is_win(self.opponent[currColor])

        for _ in range(movesMade):
            self.board.undo()

        return winner, updateList

    # def backpropagate(self, result, child):
    #     while child.parent is not None:
    #
    #         child.simCount += 1
    #
    #         # if draw or our color returned, we win
    #         if result == self.color:
    #             if child.color == self.opponent[self.color]:
    #                 child.wins += 1
    #         elif result == -1:
    #             if child.color == self.opponent[self.color]:
    #                 child.wins += 0.5
    #         else:
    #             child.wins -= 0.5
    #         child = child.parent
    #
    #     child.simCount += 1

    def backpropagateAMAF(self, result, updateList):
        for child in updateList:

            child.simCount += 1

            # if draw or our color returned, we win
            if result == self.color:
                if child.color == self.opponent[self.color]:
                    child.wins += 1
            elif result == -1:
                if child.color == self.opponent[self.color]:
                    child.wins += 0
            else:
                child.wins -= 0.5



    def mcts(self, simCount):



        moveset = self.board.get_all_possible_moves(self.color)

        if len(moveset) == 1:
            return moveset[0][0]


        root = Node(None, None, self.color)
        for moves in moveset:
            for move in moves:
                root.next.append(Node(move, root, self.opponent[self.color]))



        for _ in range(simCount):
            maxNode, undoCount = self.selectionAlg(root,math.sqrt(2))
            result, updateSet = self.simulate(maxNode)
            self.backpropagateAMAF(result, updateSet)
            for _ in range(undoCount):
                self.board.undo()


        ucbNumber = -1
        winNode = None

        for child in root.next:
            if child.simCount > 0:
                child.ucb = (child.wins / child.simCount) + (
                        math.sqrt(2) * math.sqrt(math.log(child.parent.simCount) / child.simCount))
            if child.ucb > ucbNumber:
                winNode = child
                ucbNumber = child.ucb

        if winNode == None:
            new_list = []
            for moves in self.board.get_all_possible_moves(self.color):
                for move in moves:
                    new_list.append(move)
            return new_list[0]
        return winNode.move

