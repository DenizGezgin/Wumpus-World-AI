# ======================================================================
# FILE:        MyAI.py
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from wumpus.Agent import Agent
from z3 import *
from itertools import combinations
import sys
import queue

sys.path.append('.')
sys.path.append('..')


class MyAI():

    def __init__(self):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        self.world_size = [8, 8]

        self.__wumpus = {(i, j): Bool('wumpus x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                         range(self.world_size[1])}
        self.__agent_position_history = [(0, 0)]
        self.__pits = {(i, j): Bool('pit x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                       range(self.world_size[1])}
        self.__ok = {(i, j): Bool('ok x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                     range(self.world_size[1])}
        self.__breeze = {(i, j): Bool('breeze x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                         range(self.world_size[1])}
        self.__stench = {(i, j): Bool('stench x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                         range(self.world_size[1])}
        self.__bump = {(i, j): Bool('bump x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                       range(self.world_size[1])}
        self.__glitter = {(i, j): Bool('glitter x_%s_%s' % (i, j)) for i in range(self.world_size[0]) for j in
                          range(self.world_size[1])}
        self.__scream = Bool('scream')
        self.has_arrow = True
        self.has_gold = False
        self.wumpus_alive = True
        self.__kb = Solver()
        self.__kb.add(Not(self.__pits[(0, 0)]), Not(self.__wumpus[(0, 0)]))
        self.plan = []
        self.safe_squares = [(0, 0)]
        self.current = (0, 0, 0)

        for i in range(self.world_size[0]):
            for j in range(self.world_size[1]):
                if (i, j) == (0, 0):
                    a = self.__breeze[i, j]
                    b = Or(self.__pits[(i + 1, j)], self.__pits[(i, j + 1)])
                    self.__kb.add(Implies(a, b))
                    self.__kb.add(Implies(b, a))
                    c = And(self.__stench[i, j], self.wumpus_alive)
                    d = Or(self.__wumpus[(i + 1, j)], self.__wumpus[(i, j + 1)])
                    self.__kb.add(Implies(c, d))
                    self.__kb.add(Implies(d, c))
                elif i == self.world_size[0] - 1 and j == self.world_size[1] - 1:
                    a = self.__breeze[i, j]
                    b = Or(self.__pits[(i - 1, j)], self.__pits[(i, j - 1)])
                    self.__kb.add(Implies(a, b))
                    self.__kb.add(Implies(b, a))
                    c = And(self.__stench[i, j], self.wumpus_alive)
                    d = Or(self.__wumpus[(i - 1, j)], self.__wumpus[(i, j - 1)])
                    self.__kb.add(Implies(c, d))
                    self.__kb.add(Implies(d, c))
                elif i == 0 and j != self.world_size[1] - 1:
                    a = self.__breeze[i, j]
                    b = Or(self.__pits[(i, j - 1)], self.__pits[(i + 1, j)], self.__pits[(i, j + 1)])
                    self.__kb.add(Implies(a, b))
                    self.__kb.add(Implies(b, a))
                    c = And(self.__stench[i, j], self.wumpus_alive)
                    d = Or(self.__wumpus[(i, j - 1)], self.__wumpus[(i + 1, j)], self.__wumpus[(i, j + 1)])
                    self.__kb.add(Implies(c, d))
                    self.__kb.add(Implies(d, c))
                elif i == 0 and j == self.world_size[1] - 1:
                    a = self.__breeze[i, j]
                    b = Or(self.__pits[(i, j - 1)], self.__pits[(i + 1, j)])
                    self.__kb.add(Implies(a, b))
                    self.__kb.add(Implies(b, a))
                    c = And(self.__stench[i, j], self.wumpus_alive)
                    d = Or(self.__wumpus[(i, j - 1)], self.__wumpus[(i + 1, j)])
                    self.__kb.add(Implies(c, d))
                    self.__kb.add(Implies(d, c))
                elif i == self.world_size[0] - 1 and j != 0:
                    a = self.__breeze[i, j]
                    b = Or(self.__pits[(i, j - 1)], self.__pits[(i - 1, j)], self.__pits[(i, j + 1)])
                    self.__kb.add(Implies(a, b))
                    self.__kb.add(Implies(b, a))
                    c = And(self.__stench[i, j], self.wumpus_alive)
                    d = Or(self.__wumpus[(i, j - 1)], self.__wumpus[(i - 1, j)], self.__wumpus[(i, j + 1)])
                    self.__kb.add(Implies(c, d))
                    self.__kb.add(Implies(d, c))
                elif i == self.world_size[0] - 1 and j == 0:
                    a = self.__breeze[i, j]
                    b = Or(self.__pits[(i - 1, j)], self.__pits[(i, j + 1)])
                    self.__kb.add(Implies(a, b))
                    self.__kb.add(Implies(b, a))
                    c = And(self.__stench[i, j], self.wumpus_alive)
                    d = Or(self.__wumpus[(i - 1, j)], self.__wumpus[(i, j + 1)])
                    self.__kb.add(Implies(c, d))
                    self.__kb.add(Implies(d, c))
                else:
                    if j == 0:
                        a = self.__breeze[i, j]
                        b = Or(self.__pits[(i - 1, j)], self.__pits[(i, j + 1)], self.__pits[(i + 1, j)])
                        self.__kb.add(Implies(a, b))
                        self.__kb.add(Implies(b, a))
                        c = And(self.__stench[i, j], self.wumpus_alive)
                        d = Or(self.__wumpus[(i - 1, j)], self.__wumpus[(i, j + 1)], self.__wumpus[(i + 1, j)])
                        self.__kb.add(Implies(c, d))
                        self.__kb.add(Implies(d, c))
                    elif j == self.world_size[1] - 1:
                        a = self.__breeze[i, j]
                        b = Or(self.__pits[(i, j - 1)], self.__pits[(i - 1, j)], self.__pits[(i + 1, j)])
                        self.__kb.add(Implies(a, b))
                        self.__kb.add(Implies(b, a))
                        c = And(self.__stench[i, j], self.wumpus_alive)
                        d = Or(self.__wumpus[(i, j - 1)], self.__wumpus[(i - 1, j)], self.__wumpus[(i + 1, j)])
                        self.__kb.add(Implies(c, d))
                        self.__kb.add(Implies(d, c))
                    else:
                        a = self.__breeze[i, j]
                        b = Or(self.__pits[(i, j - 1)], self.__pits[(i - 1, j)], self.__pits[(i, j + 1)],
                               self.__pits[(i + 1, j)])
                        self.__kb.add(Implies(a, b))
                        self.__kb.add(Implies(b, a))
                        c = And(self.__stench[i, j], self.wumpus_alive)
                        d = Or(self.__wumpus[(i, j - 1)], self.__wumpus[(i - 1, j)], self.__wumpus[(i, j + 1)],
                               self.__wumpus[(i + 1, j)])
                        self.__kb.add(Implies(c, d))
                        self.__kb.add(Implies(d, c))

                a = self.__ok[(i, j)]
                b = And(Not(self.__wumpus[(i, j)]), Not(self.__pits[(i, j)]))
                self.__kb.add(Implies(a, b))
                self.__kb.add(Implies(b, a))

        pairs = [(i, j) for i in range(self.world_size[0]) for j in range(self.world_size[1])]
        at_least_one_wumpus = [self.__wumpus[(i, j)] for i in range(self.world_size[0]) for j in
                               range(self.world_size[1])]
        at_most_one_wumpus = [And(Or(Not(self.__wumpus[pair_1]), Not(self.__wumpus[pair_2]))) for (pair_1, pair_2) in
                              set(combinations(pairs, r=2))]
        self.__kb.add(at_most_one_wumpus)
        self.__kb.add(Or(at_least_one_wumpus))

        pass
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    class Node():
        def __init__(self, state, parent, action, cost):
            self.state = state
            self.parent = parent
            self.action = action
            self.cost = cost

    def string_to_action(self, action):
        if action == "":
            print("Goal is not reachable.")
            return None
        else:
            if action == "move forward":
                return Agent.Action.FORWARD
            elif action == "climb":
                return Agent.Action.CLIMB
            elif action == "turn right":
                return Agent.Action.TURN_RIGHT
            elif action == "turn left":
                return Agent.Action.TURN_LEFT
            elif action == "shoot":
                return Agent.Action.SHOOT
            elif action == "grab":
                return Agent.Action.GRAB

    def plan_route(self, current, goals, allowed):
        current = self.current
        node = self.Node(current, None, None, 0)  # state, parent, action, cost
        to_check = queue.Queue()  # frontier
        to_check.put(node)
        reached = {current: node}
        boo = True
        while not to_check.empty():
            node = to_check.get()
            if (node.state[0], node.state[1]) in goals:
                return node
            children = self.expand_visit(node, goals + allowed)
            for child in children:
                s = child.state
                if s not in reached:
                    reached[s] = child
                    to_check.put(child)
                elif child.cost >= reached[s].cost:
                    reached[s] = child
                    to_check.put(child)
        return None

    def expand_visit(self, node, allowed):
        actions = self.get_actions(node.state, allowed)
        children = []
        for action in actions:
            new_state = self.transition_function(action, node.state)
            children.append(self.Node(new_state, node, action, node.cost + self.get_cost(action)))
        return children

    def get_actions(self, state, allowed):
        agent_pos = (state[0], state[1])
        d = state[-1]
        action_set = []
        if state[2] == 0:
            if (state[0], state[1] + 1) in allowed:
                action_set.append("move forward")
        if state[2] == 1:
            if (state[0] - 1, state[1]) in allowed:
                action_set.append("move forward")
        if state[2] == 2:
            if (state[0], state[1] - 1) in allowed:
                action_set.append("move forward")
        if state[2] == 3:
            if (state[0] + 1, state[1]) in allowed:
                action_set.append("move forward")
        action_set.append("turn right")
        action_set.append("turn left")
        return action_set

    def transition_function(self, action, state):
        key = state
        x_new = key[0]
        y_new = key[1]
        d = key[2]
        if action == "move forward":
            if d == 0:
                y_new = key[1] + 1
            elif d == 1:
                x_new -= 1
            elif d == 2:
                y_new -= 1
            else:
                x_new += 1
        elif action == "turn right":
            d += 1
            if d > 3:
                d = 0
        elif action == "turn left":
            d -= 1
            if d < 0:
                d = 3
        return x_new, y_new, d

    def get_cost(self, action):
        if action == "throw" and self.has_arrow:
            return -11
        else:
            return -1

    def getAction(self, stench, breeze, glitter, bump, scream):
        #i = input()
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================

        # Tell procedure
        plan = []
        position = self.__agent_position_history[-1]
        pairs = [(i, j) for i in range(self.world_size[0]) for j in range(self.world_size[1])]
        self.__pits[position] = False
        self.__wumpus[position] = False
        if stench:
            self.__kb.add(self.__stench[position])
            # self.push()
        else:
            self.__kb.add(Not(self.__stench[position]))
        if breeze:
            self.__kb.add(self.__breeze[position])
        else:
            self.__kb.add(Not(self.__breeze[position]))
        self.__glitter[position] = glitter
        # self.__kb.add(self.__glitter[(position)])
        self.__bump[position] = bump
        # self.__kb.add(self.__bump[(position)])
        self.__scream = scream
        # ask procedure -> safe squares
        self.safe_squares += (self.ask_procedure("squares"))
        # Grab the gold
        if glitter and not self.has_gold:
            # print("glitter part")
            self.plan += ["grab"] + self.action_list(self.plan_route(self.current, [(0, 0)], self.safe_squares)) + [
                "climb"]
            self.has_gold = True
            action = "grab"
            self.current = self.transition_function(action, self.current)
            return self.string_to_action(action)
        if scream:
            # print("Wumpus dead")
            for i in range(self.world_size[0]):
                for j in range(self.world_size[1]):
                    self.__wumpus[(i, j)] = False
            self.wumpus_alive = False
        if bump:
            # print(f"Current position {self.current} at bump")
            if self.current[2] == 0:  # right
                self.current = (self.current[0], self.current[1] - 1, self.current[2])
                self.world_size[1] = self.current[1]
                for i in range(self.world_size[0]):
                    self.__kb.add(Not(self.__ok[(i, self.current[1] + 1)]))
            elif self.current[2] == 3:  # up
                self.current = (self.current[0] - 1, self.current[1], self.current[2])
                self.world_size[0] = self.current[0]
                for j in range(self.world_size[1]):
                    self.__kb.add(Not(self.__ok[(self.current[0] + 1, j)]))
        if plan == [] and self.has_gold == False:
            # print("checking unvisited safe squares")
            # listing the unvisited squares
            unvisited = []
            for elem in pairs:
                if elem not in self.__agent_position_history:
                    unvisited.append(elem)
            # unvisited INTERSECT safe_squares
            unvisited_safe = [square for square in unvisited if square in self.safe_squares]
            # print("unvisited safe squares")
            # print(unvisited_safe)
            plan += self.action_list(self.plan_route(self.current, unvisited_safe, self.safe_squares))
            # print(plan)
        if plan == [] and self.has_arrow and self.has_gold == False:
            # print("wumpus part")
            possible_squares = self.ask_procedure("wumpus")
            plan = self.plan_shot(self.current, possible_squares, self.safe_squares)
        if plan == [] and self.has_gold == False:
            # print("unsafe visit")
            not_unsafe = (self.ask_procedure("not unsafe squares"))
            unvisited = []
            for elem in pairs:
                if elem not in self.__agent_position_history:
                    unvisited.append(elem)
            unvisited_safe = [square for square in not_unsafe if square in unvisited]
            plan = self.action_list(self.plan_route(self.current, unvisited_safe, self.safe_squares))
        if plan == []:
            # print("go back")
            plan = self.action_list(self.plan_route(self.current, [(0, 0)], self.safe_squares))
            plan.append("climb")
        action = plan[0]
        if action == "shoot":
            self.has_arrow = False
        # print(action)
        self.current = self.transition_function(action, self.current)
        self.__agent_position_history.append((self.current[0], self.current[1]))
        # print("new agent position:", self.current)
        # print(self.__kb)
        return self.string_to_action(action)

        # return Agent.Action.FORWARD
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================

    def ask_procedure(self, task):
        position = self.__agent_position_history[-1]
        pairs = [(i, j) for i in range(self.world_size[0]) for j in range(self.world_size[1])]

        if task == "squares":
            safe = []
            # Checking if the 4 adjacent squares are safe
            potential_squares = [(position[0] - 1, position[1]), (position[0], position[1] - 1),
                                 (position[0] + 1, position[1]), (position[0], position[1] + 1)]
            for (a, b) in potential_squares:
                if (a, b) in pairs:
                    self.__kb.push()
                    self.__kb.add(Not(self.__ok[(a, b)]))
                    if not (self.__kb.check() == sat):
                        safe.append((a, b))
                    self.__kb.pop()

            return safe
        elif task == "wumpus":
            possible_wumpus = []
            for (a, b) in pairs:

                self.__kb.push()
                self.__kb.add(self.__wumpus[(a, b)])
                if self.__kb.check() == sat:
                    # print("wumpus ca marche")
                    possible_wumpus.append((a, b))
                # print(possible_wumpus)
                self.__kb.pop()
            return possible_wumpus
        elif task == "not unsafe squares":
            not_unsafe = []
            for (a, b) in pairs:
                self.__kb.push()
                self.__kb.add(self.__ok[(a, b)])
                if self.__kb.check() == sat:
                    not_unsafe.append((a, b))
                self.__kb.pop()
            return not_unsafe

    def plan_shot(self, current, possible_wumpus, allowed):
        # we choose the first location where the wumpus can be
        wumpus_random = possible_wumpus[0]
        cost = 20000
        temp = None
        # we check if we can go to one of the adjacent squares of this location
        # we pick the cheapest way to go to the wumpus
        possible_plans = []
        if (wumpus_random[0], wumpus_random[1] + 1) in self.safe_squares:
            possible_plans.append(self.plan_route(current, [(wumpus_random[0], wumpus_random[1] + 1)], allowed))
        if (wumpus_random[0] + 1, wumpus_random[1]) in self.safe_squares:
            possible_plans.append(self.plan_route(current, [(wumpus_random[0] + 1, wumpus_random[1])], allowed))
        if (wumpus_random[0] - 1, wumpus_random[1]) in self.safe_squares:
            possible_plans.append(self.plan_route(current, [(wumpus_random[0] - 1, wumpus_random[1])], allowed))
        if (wumpus_random[0], wumpus_random[1] - 1) in self.safe_squares:
            possible_plans.append(self.plan_route(current, [(wumpus_random[0], wumpus_random[1] - 1)], allowed))
        # picking the cheapest way to the wumpus
        for node in possible_plans:
            if node:
                if node.cost < cost:
                    temp = node
                    cost = node.cost
        if not temp:
            return []
        else:
            plan = self.action_list(temp) + ["shoot"]
            return plan

    def action_list(self, node):
        temp = node
        action_list = []
        while temp != None:
            action_list.append(temp.action)
            # print(action_list)
            temp = temp.parent
        action_list.reverse()
        return action_list[1:]

    def pit(self, x, y):
        if (x, y) in self.__pits.keys():
            return True
        else:
            return False

    def breeze(self, x, y):
        if (x, y) in self.__breeze.keys():
            return True
        else:
            return False

    def wumpus(self, x, y):
        if (x, y) in self.__wumpus.keys():
            return True
        else:
            return False

    def stench(self, x, y):
        if (x, y) in self.__stench.keys():
            return True
        else:
            return False

    def glitter(self, x, y):
        if (x, y) in self.__glitter.keys():
            return True
        else:
            return False

    def bump(self, x, y):
        if (x, y) in self.__bump.keys():
            return True
        else:
            return False

    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================
