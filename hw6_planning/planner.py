from constants import *
from utils import *
from core import *

import pdb
import copy
from functools import reduce

from statesactions import *

############################
## HELPERS

### Return true if the given state object is a goal. Goal is a State object too.
def is_goal(state, goal):
  return len(goal.propositions.difference(state.propositions)) == 0

### Return true if the given state is in a set of states.
def state_in_set(state, set_of_states):
  if len(set_of_states) == 0:
    return False
  for s in set_of_states:
    if s.propositions != state.propositions:
      return False
  return True

### For debugging, print each state in a list of states
def print_states(states):
  for s in states:
    ca = None
    if s.causing_action is not None:
      ca = s.causing_action.name
    print(s.id, s.propositions, ca, s.get_g(), s.get_h(), s.get_f())


############################
### Planner 
###
### The planner knows how to generate a plan using a-star and heuristic search planning.
### It also knows how to execute plans in a continuous, time environment.

class Planner():

  def __init__(self):
    self.running = False              # is the planner running?
    self.world = None                 # pointer back to the world
    self.the_plan = []                # the plan (when generated)
    self.initial_state = None         # Initial state (State object)
    self.goal_state = None            # Goal state (State object)
    self.actions = []                 # list of actions (Action objects)

  ### Start running
  def start(self):
    self.running = True
    
  ### Stop running
  def stop(self):
    self.running = False

  ### Called every tick. Executes the plan if there is one
  def update(self, delta = 0):
    result = False # default return value
    if self.running and len(self.the_plan) > 0:
      # I have a plan, so execute the first action in the plan
      self.the_plan[0].agent = self
      result = self.the_plan[0].execute(delta)
      if result == False:
        # action failed
        print("AGENT FAILED")
        self.the_plan = []
      elif result == True:
        # action succeeded
        done_action = self.the_plan.pop(0)
        print("ACTION", done_action.name, "SUCCEEDED")
        done_action.reset()
    # If the result is None, the action is still executing
    return result

  ### Call back from Action class. Pass through to world
  def check_preconditions(self, preconds):
    if self.world is not None:
      return self.world.check_preconditions(preconds)
    return False

  ### Call back from Action class. Pass through to world
  def get_x_y_for_label(self, label):
    if self.world is not None:
      return self.world.get_x_y_for_label(label)
    return None

  ### Call back from Action class. Pass through to world
  def trigger(self, action):
    if self.world is not None:
      return self.world.trigger(action)
    return False

  ### Generate a plan. Init and goal are State objects. Actions is a list of Action objects
  ### Return the plan and the closed list
  def astar(self, init, goal, actions):
      plan = []    # the final plan
      open = []    # the open list (priority queue) holding State objects
      closed = []  # the closed list (already visited states). Holds state objects
      ### YOUR CODE GOES HERE
      ### Create all the successor states based on the current available actions (available actions means actions of which all the prcondistions is met)
      ### Return all the new states
      def find_successor_states(current_state):
        # List to store the successor states
        successor_states = []
        # Loop through all the actions and find out the actions can be taken during current state. 
        for action in actions:
          # print(action.preconditions)
          # print(current_state.propositions)
          if action.preconditions.issubset(current_state.propositions):
            # If an action can be taken, create new state that can reach. 
            updated_propositions = (current_state.propositions-action.delete_list) | action.add_list
            new_state = State(updated_propositions)
            new_state.parent = current_state
            new_state.causing_action = action
            new_state.g = current_state.g + action.cost
            new_state.h = Planner.compute_heuristic(self, new_state, goal, actions)
            successor_states.append(new_state)
        return successor_states
      # Set current state to init
      current_state = init
      # Add current state to open list
      open.append(init)
      # Continue processing until it gets to the goal state
      while not is_goal(current_state, goal):
          # print(current_state.id)
          # if open is empty but goaal has not been reached, then return None (can't get to the goal)
          if len(open) == 0:
            return None
          # Find all the successor states based on the current state
          successor_states = find_successor_states(current_state)
          # print(len(successor_states))
          # if current state has successor states, check if the successor states need to be added to the open list or need to be updated
          if len(successor_states) != 0:
            for s in successor_states:
              # print(len(closed))
              if state_in_set(s, set(closed)):
                # print("close")
                continue
              if state_in_set(s, set(open)):
                for open_state in open:
                  if s.propositions == open_state.propositions:
                    if s.get_f() < open_state.get_f():
                      open_state.h = s.h
                      open_state.g = s.g
                      open_state.parent = s.parent
              else:
                open.append(s)
          # Add current state to the closed list
          closed.append(current_state)
          # Remove the current state from the open list
          for open_state in open:
              print(open_state.id)
              if current_state.propositions == open_state.propositions:
                # print(open_state.id)
                open.remove(open_state)
                break
          # Sort the open list based on the heuristic value and set current state to the state with smallest heuristic value
          open.sort(key=lambda state: state.h+state.g)
          current_state = open[0]
      # Construct the plan
      while current_state.propositions != init.propositions:
        plan.append(current_state.causing_action)
        current_state = current_state.parent
      plan.reverse()


      ### CODE ABOVE
      return plan, closed

  ### Compute the heuristic value of the current state using the HSP technique.
  ### Current_state and goal_state are State objects.
  def compute_heuristic(self, current_state, goal_state, actions):
    actions = copy.deepcopy(actions)  # Make a deep copy just in case
    h = 0                             # heuristic value to return
    ### YOUR CODE BELOW
    # Create dummy goal and dummy current
    dummy_goal = Action("dummy_goal", goal_state.propositions, [], [], 0)
    dummy_current = Action("dummy_current", [], current_state.propositions, [], 0)
    # Add dummy goal and dummy current to the actions list
    actions.append(dummy_goal)
    actions.append(dummy_current)
    # Create a graph dictionary
    graph = {}
    # Create a "subdictionary" for each action
    for action in actions:
      graph [action.name] = {"predecessor" : [], "out" : [], "in":[], "dist":0}
    # Create the graph
    for a1 in actions:
      for a2 in actions:
        if a1.name != a2.name:
          intersection = a1.add_list.intersection(a2.preconditions)
          for element in intersection:
            graph[a1.name]["out"].append((element, a2))
            graph[a2.name]["predecessor"].append(a1)
            graph[a2.name]["in"].append((element, a1))
    # Add dummy current to the queue
    queue = []
    queue.append(dummy_current)
    # store the node being visited
    visited = []
    # while queue is not empty
    while queue:
      # set the current action be the first element in the queue
      current_action = queue.pop(0)
      # set current action visited
      visited.append(current_action.name)
      # Find successor of current node
      for proposition, successor in graph[current_action.name]["out"]:
        if successor.name not in visited:
          # all_predecessors_visited = True
          # for e in graph[successor.name]["predecessor"]:
          #   if e.name not in visited:
          #     all_predecessors_visited = False
          #     break   
          # if all_predecessors_visited:
          #   queue.append(successor)
          temp_propositions = []
          all_proposition = []
          # Add the available actions to the queue
          for e, a in graph[successor.name]["in"]:
            all_proposition.append(e)
            if a.name in visited:
              temp_propositions.append(e)
          if set(temp_propositions) == successor.preconditions:
            queue.append(successor)
        # compute the distance from dummy current
        new_dist = graph[current_action.name]["dist"] + successor.cost
        if new_dist > graph[successor.name]["dist"]:
          graph[successor.name]["dist"] = new_dist
    # heuristic value is the distance from the dummy current to the dummy goal     
    h = graph["dummy_goal"]["dist"]
    

    ### YOUR CODE ABOVE
    return h

