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

from utils_navmesh import NavMeshUtils

# Creates a path node network that connects the midpoints of each nav mesh together
def myCreatePathNetwork(world, agent = None):	
	nodes = []
	edges = []
	polys = []

	# you don't strictly speaking need to use these. But we include in case they help you get started.
	obstacleLines = world.getLines()[4:] # the first four (i.e. 0-3) are the screen edges; this gets all but those
	worldLines = set(world.getLines())
	worldPoints = world.getPoints()
	worldObstacles = world.getObstacles()
	numPoints = len(worldPoints)
	lineDict = {}
	polySet = set() # Probably good for holding ManualObstacle instances

	# hint 0: to iterate over a collection, the `range` function is useful. E.g. `for i in range(numPoints):`
	#
	# hint 1: We can represent a triangle as a tuple of three worldPoints: triangle = (p1, p2, p3)
	#    Tuples in python are not limited to three elements
	#
	# hint 2: It may be useful to use the ManualObstacle class to help manage complexity. E.g. ManualObstacle(triangle)
	#    Because ManualObstacle is a Obstacle, you have helper methods like draw, getLines, getPoints, and pointInside
	#
	# hint 3: for debugging, it can also be useful to 'draw' centroids of hulls, e.g. NavMeshUtils.drawCentroids(world, polySet)

	### YOUR CODE GOES BELOW HERE ###

	# Any and all of these comments before "YOUR CODE GOES ABOVE HERE" can be deleted. They are meant to help, but may not.

	# Add all the obstacle edges to the edges list
	for oline in obstacleLines:
		edges.append(oline)

	# HW TODO: Create triangles that don't intersect with each other or obstacles.
		# You may need to make sure no obstacles are completely inside the triangle.
		# You may need to register the triangle's lines for later use (when merging).
	
	# This function is used to check the validity of the edge and thus one of the functions used to check the validity of triangle
	def check_endpoints(worldPoints, intersection, edge):
		a, b = edge
		# Check if the edge is not intersect with other edges
		if intersection is None:
			return True
		# Check if the edge is being considered as intersect because of it is already existed in the list
		elif ((a, b) in edges) or ((b, a) in edges):
			return True
		# If the edge does not follow the previous conditions, then the edge is not valid
		return False
	# This function is used to check if the triangle built is overlapped with the obstacles
	def check_obstacle_tri(triangle, obstacles):
		# extract triangle vertex
		a, b, c = triangle
		# Go through all the points in the world and check if there is a point inside the triangle (if so, it means the triangle is overlap with one of the obstacles)
		for point in worldPoints:
			if pointInsidePolygonPoints(point, [a, b, c]):
				if sorted([point[0], point[1]]) != sorted([a[0], a[1]]) and sorted([point[0], point[1]]) != sorted([b[0], b[1]]) and sorted([point[0], point[1]]) != sorted([c[0], c[1]]):
					return True	
		# Return False if no overlap
		return False
	# This function is to find a middle point 
	def midpoint(p1, p2):
		x1, y1 = p1
		x2, y2 = p2
		midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
		return midpoint
 	# This function is used to check if the triangle that is going to be created is completely inside an obstacle
	def check_obstacle_inside (triangle, obstacles):
		# Extract the vertex
		a, b, c = triangle
		# Find the middle point of the edge of trianlge
		# This is because endpoint of the edge/vertex is hard to check, since pointInsidePolygonPoints function also include the points on the edge of the shape
		# However, if the midpoint is in the obstacles, it means the edge must inside the obstacle
		mid_ab = midpoint(a, b)
		mid_ac = midpoint(a, c)
		mid_bc = midpoint(b, c)
		# If three edges all lie inside the obstacle, means the whole triangle is inside the obstacle, we dont want a triangle like this, thus return False
		for obstacle in obstacles:
			if pointInsidePolygonPoints(mid_ab, obstacle.getPoints()) and pointInsidePolygonPoints(mid_bc, obstacle.getPoints()) and pointInsidePolygonPoints(mid_ac, obstacle.getPoints()):
				return False
		# otherwise, return True
		return True

	flag = False
	# This part is used to go through each point in the game world and check for validity using functions defined above.
	for a in worldPoints:
		for b in worldPoints:
			for c in worldPoints:
				if (a, b, c) not in polys:
					intersection_1 = rayTraceWorldNoEndPoints(a, b, edges)
					intersection_2 = rayTraceWorldNoEndPoints(a, c, edges)
					intersection_3 = rayTraceWorldNoEndPoints(c, b, edges)
					if a!=b and b!= c and a!=c:
						if check_endpoints(worldPoints, intersection_1, (a, b)) and check_endpoints(worldPoints, intersection_2, (a, c)) and check_endpoints(worldPoints, intersection_3, (c, b)):
							triangle = tuple(sorted([a, b, c]))
							if not check_obstacle_tri(triangle, worldObstacles):
								if check_obstacle_inside(triangle, worldObstacles):
									#If all the checks passed, add the triangle to polys and edge to edges
									edges.append(tuple(sorted([a, b])))
									edges.append(tuple(sorted([a, c])))
									edges.append(tuple(sorted([c, b])))
									polys.append(triangle)
						
			

 	# Since there might be duplicates in polys and edges, remove it 
	def remove_duplicates(tuple_list):
		unique_tuples = list(set(tuple_list))
		return unique_tuples
	edges = remove_duplicates(edges)
	polys = remove_duplicates(polys)


	# HW TODO: Now merge triangles in a way that preserves convexity.

	# HW Hint: Now might be a good time to NavMeshUtils.drawCentroids(world, polySet)
	# NavMeshUtils.drawCentroids(world, polySet)
	# This function is to check for common verteices of two polygons
	def common_vertices(p1, p2):
		# Find the intersect of sets
		cv = tuple(set(p1)&set(p2))
		return cv
	# This function is used to merge two polygons (by finding the union of vertices of two polygons)
	# It returns a new polygon with vertices from the two polygons and remove the duplicates caused by the common vertices
	def merge_polys(p1, p2):
		new_polygon = []
		cv = common_vertices(p1, p2)
		for point in p1:
			if point not in cv:
				new_polygon.append(point)
		for point in p2:
			new_polygon.append(point)		
		return tuple(new_polygon)
	# This is used to sort the polygons so the points will orderd in a way in which the isConvex can check correctly 
	def sort_poly_points(poly):
		# get the centroid od polygon
		centroid = NavMeshUtils.getCentroid(poly)
		# function to for ordering
		def sort_func(poly):
			return math.atan2(poly[1] - centroid[1], poly[0] - centroid[0])
		sorted_poly = sorted(poly, key=sort_func)
		return tuple(sorted_poly)
	i = 0

	# Citation: Use ChatGPT
	# QUESTION:
	# def merge_polys(p1, p2):
	# 	new_polygon = []
	# 	cv = common_vertices(p1, p2)
	# 	for point in p1:
	# 		if point not in cv:
	# 			new_polygon.append(point)
	# 	for point in p2:
	# 		new_polygon.append(point)		
	# 	return tuple(new_polygon)
	# # This is used to sort the polygons so the points will orderd in a way in which the isConvex can check correctly 
	# def sort_poly_points(poly):
	# 	# get the centroid od polygon
	# 	centroid = NavMeshUtils.getCentroid(poly)
	# 	# function to for ordering
	# 	def sort_func(poly):
	# 		return math.atan2(poly[1] - centroid[1], poly[0] - centroid[0])
	# 	sorted_poly = sorted(poly, key=sort_func)
	# 	return tuple(sorted_poly)
	# based on these functions, how can I go through all the polygon in 
	# polys list and merge the triangles inside the polys. Remove the triangle merged and add the 
	# new_merged_polygon to the polys list.
	# ANSWER:
	#To go through all polygons in the polys list, merge the triangles, remove the merged triangles, and add the newly merged polygons back to the polys list, you can follow a strategy similar to the one discussed previously but with specific steps tailored to your functions merge_polys and sort_poly_points. The goal here is to iteratively merge polygons that share common vertices and are adjacent, ensuring that the merged polygon is convex before adding it to the list.

	# Here's how you can implement this process:

	# Iterate and Merge: Go through each pair of polygons in the polys list, checking for common vertices (indicating adjacency) and potential for merging.

	# Sort and Check Convexity: After merging, sort the points of the newly formed polygon to ensure they are ordered correctly for convexity checking.

	# Update List: If the merged polygon is convex, update the polys list by removing the original polygons and adding the newly merged polygon.

	# Here is a conceptual implementation:

	# python
	# Copy code
	# def attempt_merge_polys(polys):
	#     has_merged = True
	#     while has_merged:
	#         has_merged = False
	#         new_polys = []
	#         i = 0
	#         while i < len(polys):
	#             merged = False
	#             for j in range(i + 1, len(polys)):
	#                 common_v = common_vertices(polys[i], polys[j])
	#                 if common_v:  # Check if there are common vertices indicating potential for merging
	#                     new_poly = merge_polys(polys[i], polys[j])
	#                     new_poly = sort_poly_points(new_poly)
	#                     if isConvex(new_poly):  # Assuming isConvex function is available
	#                         new_polys.append(new_poly)  # Add merged polygon to the list
	#                         # Mark indices or polygons to be removed
	#                         polys.pop(j)
	#                         polys.pop(i)
	#                         merged = True
	#                         has_merged = True
	#                         break  # Exit the inner loop to restart with the updated list
	#             if not merged:
	#                 # If no merge happened for polys[i], move it to the new list
	#                 new_polys.append(polys[i])
	#             i += 1 if not merged else 0  # Reset i if merged, else increment
	#         polys[:] = new_polys  # Update polys list with the new list of polygons

	#     return polys
	# Key Points:

	# This implementation uses a while loop that continues as long as at least one merge occurs during an iteration over the list, ensuring all potential merges are explored.
	# The common_vertices function is used to identify polygons that share vertices and are therefore adjacent and potentially mergeable.
	# After merging, the sort_poly_points function is called to order the points of the newly formed polygon correctly for convexity checking.
	# The isConvex function checks if the newly formed polygon is convex. If it is, the merge is accepted, and the new polygon is added to the list.
	# The polys list is updated at the end of each iteration to reflect the merges that occurred, removing merged polygons and adding new ones.
	# This approach ensures that all polygons are considered for merging, and the list is dynamically updated to reflect merges as they occur, eventually resulting in a list of polygons where no further merges are possible.
	# NOTE the isConvex function is mentioned in previous question but I finally use this part of code as a reference
	# Also, I firstly tried out to go through all polys and check for Convex, but I did not realize the polys are chaning during the loop at the beginning, 
	# and this caused an outofbound error. I also thought about using a temp polys to store the new polys merged but finally found that using a flag 
	# to track this process is much simpler 


	# Track if the merges happened
	merged = True
	while merged:
		# First set it to false, since the merge has not happened during this round
		# If it is not changed to True in the end of the loop, means that no merges could happen,
		# then the process ends
		merged = False
		# iterator
		i = 0
		# go through all the polygons 
		while i < len(polys) - 1:
			for j in range(i + 1, len(polys)):
				poly1 = polys[i]
				poly2 = polys[j]
				# find common edges
				
				common_pts = common_vertices(poly1, poly2)
				# check if the two polygons is adjacent
				if polygonsAdjacent(poly1, poly2):  
					merged_poly = merge_polys(poly1, poly2)
					# sort the poly so isConves can check correcly
					merged_poly = sort_poly_points(merged_poly)
					if isConvex(merged_poly):
						# append mew polygon to the list
						polys.append(merged_poly)
						# remove the old triangles
						polys.remove(poly1)
						polys.remove(poly2)
						# Also remove the corresponding edges(the common edges)
						edges.remove(tuple(sorted([common_pts[0], common_pts[1]])))
						merged = True
						# There is no need for us to go through the rest of the list since we are doing from the start again, so break the loop to restart
						break
			# If merged this round, it means that the polys list changed and new polygons added in while the old ones being removed
			# So one way to make sure all the polygons in the list being engaged in merging is to break the loop and restart the 
			# mergin process from the beginning of polys list
			if merged:
				break
			# If no merge for this polygon, go to the next one
			i += 1
      





	# HW TODO: Create the final nav mesh and create cliques out of the boundaries of each polygon.
		# Decide how you will use the boundaries and centroid of the polygon as nodes.
		# For example, if the polygon has more than 3 sides, you may just send a line from each edge to the middle
		# Note: you can link borders directly in polygons or if the centroid is unusable.
			# NB: Don't try to link a border to itself!

	# We should only return nodes that the agent can reach on the path network.
	# Suggestion: consider using a BFS of sorts to get a connected graph.
	

	# This function is used to check if the line is one of the edge of obstacles in the gane world
	def is_obstacles_edge(p1, p2):
		if (p1, p2) in obstacleLines or (p2, p1) in obstacleLines:
				return True 
		return False
	# get through all the polygons 
	for poly in polys:
		# A list for storing midpoint
		midpoints = []
		# Go though each edge of polygon
		for i in range(len(poly)):
			# Find two adjaccent edges
			p1 = poly[i] 
			if i < len(poly) -1:
				p2 = poly[i+1]
			else:
				p2 = poly[0]
			# if the edge of the poly is also the edge of obstacles, skip the loop 
			if is_obstacles_edge(p1, p2):
				continue
			# Find midpoint of the edge and add to the nodes, also add to midpoint list for later use. 
			midp = midpoint(p1, p2)
			midpoints.append(midp)
			nodes.append(midp)
		# Check if the polygon has more than 3 edges
		if len(poly) > 3:
			# For polygons more than 3 edges, find the centroid
			centroid = NavMeshUtils.getCentroid(poly)  
			# add centroid as one of the nodes
			nodes.append(centroid)
			# add the edges (from centroid to other midpoind on the edges)
			for midp in midpoints:
				edges.append(tuple(sorted([midp, centroid])))
		else:
			# For polygons have 3 edges, connect the midpoint of two adjacent edges (use the midpoint of this polygon that stored in the list)
			for i in range(len(midpoints)):
				edges.append(tuple(sorted([midpoints[i], midpoints[(i + 1) % len(midpoints)]])))




	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys

