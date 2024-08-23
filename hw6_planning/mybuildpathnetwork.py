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

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates the path network as a list of lines between all path nodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
	lines = []
	### YOUR CODE GOES BELOW HERE ###
	# get all the obstacles in the game world
	obstacles = world.getObstacles()
	# get the radius of agent
	agent_radius = agent.getMaxRadius()
	# go through all the pairs of pathnodes, connect them using line if not collide with obstacles
	for i in range(0, len(pathnodes)):
		for j in range(i+1, len(pathnodes)):
			# get one pair of node
			node_1 = pathnodes[i]
			node_2 = pathnodes[j]
			# connect two nodes using line
			path = (node_1, node_2)
			# flag for checking
			intersect = False
			# check if the edge of obstacles are intersect with the line, if intersect, the agent will collide with obstacles when move along this line
			# so connection/line between these two nodes should not be set
			for obstacle in obstacles:
				for obsLine in obstacle.getLines():
					# use rayTrace function to check the intersection
					if rayTrace(node_1, node_2, obsLine) != None:
						intersect = True
						break
			# if not intersect and the path is not too close to the obstacles, add this path to the return list
			if not intersect and checkPathFeasibility(path, obstacles, agent_radius, agent_radius/2):
				lines.append(path)
			

	### YOUR CODE GOES ABOVE HERE ###
	return lines

# Function to check if the path is too close to the eldge of the obstacles
# param: path -- the path that need to be checked, defined by two end points
# param: obstacles -- all the obstacles in the game
# param: agent_radius -- the maximum radius of the agent
# param: check_interval -- the distance between two points need to be check along the path (we cannot check all the points along a line, its infinity)

def checkPathFeasibility(path, obstacles, agent_radius, check_interval):
	# get the two end points of the line segment
	start_point = path[0]
	end_point = path[1]
	# calculate the distance to determine how many points have to be checked in total
	path_length = distance(start_point, end_point)
	# know the direction of the path
	direction = (end_point[0]-start_point[0], end_point[1]-start_point[1])
	# calculate number of points have to be checked based on the interval
	numOfCheckingPoints = int(path_length/check_interval)
	# check the distance between each point and the edge of obstacles
	for i in range (0, numOfCheckingPoints):
		x = start_point[0] + direction[0]*(i/numOfCheckingPoints)
		y = start_point[1] + direction[1]*(i/numOfCheckingPoints)
		checkPoint = (x, y)
		for obstacle in obstacles:
			for obsLine in obstacle.getLines():
				if minimumDistance(obsLine, checkPoint) < agent_radius:
					# return false if the distance is smaller than radius
					return False
	# return true if all the points along the path is not too close to the obstacles
	return True

