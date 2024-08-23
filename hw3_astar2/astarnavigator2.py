'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *



###############################
### AStarNavigator2
###
### Creates a path node network and implements the A* algorithm to create a path to the given destination.
			
class AStarNavigator2(PathNetworkNavigator):

				
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., its current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		self.setPath(None)
		### Make sure the next and dist matrices exist
		if self.agent != None and self.world != None:
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			### Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			### Tell the agent to move to dest
			if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				### Step 2: If there is an obstacle, create the path that will move around the obstacles.
				### Find the path nodes closest to source and destination.
				start = getOnPathNetwork(source, self.pathnodes, self.world.getLinesWithoutBorders(), self.agent)
				end = getOnPathNetwork(dest, self.pathnodes, self.world.getLinesWithoutBorders(), self.agent)
				if start != None and end != None:
					### Remove edges from the path network that intersect gates
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates(), self.world)
					closedlist = []
					### Create the path by traversing the pathnode network until the path node closest to the destination is reached
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						### Determine whether shortcuts are available
						path = shortcutPath(source, dest, path, self.world, self.agent)
						### Store the path by calling self.setPath()
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							### Tell the agent to move to the first node in the path (and pop the first node off the path)
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


### Removes any edge in the path network that intersects a worldLine (which should include gates).
def unobstructedNetwork(network, worldLines, world):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork



### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
    ### YOUR CODE GOES BELOW HERE ###
	if rayTraceWorld (p1, p2, worldLines) is None:
		return True
    ### YOUR CODE GOES ABOVE HERE ###
	return False

### Given a location, find the closest pathnode that the agent can get to without collision
### agent: the agent
### location: the location to check from (typically where the agent is starting from or where the agent wants to go to) as an (x, y) point
### pathnodes: a list of pathnodes, where each pathnode is an (x, y) point
### world: pointer to the world
def getOnPathNetwork(location, pathnodes, worldLines, agent):
	node = None
	### YOUR CODE GOES BELOW HERE ###
	# get all available nodes that the agent could get on
	available_nodes = []
	for n in pathnodes:
		if rayTraceWorld (n, location, worldLines) == None:
			available_nodes.append(n)
	# choose the nearest node to get on
	if len(available_nodes) > 0:
		node = min(available_nodes, key=lambda n: distance(n, location))		
	### YOUR CODE GOES ABOVE HERE ###
	return node



### Implement the a-star algorithm
### Given:
### Init: a pathnode (x, y) that is part of the pathnode network
### goal: a pathnode (x, y) that is part of the pathnode network
### network: the pathnode network
### Return two values: 
### 1. the path, which is a list of states that are connected in the path network
### 2. the closed list, the list of pathnodes visited during the search process
def astar(init, goal, network):
	path = []
	open = []
	closed = []
	### YOUR CODE GOES BELOW HERE ###
	# Node class including necessary attributes: g_value, h_value, f, parent, and position
	class Node:
		def __init__(self, position, parent=None, g=0, h=0):
			self.position = position
			self.parent = parent
			self.g = g
			self.h = h
			self.f = g + h
	# heuristic function by directly calculate the straight line distance
	def heuristic(node: Node):
		return distance(node.position, goal)
	# Find all the successors of a node
	def find_successors(node: Node):
		successors = []
		for edge in network:
			if node.position in edge:
				for p in edge:
					# dont have to consider itself
					if p != node.position:
						if node.parent == None:
							successors.append(Node(p, node, node.g + distance(node.position, p), heuristic(node)))
						else:
							# dont have to consider the parent node
							if p != node.parent.position:
								successors.append(Node(p, node, node.g + distance(node.position, p), heuristic(node)))
		return successors
	# set the initial state for astar search				 
	current = Node(init, h=distance(init, goal))
	open.append(current)
	while current.position != goal:
		if len(open) == 0:
			return None
		# find all the successors
		current_successors = find_successors(current)
		# iterate through successors
		if len(current_successors) != 0:
			for s in current_successors:
				# if already visited, ignore
				if s.position in closed:
					continue
				# if in open list, check g value, update if g value is smaller
				updated = False
				for op in open:
					if op.position == s.position:
						if op.f > s.f: ################################
							op.parent = s.parent
							op.g = s.g
							op.f = s.g+s.h
							continue
						updated = True
				# if not visited and no update happened, add successor to open
				if not updated:
					open.append(s)
		# add current to closed list
		if current.position not in closed:
			closed.append(current.position)
		# remove current from open list
		open.remove(current)
		if len(open) != 0:
			current = min(open, key=lambda node: node.f)
	# construct the path
	while current != None:
		path.append(current.position)
		current = current.parent
	path.reverse()

	### YOUR CODE GOES ABOVE HERE ###
	return path, closed




def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return None




def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return None


### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the A* algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
	path = copy.deepcopy(path)
	### YOUR CODE GOES BELOW HERE ###
	# find the farthest node that the source can directly go
	start = path[0]
	end = path[len(path)-1]
	if rayTraceWorld(source, dest, world.getLines()) == None:
		return [source, dest]
	
	index_s = 0
	farthest_index = 0

	for i, node in enumerate(path):
		if rayTraceWorld(source, node, world.getLines()) is None:
			farthest_index = i

	while index_s < farthest_index:
		path.pop(0)
		index_s = index_s + 1  
			
    # loop through all the nodes to eliminate nodes in between two nodes that can be directly access
	i = 0
	while i < len(path) - 2:
		j = len(path) - 1
		while j > i:
			if rayTraceWorld(path[i], path[j], world.getLines()) == None:
				for node in path[i+1:j]:
					path.remove(node)
				break
			j = j - 1
		i = i + 1
	# find the farthest node that destination can directly go
	index_d = len(path) - 1  
	farthest_index_d = len(path) - 1  
	for i in range(len(path) - 1, 0, -1):
		if rayTraceWorld(dest, path[i], world.getLines()) is None:
			farthest_index_d = i
	while index_d > farthest_index_d:
		path.pop(index_d)
		index_d = index_d - 1

	### YOUR CODE GOES BELOW HERE ###
	return path


### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
	### YOUR CODE GOES BELOW HERE ###
	# empty the path when agent is able to go to destination directly
	if rayTraceWorld(nav.agent.position, nav.destination, nav.world.getLines()) == None:
		nav.agent.moveToTarget(nav.destination)
		nav.path = []
		return True
	else:
		if len(nav.path) > 0:
			index_s = 0
			farthest_index = 0
			for i, node in enumerate(nav.path):
				if rayTraceWorld(nav.agent.position, node, nav.world.getLines()) is None:
					farthest_index = i
			while index_s < farthest_index:
				nav.path.pop(0)
				index_s = index_s + 1  
	### YOUR CODE GOES ABOVE HERE ###
	return False

