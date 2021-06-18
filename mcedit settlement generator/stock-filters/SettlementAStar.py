# A* Pathfinding implementation in Python 2.7
# Adopted from original script by Christian Careaga (christian.careaga7@gmail.com)
# Source: http://code.activestate.com/recipes/578919-python-a-pathfinding-with-binary-heap/
# Released under the MIT License: https://opensource.org/licenses/MIT

import numpy
from heapq import *


def heuristic(a, b, map):
	# penalize going up hills diagonally, even if the settings allow it
	if map.roads_can_cross_corners and map.corners[b[0],b[1]]:
		return 999
	else:
		return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (map.altitudes[a[0],a[1]] - map.altitudes[b[0],b[1]]) ** 2


def astar(array, start, goal, map):
	neighbors = [(0,1),(0,-1),(1,0),(-1,0)]

	close_set = set()
	came_from = {}
	gscore = {start:0}
	fscore = {start:heuristic(start, goal, map)}
	oheap = []

	heappush(oheap, (fscore[start], start))

	while oheap:

		current = heappop(oheap)[1]

		if current == goal:
			data = []
			while current in came_from:
				data.append(current)
				current = came_from[current]
			return data

		close_set.add(current)
		for i, j in neighbors:
			neighbor = current[0] + i, current[1] + j

			if 0 <= neighbor[0] < array.shape[0]:
				if 0 <= neighbor[1] < array.shape[1]:				
					if array[neighbor[0]][neighbor[1]] == 1:
						continue
				else:
					continue
			else:
				continue

			tentative_g_score = gscore[current] + heuristic(current, neighbor, map)
				
			if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
				continue
				
			if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
				came_from[neighbor] = current
				gscore[neighbor] = tentative_g_score
				fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal, map)
				heappush(oheap, (fscore[neighbor], neighbor))
				
	return False