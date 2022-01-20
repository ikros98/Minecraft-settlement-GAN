import time
from math import sqrt, tan, sin, cos, pi, ceil, floor, acos, atan, asin, degrees, radians, log, atan2, acos, asin
from random import *
from numpy import *
from itertools import izip

from SettlementMap import Map, get_block, get_block_tuple
from SettlementStructure import Structure, Bridge
import SettlementAStar as pathfinding


class Generator:
	def __init__(self, level, box, options, map, materials, seed_number, start_time):
		self.level = level
		self.box = box
		self.options = options

		self.attempts = 0
		self.seed_number = seed_number
		seed(self.seed_number)

		self.map = map
		self.structures = []
		self.candidates = []
		self.candidate_selected = 0

		self.materials = materials

		#order of priorities when selecting locations for structures
		self.score_guide = {}

		# self.score_guide['house'] = ('access', 'elevation', 'layout', 'distance')
		# self.score_guide['plaza'] = ('access', 'elevation', 'layout', 'distance')
		# self.score_guide['farm'] = ('elevation', 'in front of road', 'distance')

		# self.score_guide['house'] = ('layout', 'elevation', 'access', 'distance')
		# self.score_guide['plaza'] = ('layout', 'elevation', 'access', 'distance')
		# self.score_guide['farm'] = ('in front of road', 'elevation', 'distance')

		self.score_guide['house'] = ('elevation', 'access', 'layout', 'distance')
		self.score_guide['plaza'] = ('elevation', 'access', 'layout', 'distance')
		self.score_guide['farm'] = ('elevation', 'in front of road', 'distance')

		# self.score_guide['bridge'] = ()
		# self.score_guide['bridge'] = ('access',)
		self.score_guide['bridge'] = ('access', 'distance')


	def add_sequence(self, sequence, max_attempts, road_connection_points, connect_to_existing_roads, start_time):
		seed(self.seed_number)

		for i in xrange(0, len(sequence)):
			structure_data = sequence[i]

			if i < len(sequence) - 1:
				next_structure_data = sequence[i+1]
			else:
				next_structure_data = None

			self.add_structure(structure_data, next_structure_data, max_attempts, road_connection_points, connect_to_existing_roads, start_time)


	def add_structure(self, structure_data, next_structure_data, max_attempts, road_connection_points, connect_to_existing_roads, start_time):
		map = self.map
		ws, hs, height, entry_distance, reserved_space, road_distance, cat, subcat = structure_data
		w, h = choice(ws), choice(hs)

		self.attempts += 1
		if subcat == '':
			print("\n  Trying to add a new structure (#%i) - %s..." % (self.attempts, cat))
		else:
			print("\n  Trying to add a new structure (#%i) - %s... (%s)" % (self.attempts, cat, subcat))

		self.candidates = []


		if len(self.structures) > 0:
			random_structure = choice(self.structures)
			start_x, start_y = random_structure.x1, random_structure.y1
		else:
			start_x, start_y = map.w/2, map.h/2


		if cat == 'bridge':
			sorted_positions = sorted(map.occupied_by_impassable, key=lambda position: map.get_distance(position[0], position[1], start_x, start_y))

			for x, y in sorted_positions:
				new_structures = [
									Bridge(self.map, self.structures, x, y, x+w, y+h, height, entry_distance, reserved_space, 's', cat, subcat, self.materials, start_time),
									Bridge(self.map, self.structures, x, y, x+h, y+w, height, entry_distance, reserved_space, 'w', cat, subcat, self.materials, start_time),
								]
				for structure in new_structures:
					if structure.acceptable():
						self.candidates.append({'structure': structure})
				if len(self.candidates) >= max_attempts:
					break

		else:
			sorted_positions = sorted(map.positions, key=lambda position: map.get_distance(position[0], position[1], start_x, start_y))

			for x, y in sorted_positions:
				new_structures = [
									Structure(self.map, self.structures, x, y, x+w, y+h, height, entry_distance, reserved_space, 's', cat, subcat, self.materials, start_time),
									Structure(self.map, self.structures, x, y, x+w, y+h, height, entry_distance, reserved_space, 'n', cat, subcat, self.materials, start_time),
									Structure(self.map, self.structures, x, y, x+h, y+w, height, entry_distance, reserved_space, 'w', cat, subcat, self.materials, start_time),
									Structure(self.map, self.structures, x, y, x+h, y+w, height, entry_distance, reserved_space, 'e', cat, subcat, self.materials, start_time),
								]
				for structure in new_structures:
					if structure.acceptable():
						self.candidates.append({'structure': structure})
				if len(self.candidates) >= max_attempts:
					break


		if self.candidates:
			print("  Found %i candidates..." % (len(self.candidates),))

			score_guide = self.score_guide[self.candidates[0]['structure'].cat]

			shuffle(self.candidates)
			top_candidate = self.get_top_score_decision_tree(self.candidates, score_guide)

			if len(self.structures) > 0 and cat != 'farm':
				top_candidate['distance_data'] = top_candidate['structure'].update_distance_data()

			self.generate_top_candidate(top_candidate, score_guide, road_distance, road_connection_points, connect_to_existing_roads)

		else:
			print(" -No acceptable area to generate structure found.")


		print("  Done (time elapsed: %i s)." % (time.time() - start_time))


	def get_top_score_decision_tree(self, candidates, score_guide):
		# print "\nstarting with %i candidates" % len(candidates)

		top_scores = {}

		for criterion in score_guide:
			if criterion == 'elevation':
				local_scoring_function = self.get_candidate_elevation_score
			elif criterion == 'layout':
				local_scoring_function = self.get_candidate_layout_score
			elif criterion == 'access':
				local_scoring_function = self.get_candidate_access_score
			elif criterion == 'distance':
				local_scoring_function = self.get_candidate_distance_score
			elif criterion == 'in front of road':
				local_scoring_function = self.get_candidate_in_front_of_road_score

			selected_candidates = []
			highest_score = -9999

			for candidate in candidates:
				local_score = local_scoring_function(candidate)
				if local_score > highest_score:
					highest_score = local_score
					selected_candidates = [candidate]
				elif local_score == highest_score:
					selected_candidates.append(candidate)

			top_scores[criterion] = highest_score

			# print "  %i selected using criterion %s" % (len(selected_candidates), criterion)

			candidates = selected_candidates

			if len(candidates) == 1:
				break


		# print ""

		top_candidate = selected_candidates[0]
		top_candidate['scores'] = top_scores
		return top_candidate


	def get_candidate_elevation_score(self, candidate):
		return candidate['structure'].get_elevation_score()

	def get_candidate_layout_score(self, candidate):
		return candidate['structure'].get_layout_score()

	def get_candidate_access_score(self, candidate):
		return candidate['structure'].get_access_score()

	def get_candidate_distance_score(self, candidate):
		return candidate['structure'].get_distance_score()

	def get_candidate_in_front_of_road_score(self, candidate):
		return candidate['structure'].get_in_front_of_road_score()


	def get_path(self, road_distance, target, entry_target, entry_source):
		#note: sometimes paths ascend up 2 or more squares when crossing hills/mountains
		path = pathfinding.astar(self.map.grid, entry_target, entry_source, self.map)
		return path


	def clearup_path_loops(self, full_path):
		earliest_start = -9999
		latest_finish = -9999
		iterated_points = set([])

		for i, point in enumerate(full_path):

			if point in iterated_points:
				start = full_path.index(point)
				finish = len(full_path) - 1 - full_path[::-1].index(point)

				if earliest_start == -9999 or (start <= earliest_start and finish >= latest_finish):
					earliest_start = start
					latest_finish = finish

			iterated_points.add(point)

		if earliest_start != -9999:
			new_full_path = full_path[:earliest_start] + full_path[latest_finish:]
		else:
			new_full_path = full_path

		return new_full_path


	def clearup_path(self, path):
		map = self.map

		new_path = []
		previous_connected = False

		for i, point in enumerate(path):
			connected = False

			for xd, yd in ((0,0), (-1,0), (1,0), (0,-1), (0,1)):
				if (point[0]+xd, point[1]+yd) in self.map.occupied_by_road:
					connected = True
					break

			if connected:
				new_path.append(point)
				break

			else:
				if not previous_connected:
					new_path.append(point)

			previous_connected = connected

		return new_path


	def get_considered_entry_points(self, map, structure, pointA, all_from_plaza):
		if structure.cat == 'bridge':
			if structure.direction in "sn":
				structure_entry_points = [(structure.center_x,structure.y1-1), (structure.center_x,structure.y2)]
			else:
				structure_entry_points = [(structure.x1-1,structure.center_y), (structure.x2,structure.center_y)]
		else:
			structure_entry_points = structure.get_other_entry_points()
			structure_entry_points.append(structure.get_entry_point())

		if structure.cat == 'plaza' and not all_from_plaza:
			considered_entry_points = []

			shortest_entry_distance = (map.w + map.h)
			nearest_entry_point = None

			for structure_point in structure_entry_points:
				topdown_distance = self.map.get_distance(pointA[0], pointA[1], structure_point[0], structure_point[1])
				altitude_difference = abs(self.map.altitudes[pointA[0],pointA[1]] - self.map.altitudes[structure_point[0],structure_point[1]])
				point_distance = topdown_distance * (1 + altitude_difference)

				if point_distance < shortest_entry_distance:
					shortest_entry_distance = point_distance
					nearest_entry_point = structure_point

			if nearest_entry_point != None:
				return [nearest_entry_point]

			return []

		else:
			return structure_entry_points


	def get_line(self, x1, y1, x2, y2):
		#Bresenham's Line Algorithm adapted from roguebasin.com wiki

		#setup initial conditions
		dx = x2 - x1
		dy = y2 - y1

		#determine how steep the line is
		is_steep = abs(dy) > abs(dx)

		#rotate line
		if is_steep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2

		#swap start and end points if necessary and store swap state
		swapped = False
		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1
			swapped = True

		#recalculate differentials
		dx = x2 - x1
		dy = y2 - y1

		#calculate error
		error = int(dx / 2.0)
		ystep = 1 if y1 < y2 else -1
	 
		#iterate over bounding box generating points between start and end
		y = y1
		points = []
		for x in range(x1, x2 + 1):
			coord = (y, x) if is_steep else (x, y)
			points.append(coord)
			error -= abs(dy)
			if error < 0:
				y += ystep
				error += dx

		#reverse the list if the coordinates were swapped
		if swapped:
			points.reverse()

		return points


	def paths_pass_building_from_different_sides(self, pathA, pathB):
		#approximate whether there is a building in between the two paths
		#(checks for building collisions along the lines running between 10 equivalent points of either path)

		if not pathA or not pathB:
			return True

		selected_points_A = []
		selected_points_B = []

		for i in xrange(10):
			point_A = min(len(pathA)-1, int(round( (float(i)/10.) * float(len(pathA)) )))
			selected_points_A.append(pathA[point_A])
			point_B = min(len(pathB)-1, int(round( (float(i)/10.) * float(len(pathB)) )))
			selected_points_B.append(pathB[point_B])

		for i in xrange(10):
			x1, y1 = selected_points_A[i]
			x2, y2 = selected_points_B[i]

			line = self.get_line(x1, y1, x2, y2)

			#adding another road around plazas may be a bad idea? (reduced space for buildings around it?)

			for x, y in line:
				if (x,y) in self.map.occupied_by_building or (x,y) in self.map.occupied_by_farm:
					return True

		return False


	def add_roads(self, map, target, road_distance, road_connection_points, connect_to_existing_roads):
		print("  Trying to generate road...")

		#get nearest sources (limit to X last generated structures + always include last selected point for expansion (random_structure)? or use this as an optional setting?)

		nearest_sources = []

		if target.cat == "bridge":
			if target.direction in "sn":
				entry_points = [(target.center_x,target.y1-1), (target.center_x,target.y2)]
			else:
				entry_points = [(target.x1-1,target.center_y), (target.x2,target.center_y)]
		else:
			entry_points = [target.get_entry_point()]

		for pointA in entry_points:
			for structure in self.structures:
				if structure != target and structure.cat != 'farm':

					considered_entry_points = self.get_considered_entry_points(map, structure, pointA, False)

					for structure_point in considered_entry_points:
						topdown_distance = self.map.get_distance(pointA[0], pointA[1], structure_point[0], structure_point[1])
						altitude_difference = abs(self.map.altitudes[pointA[0],pointA[1]] - self.map.altitudes[structure_point[0],structure_point[1]])

						point_distance = topdown_distance * (1 + altitude_difference)
						distance_data = (point_distance, pointA, structure_point, structure)
						nearest_sources.append(distance_data)


		#sort nearest sources by distance

		nearest_sources.sort(key = lambda source_candidate: source_candidate[0])

		if road_connection_points != - 1:
			nearest_sources = nearest_sources[:road_connection_points]


		#generate paths

		paths_to_generate = []

		for distance_data in nearest_sources:
			shortest_point_distance, entry_target, entry_source, source = distance_data
			path = self.get_path(road_distance, target, entry_target, entry_source)

			# print "(  %s ---> %s)" % (entry_target, entry_source)

			if path:
				print(" :Found path (length: %i)" % (len(path)))

				target_entry_path = target.get_entry_path(entry_target)[:-1]
				source_entry_path = source.get_entry_path(entry_source)[:-1]

				target_entry_points = set(target_entry_path)

				full_path = source_entry_path[::-1] + path + target_entry_path

				if connect_to_existing_roads:
					full_path = self.clearup_path(full_path[::-1])[::-1]
					full_path = self.clearup_path_loops(full_path)

				path_data = (False, full_path, target_entry_points, entry_target, entry_source, target, source)
				paths_to_generate.append(path_data)

			else:
				if entry_target == entry_source:
					print(" :Entry points align without a need for path.")					
					paths_to_generate.append((True, [], [], entry_target, entry_source, target, source))

				else:
					print(" -No path found.")


		#filtering branching paths

		paths_to_generate.sort(key=lambda path_data: len(path_data[1]))


		#filter paths - only generate another path if it surrounds one of the existing buildings from the opposite side to previous path

		filtered_paths = []

		if len(paths_to_generate) < 2:
			filtered_paths = paths_to_generate
		else:
			for path_data in paths_to_generate:

				if path_data[0]:
					filtered_paths.append(path_data)
					break

				elif not filtered_paths:
					filtered_paths.append(path_data)

				else:
					#ignore for bridges
					if path_data[5].cat == 'bridge' or path_data[6].cat == 'bridge':
						filtered_paths.append(path_data)

					else:
						reference_path = filtered_paths[-1][1]
						evaluated_path = path_data[1]

						building_in_between = self.paths_pass_building_from_different_sides(reference_path, evaluated_path)

						if building_in_between:
							filtered_paths.append(path_data)


		paths_to_generate = filtered_paths


		#generating

		for short_path, full_path, target_entry_points, entry_target, entry_source, _target, _source in paths_to_generate:
			if not short_path:
				for i, point in enumerate(full_path):
					x, y = point

					map.fill_block_relative_to_surface(point[0], point[1], 0, self.materials['road'])
					map.clear_space_relative_to_surface(point[0], point[1], 1)

					map.occupied_by_road.add(point)
					map.occupied_by_any.add(point)

			elif short_path:
				target_entry_path = target.get_entry_path(entry_target)[:-1]
				source_entry_path = source.get_entry_path(entry_source)[:-1]

				map.complete_path(target_entry_path, self.materials['road'])
				map.complete_path(source_entry_path, self.materials['road'])


	def generate_top_candidate(self, top_candidate, score_guide, road_distance, road_connection_points, connect_to_existing_roads):
		map = self.map

		top_candidate['structure'].generate()
		self.structures.append(top_candidate['structure'])

		#update grid

		map.update_grid_for_structure(top_candidate['structure'], road_distance)


		#display scores

		print("  Winning scores:\n")
		top_keys = set(top_candidate['scores'].keys())
		for label in score_guide:
			if label in top_keys:
				print("    %-30s %.2f" % (label, top_candidate['scores'][label]))
			else:
				print("    %-30s %s" % (label, "---"))
		print("")


		#add new roads

		if top_candidate['structure'].has_distance_data:
			self.add_roads(map, top_candidate['structure'], road_distance, road_connection_points, connect_to_existing_roads)
