import sys
import queue
sys.path.append('.')
sys.path.append('..')

from wumpus.Agent import Agent

class SearchAI ( Agent ):

    def __init__(self, board):

        self.__currentIndex = 0
        self.__plan = []

        self.__plan

        print(self.action_list(self.best_first_search_grab(board)))

        allMoves = self.action_list(self.best_first_search_grab(board))
        # possible actions: "move forward","climb","turn right","turn left","shoot","grab"
        if not allMoves:
            print("Goal is not reachable.")
        else:
            for i in range(len(allMoves)):
                if(allMoves[i] == "move forward"):
                    self.__plan.append(Agent.Action.FORWARD)
                elif(allMoves[i] == "climb"):
                    self.__plan.append(Agent.Action.CLIMB)
                elif(allMoves[i] == "turn right"):
                    self.__plan.append(Agent.Action.TURN_RIGHT)
                elif(allMoves[i] == "turn left"):
                    self.__plan.append(Agent.Action.TURN_LEFT)
                elif(allMoves[i] == "shoot"):
                    self.__plan.append(Agent.Action.SHOOT)
                elif(allMoves[i] == "grab"):
                    self.__plan.append(Agent.Action.GRAB)




    class Node():
        def __init__(self,state,parent,action,cost):
            self.state = state
            self.parent = parent
            self.action = action
            self.cost = cost


    def getAction ( self, stench, breeze, glitter, bump, scream):
        self.__currentIndex += 1
        if self.__plan:
            return self.__plan[self.__currentIndex - 1]
        else:
            return

    def get_Wumpus(self,board):
        board_size = (len(board),len(board[0]))
        for r in range (board_size[0]):
            for c in range (board_size[1]):
                if board[r][c].wumpus:
                    return (c,r)

    def get_Pits(self,board):
        pits = []
        board_size = (len(board),len(board[0]))
        for r in range (board_size[0]):
            for c in range (board_size[1]):
                if board[r][c].pit:
                    pits.append((c,r))
        return pits

    def get_money(self,board):
        board_size = (len(board),len(board[0]))
        for r in range (board_size[0]):
            for c in range (board_size[1]):
                if board[r][c].gold:
                    return (c,r)


    def action_availability_dict(self,board):
        board_size = (len(board),len(board[0]))
        wumpus_pos = self.get_Wumpus(board)
        pits = self.get_Pits(board)
        money = self.get_money(board)
        action_set = {}
        # possible actions: "move forward","climb","turn right","turn left","shoot","grab"
        for r in range (board_size[0]):
            for c in range (board_size[1]):
                if (c,r) in pits: #we did not include the wumpus because we can kill him
                    continue
                key_set = []
                for d in range(4):
                    key_set.append((c,r,d))
                for state in key_set:
                    action_set[state] = []
                    if ((state[0],state[1])==(0,0)):
                        action_set[state].append("climb")
                    action_set[state].append("turn right")
                    action_set[state].append("turn left")
                    action_set[state].append("shoot")
                    if ((state[0],state[1])==money):
                        action_set[state].append("grab")
                    if state[2] == 0:
                        if not ((state[0],state[1]+1) == wumpus_pos or (state[0],state[1]+1) in pits or state[1]+1>=board_size[1]):
                            action_set[state].append("move forward")
                    elif state[2] == 1:
                        if not ((state[0]-1,state[1]) == wumpus_pos or (state[0]-1,state[1]) in pits or state[0]-1<=board_size[0]):
                            action_set[state].append("move forward")
                    elif state[2] == 2:
                        if not ((state[0],state[1]-1) == wumpus_pos or (state[0],state[1]-1) in pits or state[1]-1<=board_size[1]):
                            action_set[state].append("move forward")
                    else:
                        if not ((state[0]+1,state[1]) == wumpus_pos or (state[0]+1,state[1]) in pits or state[0]+1>=board_size[0]):
                            action_set[state].append("move forward")

        # print(action_set)
        # new_action_set = {}
        # for key in action_set:
        #     new_action_set[key]=[]
        #     for value in action_set[key]:
        #         new_action_set[key].append(self.transition_function(value,key,wumpus_pos,True,False,False,False))
        # print(new_action_set)


    def best_first_search_grab(self,board):
        initial_state = ((0,0,0),True,False,False,False) # position, direction, wumpus_alive, arrow_thrown, gold_collected, goal_reached
        node = self.Node(initial_state,None,None,0) # state, parent, action, cost
        to_check = queue.Queue() # frontier
        to_check.put(node)
        reached = {}
        reached[initial_state] = node
        boo = True
        while (not to_check.empty()):
            node = to_check.get()
            if node.state[-1] and node.state[-2]: # gold collected and climbed out
                print("success")
                return node
            if node.state[-2] and boo:
                while not to_check.empty():
                    to_check.get()
                reached.clear()
                reached[node.state]=node
                boo = False
            children = self.expand(board,node)
            for child in children:
                s = child.state
                if (s not in reached):

                    reached[s] = child
                    to_check.put(child)
                elif (child.cost>=reached[s].cost):
                    reached[s] = child
                    to_check.put(child)
                else:
                    if (s in reached and s[-2]):
                        #print("", end=".")
                        print("", end="")

        return None


    def expand(self,board,node):
        actions = self.get_actions(board,node.state)
        children = []
        for action in actions:
            new_state = self.transition_function(action,board,node.state)
            children.append(self.Node(new_state,node,action,node.cost+self.get_cost(action,new_state)))
        return children

    def action_list(self,node):
        temp = node
        action_list = []
        while (temp!=None):
            action_list.append(temp.action)
            #print(action_list)
            temp = temp.parent
        action_list.reverse()
        return action_list[1:]


    def get_cost(self,action,state):
        if (action=="throw" and not state[2]):
            return -11
        else:
            return -1

    def transition_function(self,action,board,state):
        key = state[0]
        x_new = key[0]
        y_new = key[1]
        d = key[2]
        wumpus_pos=self.get_Wumpus(board)
        wumpus_life = state[1]
        arrow_thrown = state[2]
        gold_collected=state[3]
        goal_state = state[4]
        if (action == "move forward"):
            if (d == 0):
                y_new = key[1]+1
            elif (d==1):
                x_new-=1
            elif (d==2):
                y_new-=1
            else:
                x_new+=1
        elif (action == "shoot"):
            if not (arrow_thrown):
                arrow_thrown = True
                if (wumpus_life):
                    if (d==0):
                        if (wumpus_pos[0]==x_new and wumpus_pos[1]>y_new):
                            wumpus_life = False
                    elif (d==1):
                        if (wumpus_pos[0]<x_new and wumpus_pos[1]==y_new):
                            wumpus_life = False
                    elif (d==2):
                        if (wumpus_pos[0]==x_new and wumpus_pos[1]<y_new):
                            wumpus_life = False
                    else:
                        if (wumpus_pos[0]>x_new and wumpus_pos[1]==y_new):
                            wumpus_life = False
        elif (action=="turn right"):
            d+=1
            if (d>3):
                d=0
        elif (action=="turn left"):
            d-=1
            if (d<0):
                d=3
        elif (action=="grab" and not(gold_collected)):
            gold_collected=True
        elif (action=="climb" and gold_collected):
            goal_state=True
        return ((x_new,y_new,d),wumpus_life,arrow_thrown,gold_collected,goal_state)


    def get_actions(self,board,state):
        board_size = (len(board),len(board[0]))
        wumpus_pos = self.get_Wumpus(board)
        pits = self.get_Pits(board)
        money = self.get_money(board)
        action_set = []
        agent_pos = (state[0][0],state[0][1])
        d = state[0][-1]
        if ((state[0][0],state[0][1])==(0,0) and state[-2]):
            action_set.append("climb")
            return action_set
        if ((state[0][0],state[0][1])==money and not state[-2]):
            action_set.append("grab")
            return action_set
        if state[0][2] == 0:
            if not state[1]: #if wumpus is dead dont check wumpus pos
                if not ((state[0][0],state[0][1]+1) in pits or state[0][1]+1>=board_size[1]):
                    action_set.append("move forward")
            else:
                if not ((state[0][0],state[0][1]+1) == wumpus_pos or (state[0][0],state[0][1]+1) in pits or state[0][1]+1>=board_size[1]):
                    action_set.append("move forward")
        if state[0][2] == 1:
            if not state[1]: #if wumpus is dead dont check wumpus pos
                if not ((state[0][0]-1,state[0][1]) in pits or state[0][0]-1<0):
                    action_set.append("move forward")
            else:
                if not ((state[0][0]-1,state[0][1]) == wumpus_pos or (state[0][0]-1,state[0][1]) in pits or state[0][0]-1<0):
                    action_set.append("move forward")
        if state[0][2] == 2:
            if not state[1]: #if wumpus is dead dont check wumpus pos
                if not ((state[0][0],state[0][1]-1) in pits or state[0][1]-1<0):
                    action_set.append("move forward")
            else:
                if not ((state[0][0],state[0][1]-1) == wumpus_pos or (state[0][0],state[0][1]-1) in pits or state[0][1]-1<0):
                    action_set.append("move forward")
        if state[0][2] == 3:
            if not state[1]: #if wumpus is dead dont check wumpus pos
                if not ((state[0][0]+1,state[0][1]) in pits or state[0][0]+1>=board_size[0]):
                    action_set.append("move forward")
            else:
                if not ((state[0][0]+1,state[0][1]) == wumpus_pos or (state[0][0]+1,state[0][1]) in pits or state[0][0]+1>=board_size[0]):
                    action_set.append("move forward")
        action_set.append("turn right")
        action_set.append("turn left")
        if (not state[2]):
            action_set.append("shoot")
        return action_set